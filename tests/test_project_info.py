"""Tests for ProjectInfo -> <model> metadata in 3dmodel.model."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile

from build123d import Box

from orca123d import License, Project, ProjectInfo

CORE_NS = {"c": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}


def _metadata(out) -> dict[str, str]:
  """Map each <model> <metadata> name -> text for a saved .3mf."""
  with zipfile.ZipFile(out) as z:
    root = ET.fromstring(z.read("3D/3dmodel.model").decode())
  return {
    m.get("name"): (m.text or "")
    for m in root.findall("c:metadata", CORE_NS)
  }


def _save(tmp_path, info: ProjectInfo | None) -> dict[str, str]:
  proj = Project(info=info)
  proj.add_object(Box(10, 10, 10), name="A")
  return _metadata(proj.save(tmp_path / "p.3mf"))


def test_no_info_writes_only_boilerplate(tmp_path):
  meta = _save(tmp_path, None)
  assert set(meta) == {"Application", "BambuStudio:3mfVersion"}


def test_fields_map_to_3mf_metadata_names(tmp_path):
  info = ProjectInfo(
    title="Widget",
    designer="Jas",
    description="A tidy little widget",
    copyright="(c) 2026 Jas",
    license=License.CC_BY_SA,
  )
  meta = _save(tmp_path, info)
  assert meta["Title"] == "Widget"
  assert meta["Designer"] == "Jas"
  assert meta["Description"] == "A tidy little widget"
  assert meta["Copyright"] == "(c) 2026 Jas"
  # Enum serializes to OrcaSlicer's bare license code.
  assert meta["License"] == "BY-SA"


def test_license_accepts_raw_string(tmp_path):
  meta = _save(tmp_path, ProjectInfo(license="BY-NC"))
  assert meta["License"] == "BY-NC"


def test_unset_fields_are_omitted(tmp_path):
  meta = _save(tmp_path, ProjectInfo(title="Only title"))
  assert meta["Title"] == "Only title"
  assert "Designer" not in meta
  assert "License" not in meta


def test_extra_keys_pass_through_verbatim(tmp_path):
  info = ProjectInfo(title="X", **{"Origin": "MakerWorld"})
  meta = _save(tmp_path, info)
  assert meta["Title"] == "X"
  assert meta["Origin"] == "MakerWorld"


def test_values_are_xml_escaped(tmp_path):
  # Raw &, <, > in user text must not corrupt the XML.
  info = ProjectInfo(description='A & B < C > "D"', title="Tom & Jerry")
  meta = _save(tmp_path, info)
  assert meta["Description"] == 'A & B < C > "D"'
  assert meta["Title"] == "Tom & Jerry"
