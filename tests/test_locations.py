"""Tests for print/assembly locations (project + model_xml + model_settings)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile

from build123d import Box, Pos, Rot

from orca123d import Project

IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"
CORE_NS = {"c": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}


def _read(out):
  with zipfile.ZipFile(out) as z:
    return (
      z.read("3D/3dmodel.model").decode(),
      z.read("Metadata/model_settings.config").decode(),
    )


def _build_items(model_xml: str) -> dict[str, str]:
  """Map each build ``<item>`` objectid -> its transform string."""
  root = ET.fromstring(model_xml)
  return {
    item.get("objectid"): item.get("transform")
    for item in root.findall(".//c:build/c:item", CORE_NS)
  }


def test_no_print_location_emits_identity_and_no_assemble(tmp_path):
  proj = Project()
  proj.add_object(Box(20, 20, 10), name="A")
  model, cfg = _read(proj.save(tmp_path / "a.3mf"))

  assert list(_build_items(model).values()) == [IDENTITY]
  # No object is placed for print, so no Assembly-View override is written.
  assert ET.fromstring(cfg).find("assemble") is None


def test_print_location_sets_build_item_translation(tmp_path):
  proj = Project()
  proj.add_object(Box(10, 10, 10), name="B", print_location=Pos(60, -5, 0))
  model, _ = _read(proj.save(tmp_path / "b.3mf"))

  (transform,) = _build_items(model).values()
  nums = [float(x) for x in transform.split()]
  assert nums[:9] == [1, 0, 0, 0, 1, 0, 0, 0, 1]  # identity rotation
  assert nums[9:] == [60.0, -5.0, 0.0]  # translation in the last three slots


def test_print_location_rotation_is_column_major(tmp_path):
  proj = Project()
  proj.add_object(Box(10, 10, 10), name="C", print_location=Rot(0, 0, 90))
  model, _ = _read(proj.save(tmp_path / "c.3mf"))

  (transform,) = _build_items(model).values()
  nums = [round(float(x), 6) for x in transform.split()]
  # 90deg about Z, column-major 3x3: col0=[0,1,0], col1=[-1,0,0], col2=[0,0,1].
  assert nums[:9] == [0, 1, 0, -1, 0, 0, 0, 0, 1]


def test_print_location_pins_all_objects_to_design(tmp_path):
  # When any object is placed for print, *every* object is pinned to its design
  # coordinates with an assemble transform -- otherwise an unplaced object would
  # inherit its group-centered/bed-dropped print transform and not line up with
  # the placed ones in the Assembly View. Both boxes here are centered at the
  # design origin, so each assemble transform is the identity (zero translation).
  proj = Project()
  proj.add_object(Box(20, 20, 10), name="A")  # not placed for print
  proj.add_object(Box(10, 10, 10), name="B", print_location=Pos(60, 0, 0))
  model, cfg = _read(proj.save(tmp_path / "ab.3mf"))

  assemble = ET.fromstring(cfg).find("assemble")
  assert assemble is not None
  entries = assemble.findall("assemble_item")
  assert len(entries) == 2  # both objects pinned to design coords

  for entry in entries:
    nums = [round(float(x), 6) for x in entry.get("transform").split()]
    assert nums == [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]  # identity (origin-centered)
    assert entry.get("offset") == "0 0 0"
    assert entry.get("instance_id") == "0"
  # Every build <item> objectid is covered by an assemble_item.
  assert {e.get("object_id") for e in entries} == set(_build_items(model))


def test_assemble_transform_restores_off_origin_design_center(tmp_path):
  # OrcaSlicer re-centers each imported mesh on its own bounding-box center, so an
  # object whose design center is off the origin needs that center as its assemble
  # translation (an identity transform would drop it to the origin). Mirrors the
  # print_layout example: a lid seated at z=6.5 but printed off to the side.
  proj = Project()
  proj.add_object(Box(40, 40, 10), name="Base")  # design center (0, 0, 0)
  proj.add_object(
    Pos(0, 0, 6.5) * Box(40, 40, 3),  # design center (0, 0, 6.5)
    name="Lid",
    print_location=Pos(50, 0, 0),
  )
  _, cfg = _read(proj.save(tmp_path / "lid.3mf"))

  entries = ET.fromstring(cfg).findall("assemble/assemble_item")
  trans = {e.get("object_id"): [round(float(x), 6) for x in e.get("transform").split()]
           for e in entries}
  # object_id is allocated after each object's parts: Base part=1/object=2,
  # Lid part=3/object=4.
  assert trans["2"] == [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
  assert trans["4"] == [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 6.5]  # seated, not dropped


def test_to_compound_print_layout_centers_and_spreads():
  proj = Project()
  proj.add_object(Box(10, 10, 10), name="A")  # at design origin
  proj.add_object(Box(10, 10, 10), name="B", print_location=Pos(100, 0, 0))

  asm = proj.to_compound(layout="assembly")
  prt = proj.to_compound(layout="print")

  # Assembly keeps design coords (both boxes overlap at the origin).
  assert asm.bounding_box().size.X == 10
  # Print spreads B out, then group-centers in XY.
  assert abs(prt.bounding_box().center().X) < 1e-6
  assert prt.bounding_box().size.X > asm.bounding_box().size.X
