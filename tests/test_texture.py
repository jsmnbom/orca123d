"""Tests for surface texturing (orca123d.texture + Part.apply_texture wiring)."""

from __future__ import annotations

import zipfile

import numpy as np
import pytest
import trimesh
from build123d import Axis, Box, Sphere, fillet

from orca123d import EnforcerBlockerType, ProjectionMode, Project
from orca123d.mesh import tessellate_shape
from orca123d.texture import texturize_mesh

MODEL_PATH = "3D/3dmodel.model"


def _bbox(mesh) -> np.ndarray:
  """Return the (3,) bounding-box size of a MeshData."""
  v = np.asarray(mesh.vertices)
  return v.max(axis=0) - v.min(axis=0)


def _trimesh(mesh) -> trimesh.Trimesh:
  return trimesh.Trimesh(
    np.asarray(mesh.vertices), np.asarray(mesh.triangles), process=False
  )


# --------------------------------------------------------------------------- #
# Displacement: grayscale -> signed motion along the normal
# --------------------------------------------------------------------------- #
def test_midgray_is_neutral():
  mesh = tessellate_shape(Box(20, 20, 10))
  out = texturize_mesh(mesh, np.full((4, 4), 0.5), amplitude=1.0, scale=6.0)
  # Mid-gray displaces nothing, so the bounding box is unchanged.
  assert _bbox(out) == pytest.approx([20.0, 20.0, 10.0], abs=1e-6)


def _face_center_x(mesh) -> float:
  """X of the vertex nearest the centre of the +X face (a flat-face sample)."""
  v = np.asarray(mesh.vertices)
  return float(v[np.argmin(np.linalg.norm(v - [10.0, 0.0, 0.0], axis=1))][0])


def test_white_pushes_out_black_pushes_in():
  mesh = tessellate_shape(Box(20, 20, 10))  # origin-centred: +X face at x=10
  white = texturize_mesh(
    mesh, np.ones((4, 4)), amplitude=0.5, scale=6.0, keep_bottom=False
  )
  black = texturize_mesh(
    mesh, np.zeros((4, 4)), amplitude=0.5, scale=6.0, keep_bottom=False
  )
  # On a flat face the displacement is exactly +/-amplitude along the axis.
  assert _face_center_x(white) == pytest.approx(10.5, abs=1e-3)
  assert _face_center_x(black) == pytest.approx(9.5, abs=1e-3)
  # White grows the whole box by 2*amplitude per axis (face centres dominate).
  assert _bbox(white) == pytest.approx([21.0, 21.0, 11.0], abs=1e-3)


# --------------------------------------------------------------------------- #
# Subdivision: finer mesh, bounded edge length, still watertight
# --------------------------------------------------------------------------- #
def test_subdivision_refines_below_max_edge():
  mesh = tessellate_shape(Box(20, 20, 10))
  # Mid-gray => no displacement => edge lengths reflect subdivision alone.
  # simplify=0 keeps the dense mesh; decimation would re-merge flat triangles
  # (lengthening edges) and defeat the max-edge check this test is about.
  out = texturize_mesh(mesh, np.full((4, 4), 0.5), scale=6.0, simplify=0)
  assert len(out.triangles) > len(mesh.triangles)
  assert _trimesh(out).edges_unique_length.max() <= 6.0 / 16 + 1e-6


@pytest.mark.parametrize(
  "shape",
  [Box(20, 20, 10), fillet(Box(20, 20, 10).edges(), 2), Sphere(10)],
  ids=["box", "filleted", "sphere"],
)
def test_textured_mesh_stays_watertight(shape):
  mesh = tessellate_shape(shape)
  # The displacement step must keep the mesh watertight (T-junction free). QEM
  # decimation can introduce a few non-manifold edges, so disable it here to test
  # the invariant the subdivision actually guarantees.
  out = texturize_mesh(
    mesh, np.ones((8, 8)), amplitude=0.4, scale=5.0, keep_bottom=False, simplify=0
  )
  assert _trimesh(out).is_watertight


def test_max_triangles_guard_raises():
  mesh = tessellate_shape(Box(20, 20, 10))
  with pytest.raises(ValueError, match="max_triangles"):
    texturize_mesh(mesh, np.ones((4, 4)), scale=1.0, max_edge=0.2, max_triangles=1000)


# --------------------------------------------------------------------------- #
# Masking: bed pin + angle limits
# --------------------------------------------------------------------------- #
def test_keep_bottom_pins_bed_plane():
  mesh = tessellate_shape(Box(20, 20, 10))  # bottom face at z = -5
  out = texturize_mesh(
    mesh, np.ones((4, 4)), amplitude=0.5, scale=6.0, keep_bottom=True
  )
  v = np.asarray(out.vertices)
  # The bed plane stays put (not pushed out to -5.5) so the first layer is flat.
  assert v[:, 2].min() == pytest.approx(-5.0, abs=1e-9)
  on_bed = v[v[:, 2] <= -5.0 + 1e-6]
  assert np.allclose(on_bed[:, 2], -5.0)


def test_top_angle_protects_top_face():
  mesh = tessellate_shape(Box(20, 20, 10))  # top face at z = 5
  kw = dict(amplitude=0.5, scale=6.0, keep_bottom=False)
  masked = texturize_mesh(mesh, np.ones((4, 4)), top_angle=45.0, **kw)
  unmasked = texturize_mesh(mesh, np.ones((4, 4)), **kw)
  mv, uv = np.asarray(masked.vertices), np.asarray(unmasked.vertices)
  # Unmasked, the flat top pushes fully to z=5.5; masking the up-facing top
  # holds the top face down (only the 45deg edge ring, at the limit, still moves).
  assert uv[:, 2].max() == pytest.approx(5.5, abs=1e-3)
  assert mv[:, 2].max() < 5.45
  # Vertical side walls (horizontal normals) are unaffected by the top limit.
  assert mv[:, 0].max() == pytest.approx(10.5, abs=1e-3)


# --------------------------------------------------------------------------- #
# Project wiring + 3mf output
# --------------------------------------------------------------------------- #
def test_apply_texture_end_to_end(tmp_path):
  base = tessellate_shape(Box(20, 20, 10))
  proj = Project()
  proj.add_object(Box(20, 20, 10), name="Textured").parts[0].apply_texture(
    np.ones((8, 8)), amplitude=0.4, scale=6.0
  )
  out = proj.save(tmp_path / "t.3mf")

  with zipfile.ZipFile(out) as z:
    model = z.read(MODEL_PATH).decode()
  # The exported mesh is the subdivided/displaced one, far denser than the base.
  assert model.count("<triangle ") > len(base.triangles)


def test_texture_and_paint_conflict_raises(tmp_path):
  box = Box(20, 20, 10)
  part = Project().add_object(box, name="o").parts[0]
  part.apply_texture(np.ones((4, 4)), scale=6.0)
  part.paint_seam(box.faces().sort_by(Axis.Z)[-1], mode=EnforcerBlockerType.ENFORCER)
  with pytest.raises(ValueError, match="texturing and painting"):
    part._resolve(1, 0.01, 0.1)


def test_planar_mode_runs(tmp_path):
  mesh = tessellate_shape(Box(20, 20, 10))
  out = texturize_mesh(
    mesh,
    np.ones((4, 4)),
    amplitude=0.3,
    scale=6.0,
    mode=ProjectionMode.PLANAR_XY,
    simplify=0,
  )
  assert _trimesh(out).is_watertight


# --------------------------------------------------------------------------- #
# Selecting faces + combining multiple textures
# --------------------------------------------------------------------------- #
def test_texture_only_selected_face():
  box = Box(20, 20, 20)  # origin-centred: top face at z=10, sides at x=+/-10
  part = Project().add_object(box, name="o").parts[0]
  part.apply_texture(
    np.ones((4, 4)),
    faces=box.faces().sort_by(Axis.Z)[-1],
    amplitude=0.5,
    scale=6.0,
    simplify=0,  # test selection/displacement geometry, not decimation
  )
  mesh = part._resolve(1, 0.01, 0.1).mesh
  v = np.asarray(mesh.vertices)
  assert _trimesh(mesh).is_watertight
  assert v[:, 2].max() == pytest.approx(10.5, abs=0.05)  # top face pushed out
  assert v[:, 0].max() == pytest.approx(10.0, abs=1e-6)  # untextured sides untouched
  assert v[:, 2].min() == pytest.approx(-10.0, abs=1e-6)  # and so is the bottom


def test_multiple_textures_on_different_faces():
  box = Box(20, 20, 20)
  part = Project().add_object(box, name="o").parts[0]
  part.apply_texture(
    np.ones((4, 4)),
    faces=box.faces().sort_by(Axis.Z)[-1],
    amplitude=0.5,
    scale=6.0,
    simplify=0,
  )
  part.apply_texture(
    np.ones((4, 4)),
    faces=box.faces().sort_by(Axis.Y)[0],
    amplitude=0.4,
    scale=6.0,
    simplify=0,
  )
  mesh = part._resolve(1, 0.01, 0.1).mesh
  v = np.asarray(mesh.vertices)
  assert _trimesh(mesh).is_watertight
  assert v[:, 2].max() == pytest.approx(10.5, abs=0.05)  # top out by 0.5
  assert v[:, 1].min() == pytest.approx(-10.4, abs=0.05)  # -Y face out by 0.4
  assert v[:, 0].max() == pytest.approx(10.0, abs=1e-6)  # the rest untouched


def test_apply_texture_unknown_face_raises():
  part = Project().add_object(Box(20, 20, 20), name="o").parts[0]
  stranger = Box(5, 5, 5).faces()[0]  # a face from a different shape
  part.apply_texture(np.ones((4, 4)), faces=stranger, scale=6.0)
  with pytest.raises(ValueError, match="not part of this part"):
    part._resolve(1, 0.01, 0.1)


# --------------------------------------------------------------------------- #
# Simplification: QEM decimation of the displaced mesh
# --------------------------------------------------------------------------- #
def test_simplify_reduces_triangles_but_keeps_shape():
  mesh = tessellate_shape(Box(20, 20, 10))
  img = np.random.default_rng(0).random((32, 32))
  dense = texturize_mesh(mesh, img, amplitude=0.4, scale=4.0, simplify=0)
  light = texturize_mesh(mesh, img, amplitude=0.4, scale=4.0, simplify=0.8)
  # ~80% fewer triangles, yet the silhouette barely moves (deviation << amplitude).
  assert len(light.triangles) < 0.4 * len(dense.triangles)
  assert _bbox(light) == pytest.approx(_bbox(dense), abs=0.3)


def test_simplify_zero_disables_decimation():
  mesh = tessellate_shape(Box(20, 20, 10))
  img = np.full((4, 4), 0.5)
  dense = texturize_mesh(mesh, img, scale=6.0, simplify=0)
  default = texturize_mesh(mesh, img, scale=6.0)  # simplify defaults to ~half
  assert len(default.triangles) < len(dense.triangles)


def test_part_simplify_strongest_call_wins():
  box = Box(20, 20, 20)
  top, side = box.faces().sort_by(Axis.Z)[-1], box.faces().sort_by(Axis.Y)[0]

  def resolve(s_top, s_side):
    part = Project().add_object(box, name="o").parts[0]
    part.apply_texture(np.ones((4, 4)), faces=top, scale=6.0, simplify=s_top)
    part.apply_texture(np.ones((4, 4)), faces=side, scale=6.0, simplify=s_side)
    return len(part._resolve(1, 0.01, 0.1).mesh.triangles)

  # One aggressive request decimates the whole baked mesh, even alongside a 0 call.
  assert resolve(0.0, 0.8) < resolve(0.0, 0.0)
