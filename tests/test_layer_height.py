"""Tests for variable layer height (orca123d.layer_heights + Project wiring)."""

from __future__ import annotations

import zipfile

import pytest
from build123d import Axis, Box, GeomType, Pos, fillet

from orca123d import Project

PROFILE_PATH = "Metadata/layer_heights_profile.txt"


def read_profiles(out) -> dict[int, list[tuple[float, float]]]:
  """Parse layer_heights_profile.txt into {object_id: [(z, h), ...]}, or {}."""
  with zipfile.ZipFile(out) as z:
    if PROFILE_PATH not in z.namelist():
      return {}
    text = z.read(PROFILE_PATH).decode()
  out_map: dict[int, list[tuple[float, float]]] = {}
  for line in text.splitlines():
    head, _, body = line.partition("|")
    object_id = int(head.split("=")[1])
    nums = [float(v) for v in body.split(";")]
    out_map[object_id] = list(zip(nums[0::2], nums[1::2]))
  return out_map


# --------------------------------------------------------------------------- #
# Low-level set_layer_height_profile + file format
# --------------------------------------------------------------------------- #
def test_low_level_profile_roundtrips(tmp_path):
  proj = Project()
  obj = proj.add_object(Box(20, 20, 10), name="Base")
  obj.set_layer_height_profile([(0.0, 0.2), (5.0, 0.2), (10.0, 0.1)])

  profiles = read_profiles(proj.save(tmp_path / "p.3mf"))

  assert profiles == {1: [(0.0, 0.2), (5.0, 0.2), (10.0, 0.1)]}


def test_no_profile_means_no_file(tmp_path):
  proj = Project()
  proj.add_object(Box(20, 20, 10), name="Base")
  assert read_profiles(proj.save(tmp_path / "p.3mf")) == {}


def test_profile_indexed_by_build_ordinal_not_mesh_id(tmp_path):
  # First object has two parts, so the second object's mesh/components ids are
  # well above 2; the profile file must still key it as object_id=2 (its ordinal).
  proj = Project()
  multi = proj.add_object(name="Multi")
  multi.add_part(Box(10, 10, 10), name="a")
  multi.add_part(Pos(20, 0, 0) * Box(10, 10, 10), name="b")
  second = proj.add_object(Pos(0, 20, 0) * Box(10, 10, 10), name="Second")
  second.set_layer_height_profile([(0.0, 0.2), (10.0, 0.1)])

  profiles = read_profiles(proj.save(tmp_path / "p.3mf"))

  assert list(profiles) == [2]  # ordinal of the 2nd object, not its mesh id (>=4)


@pytest.mark.parametrize(
  "points, match",
  [
    ([(0.0, 0.2)], "at least 2"),
    ([(1.0, 0.2), (5.0, 0.2)], "z=0"),
    ([(0.0, 0.2), (5.0, 0.2), (3.0, 0.2)], "non-decreasing"),
    ([(0.0, 0.2), (5.0, 0.0)], "positive"),
  ],
)
def test_set_profile_validation(points, match):
  obj = Project().add_object(Box(10, 10, 10), name="o")
  with pytest.raises(ValueError, match=match):
    obj.set_layer_height_profile(points)


# --------------------------------------------------------------------------- #
# optimize_layer_height (taper base -> min over the selected faces' z-span)
# --------------------------------------------------------------------------- #
def _filleted_block():
  # 20 tall; the top fillet (radius 6) faces span z 14..20.
  block = Box(30, 30, 20)
  return fillet(block.edges().group_by(Axis.Z)[-1], radius=6)


def _fillet_faces(block):
  return block.faces().filter_by(GeomType.PLANE, reverse=True)


def test_optimize_tapers_band_to_min():
  block = _filleted_block()
  obj = Project().add_object(block, name="o")
  obj.optimize_layer_height(_fillet_faces(block), base_height=0.24, min_layer_height=0.10)
  profile = obj.layer_height_profile

  zs = [z for z, _ in profile]
  assert profile[0] == (0.0, 0.24)  # starts at the object bottom, base height
  assert zs == sorted(zs)  # z non-decreasing
  assert any(h == pytest.approx(0.10) for _, h in profile)  # band reaches min
  # Below the fillet band (z < 14) everything is still at base.
  assert all(h == pytest.approx(0.24) for z, h in profile if z < 13.5)
  # The very top (inside the band, which here reaches the top) is the fine height.
  assert profile[-1][1] == pytest.approx(0.10)


def test_optimize_change_is_step_limited():
  block = _filleted_block()
  obj = Project().add_object(block, name="o")
  obj.optimize_layer_height(
    _fillet_faces(block), base_height=0.24, min_layer_height=0.10, max_change=0.04
  )
  profile = obj.layer_height_profile
  steps = [abs(profile[i + 1][1] - profile[i][1]) for i in range(len(profile) - 1)]
  assert max(steps) <= 0.04 + 1e-9


def test_optimize_writes_valid_file(tmp_path):
  block = _filleted_block()
  proj = Project()
  obj = proj.add_object(block, name="o")
  obj.optimize_layer_height(_fillet_faces(block), base_height=0.2, min_layer_height=0.08)

  profiles = read_profiles(proj.save(tmp_path / "p.3mf"))

  assert list(profiles) == [1]
  flat = [v for point in profiles[1] for v in point]
  assert len(flat) >= 4 and len(flat) % 2 == 0  # importer's validity rule
  assert flat[0] == 0.0
