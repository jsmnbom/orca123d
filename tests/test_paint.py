"""Tests for triangle seam painting (orca123d.paint + Project wiring)."""

from __future__ import annotations

import re
import zipfile
from collections import Counter
from pathlib import Path

import pytest
from build123d import Axis, Box, BuildSketch, Circle, Cylinder, GeomType, Pos

from orca123d import Project
from orca123d.mesh import tessellate_shape
from orca123d.paint import (
  EnforcerBlockerType,
  decode,
  encode_region_paint,
  encode_tree,
  subdivide_classify,
)

NONE = EnforcerBlockerType.NONE
ENFORCER = EnforcerBlockerType.ENFORCER
BLOCKER = EnforcerBlockerType.BLOCKER


def faces_touched(mesh, painted) -> set[int]:
  """Which source-face indices the painted triangles belong to."""
  hit: set[int] = set()
  for tri in painted:
    for fi, (start, end) in enumerate(mesh.face_ranges):
      if start <= tri < end:
        hit.add(fi)
  return hit


REPO_ROOT = Path(__file__).resolve().parents[1]


def leaf_counts(hexstr: str) -> Counter[int]:
  """Decode a paint string and count how many leaves carry each state."""
  counts: Counter[int] = Counter()

  def walk(tree: object) -> None:
    if isinstance(tree, int):
      counts[tree] += 1
    else:
      for child in tree:  # type: ignore[union-attr]
        walk(child)

  walk(decode(hexstr))
  return counts


# --------------------------------------------------------------------------- #
# Encoding
# --------------------------------------------------------------------------- #
def test_leaf_nibbles_match_orcaslicer():
  # NONE -> "0", ENFORCER -> "4", BLOCKER -> "8" (see TriangleSelector serialize).
  assert encode_tree(NONE) == "0"
  assert encode_tree(ENFORCER) == "4"
  assert encode_tree(BLOCKER) == "8"


@pytest.mark.parametrize(
  "tree",
  [
    NONE,
    ENFORCER,
    BLOCKER,
    5,  # color extruder -> extended (>=3) nibble form
    (ENFORCER, NONE, BLOCKER, NONE),
    (ENFORCER, (BLOCKER, NONE, ENFORCER, NONE), NONE, ENFORCER),
  ],
)
def test_encode_decode_roundtrip(tree):
  assert decode(encode_tree(tree)) == tree


# --------------------------------------------------------------------------- #
# Region -> paint
# --------------------------------------------------------------------------- #
def test_whole_face_paints_solid_leaves():
  box = Box(20, 20, 10)
  mesh = tessellate_shape(box)
  face = box.faces().sort_by(Axis.X)[0]

  painted = encode_region_paint(mesh, box.faces(), face, ENFORCER, max_depth=5)

  # A flat face tessellates to two triangles; both are fully enforced (no split).
  assert len(painted) == 2
  assert all(s == "4" for s in painted.values())


def test_curved_part_face_painted_whole():
  # A curved face that *is* a face of the part is matched by identity and painted
  # whole -- no plane/stencil needed. (Previously raised "must be planar".)
  cyl = Cylinder(radius=5, height=10)
  mesh = tessellate_shape(cyl)
  lateral = next(f for f in cyl.faces() if f.geom_type == GeomType.CYLINDER)

  painted = encode_region_paint(mesh, cyl.faces(), lateral, ENFORCER, max_depth=5)

  fr_start, fr_end = mesh.face_ranges[list(cyl.faces()).index(lateral)]
  assert fr_end - fr_start > 2  # the curved wall tessellates to many triangles
  assert set(painted) == set(range(fr_start, fr_end))
  assert all(s == "4" for s in painted.values())  # whole leaves, no subdivision


def test_non_part_curved_face_falls_back_to_stencil():
  # A curved face that is NOT one of the part's faces can't be matched by
  # identity, so it falls through to the planar stencil path -- which rejects it.
  cyl = Cylinder(radius=5, height=10)
  mesh = tessellate_shape(cyl)
  stranger = next(f for f in Cylinder(3, 4).faces() if f.geom_type == GeomType.CYLINDER)

  with pytest.raises(ValueError, match="must be planar"):
    encode_region_paint(mesh, cyl.faces(), stranger, ENFORCER, max_depth=5)


def test_sketch_region_subdivides_and_mixes_states():
  box = Box(20, 20, 10)
  mesh = tessellate_shape(box)
  face = box.faces().sort_by(Axis.X)[0]
  with BuildSketch(face) as sk:
    Circle(4)  # covers the middle of the 20x10 face

  painted = encode_region_paint(mesh, box.faces(), sk.sketch, BLOCKER, max_depth=4)

  assert painted, "circle should cover part of the face"
  for hexstr in painted.values():
    counts = leaf_counts(hexstr)
    # A boundary triangle must contain both painted (BLOCKER) and empty leaves.
    assert counts[BLOCKER] > 0
    assert counts[NONE] > 0
    assert set(counts) <= {NONE, BLOCKER}


def test_thin_band_not_missed_by_cull():
  # A thin region crossing a large triangle must survive the bounding-box cull
  # (the old point-sampling reject discarded bands that fell between samples).
  p0, p1, p2 = (0.0, 0.0, 0.0), (20.0, 0.0, 0.0), (0.0, 20.0, 0.0)
  aabb = ((5.0, -1.0, -1.0), (5.4, 21.0, 1.0))

  def inside(p):
    return 5.0 <= p[0] <= 5.4

  tree = subdivide_classify(p0, p1, p2, inside, ENFORCER, 6, aabb)
  assert tree is not None
  counts = Counter()

  def walk(t):
    if isinstance(t, int):
      counts[t] += 1
    else:
      for child in t:
        walk(child)

  walk(tree)
  assert counts[ENFORCER] > 0


def test_edge_region_paints_strip_on_both_faces():
  box = Box(20, 20, 10)
  mesh = tessellate_shape(box)
  edge = next(e for e in box.edges() if abs(e.length - 10) < 1e-6)  # a vertical edge

  painted = encode_region_paint(
    mesh, box.faces(), edge, ENFORCER, max_depth=5, within=2.0
  )

  assert painted
  # The edge is shared by two faces; both should receive paint.
  assert len(faces_touched(mesh, painted)) >= 2
  for hexstr in painted.values():
    assert set(leaf_counts(hexstr)) <= {NONE, ENFORCER}


def test_solid_region_spans_multiple_faces():
  box = Box(20, 20, 10)
  mesh = tessellate_shape(box)
  # Vertical cylinder on the +X/+Y corner edge (at x=10, y=10).
  tool = Pos(10, 10, 0) * Cylinder(radius=5, height=24)

  painted = encode_region_paint(mesh, box.faces(), tool, ENFORCER, max_depth=4)

  assert painted
  assert len(faces_touched(mesh, painted)) >= 2


def test_paint_off_plane_faces_untouched():
  box = Box(20, 20, 10)
  mesh = tessellate_shape(box)
  face = box.faces().sort_by(Axis.X)[0]

  painted = encode_region_paint(mesh, box.faces(), face, ENFORCER, max_depth=5)

  # Only the two triangles of the targeted face are painted, nothing else.
  painted_tris = set(painted)
  fr_start, fr_end = mesh.face_ranges[list(box.faces()).index(face)]
  assert painted_tris == set(range(fr_start, fr_end))


# --------------------------------------------------------------------------- #
# Project wiring / file output
# --------------------------------------------------------------------------- #
def test_save_emits_paint_seam_attribute(tmp_path):
  proj = Project()
  box = Box(20, 20, 10)
  obj = proj.add_object(box, name="Base")
  part = obj.parts[0]
  part.paint_seam(box.faces().sort_by(Axis.X)[0], mode=ENFORCER)

  out = proj.save(tmp_path / "seam.3mf")
  with zipfile.ZipFile(out) as z:
    model = z.read("3D/3dmodel.model").decode()

  seams = re.findall(r'paint_seam="([0-9A-F]+)"', model)
  assert len(seams) == 2
  assert all(s == "4" for s in seams)


def test_block_mode_uses_blocker_state(tmp_path):
  proj = Project()
  box = Box(20, 20, 10)
  obj = proj.add_object(box, name="Base")
  obj.parts[0].paint_seam(box.faces().sort_by(Axis.X)[0], mode=BLOCKER)

  out = proj.save(tmp_path / "seam.3mf")
  with zipfile.ZipFile(out) as z:
    model = z.read("3D/3dmodel.model").decode()

  seams = re.findall(r'paint_seam="([0-9A-F]+)"', model)
  assert seams and all(s == "8" for s in seams)


# --------------------------------------------------------------------------- #
# Regression against a real OrcaSlicer-painted file
# --------------------------------------------------------------------------- #
def test_real_orcaslicer_seam_decodes_to_enforcer_only():
  model_path = REPO_ROOT / "out2" / "3D" / "Objects" / "Base_1.model"
  if not model_path.exists():
    pytest.skip("reference Base_1.model not present")

  strings = re.findall(r'paint_seam="([0-9A-F]+)"', model_path.read_text())
  assert strings, "expected painted triangles in the reference model"
  for hexstr in strings:
    states = set(leaf_counts(hexstr))
    # The reference file was painted with the "Enforce seam" tool only.
    assert states <= {NONE, ENFORCER}
