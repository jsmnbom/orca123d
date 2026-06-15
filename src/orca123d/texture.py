"""Bake a grayscale heightmap into a mesh as real geometry (surface texturing).

This is a Python port of the core of CNC Kitchen's stlTexturizer / BumpMesh
(https://github.com/CNCKitchen/stlTexturizer): adaptively subdivide a mesh,
project a texture onto it, sample the texture per vertex, and displace each
vertex along its (smooth) surface normal. Unlike OrcaSlicer's slice-time fuzzy
skin, the texture becomes part of the geometry, so it survives in any slicer and
gives precise, repeatable relief.

Only the MVP feature set is implemented: adaptive subdivision, triplanar / planar
projection, symmetric amplitude, top/bottom angle masking and a bed-plane pin.
A texture may be applied to a chosen subset of the source faces, and several can
be combined (different textures on different faces). Cubic/cylindrical/spherical
projection, painted exclusions, boundary falloff and QEM decimation from the
original tool are intentionally left out for now.

Subdivision uses BumpMesh's global edge-marking scheme rather than
``trimesh.remesh.subdivide_to_size``: the latter subdivides only over-long faces
and produces a "triangle soup" with T-junctions, which tears open into cracks
once vertices are displaced. Marking long edges globally (so both faces sharing
an edge agree to split it) keeps the mesh watertight. For a face subset only the
selected faces' edges are marked; an edge shared with an unselected face is still
split on both sides (and the neighbour retriangulated) so no T-junctions appear,
and only vertices interior to the selected faces are displaced -- the shared
boundary stays put, which keeps neighbouring faces flat and the mesh watertight.
"""

from dataclasses import dataclass
from enum import Enum
from os import PathLike
from typing import TYPE_CHECKING, Union

import numpy as np
import trimesh

from .mesh import MeshData, simplify_mesh

if TYPE_CHECKING:
  from PIL.Image import Image

__all__ = ["ProjectionMode", "texturize_mesh"]

# A heightmap source: an image file, a PIL image, or a 2-D/3-D grayscale array.
ImageLike = Union[str, "PathLike[str]", "Image", np.ndarray]


class ProjectionMode(str, Enum):
  """How the 2-D texture is projected onto the 3-D surface."""

  TRIPLANAR = "triplanar"  # blend three planar samples by |normal|**4 (default)
  PLANAR_XY = "planar_xy"  # project straight down the Z axis
  PLANAR_XZ = "planar_xz"  # project along the Y axis
  PLANAR_YZ = "planar_yz"  # project along the X axis


# (u-axis, v-axis) world axes for each planar projection. The associated normal
# axis (the projection direction) is the third one; used for triplanar weights.
_PLANE_AXES: dict[ProjectionMode, tuple[int, int]] = {
  ProjectionMode.PLANAR_YZ: (1, 2),  # normal axis 0 (X)
  ProjectionMode.PLANAR_XZ: (0, 2),  # normal axis 1 (Y)
  ProjectionMode.PLANAR_XY: (0, 1),  # normal axis 2 (Z)
}


@dataclass
class TextureJob:
  """One texturing operation: a heightmap, its parameters, and target faces.

  ``face_ids`` are indices into the mesh's ``face_ranges`` (i.e. ``shape.faces()``
  order); ``None`` means the whole mesh. Built via :func:`make_job` so defaults
  and the heightmap are resolved once, then handed to :func:`apply_textures`.
  """

  heightmap: np.ndarray
  amplitude: float
  scale: tuple[float, float]
  offset: tuple[float, float]
  rotation: float
  mode: ProjectionMode
  max_edge: float
  top_angle: float
  bottom_angle: float
  keep_bottom: bool
  max_triangles: int
  face_ids: tuple[int, ...] | None


def make_job(
  image: ImageLike,
  *,
  amplitude: float = 0.3,
  scale: float | tuple[float, float] = 10.0,
  offset: tuple[float, float] = (0.0, 0.0),
  rotation: float = 0.0,
  mode: ProjectionMode = ProjectionMode.TRIPLANAR,
  max_edge: float | None = None,
  top_angle: float = 90.0,
  bottom_angle: float = 90.0,
  keep_bottom: bool = True,
  max_triangles: int = 2_000_000,
  face_ids: tuple[int, ...] | None = None,
) -> TextureJob:
  """Resolve defaults and load ``image`` into a :class:`TextureJob`."""
  su, sv = (scale, scale) if isinstance(scale, (int, float)) else scale
  if su <= 0 or sv <= 0:
    raise ValueError("scale must be positive")
  if max_edge is None:
    max_edge = max(su, sv) / 16.0
  return TextureJob(
    heightmap=_load_heightmap(image),
    amplitude=float(amplitude),
    scale=(float(su), float(sv)),
    offset=offset,
    rotation=rotation,
    mode=mode,
    max_edge=max(float(max_edge), 0.15),
    top_angle=top_angle,
    bottom_angle=bottom_angle,
    keep_bottom=keep_bottom,
    max_triangles=max_triangles,
    face_ids=None if face_ids is None else tuple(face_ids),
  )


def texturize_mesh(
  mesh: MeshData,
  image: ImageLike,
  *,
  amplitude: float = 0.3,
  scale: float | tuple[float, float] = 10.0,
  offset: tuple[float, float] = (0.0, 0.0),
  rotation: float = 0.0,
  mode: ProjectionMode = ProjectionMode.TRIPLANAR,
  max_edge: float | None = None,
  top_angle: float = 90.0,
  bottom_angle: float = 90.0,
  keep_bottom: bool = True,
  max_triangles: int = 2_000_000,
  simplify: float = 0.5,
) -> MeshData:
  """Return a new :class:`MeshData` with ``image`` baked into the whole mesh.

  ``image`` is a grayscale heightmap (file path, PIL image, or numpy array).
  Mid-gray (0.5) is neutral, white pushes out and black pushes in, so volume is
  roughly preserved; ``amplitude`` is the peak displacement in millimetres.
  ``scale`` is the world size in millimetres of one texture tile (a float, or
  ``(u, v)``); ``offset``/``rotation`` shift/rotate the texture in UV space;
  ``mode`` selects the projection. The mesh is adaptively subdivided so every
  edge is at most ``max_edge`` mm (default ``max(scale) / 16``), capped at
  ``max_triangles``. ``top_angle``/``bottom_angle`` suppress texture on
  near-horizontal up/down surfaces, and ``keep_bottom`` pins bed-plane vertices.

  ``simplify`` decimates the displaced mesh by that fraction of triangles
  (default ~half; ``0`` keeps every triangle) -- subdivision makes a dense mesh
  and QEM collapses the redundant flat areas back down. See :func:`simplify_mesh`.

  To texture only some faces, build a :class:`TextureJob` with ``face_ids`` and
  call :func:`apply_textures` (this is what ``Part.apply_texture`` does).
  """
  job = make_job(
    image,
    amplitude=amplitude,
    scale=scale,
    offset=offset,
    rotation=rotation,
    mode=mode,
    max_edge=max_edge,
    top_angle=top_angle,
    bottom_angle=bottom_angle,
    keep_bottom=keep_bottom,
    max_triangles=max_triangles,
  )
  return apply_textures(mesh, [job], simplify=simplify)


def apply_textures(
  mesh: MeshData, jobs: list[TextureJob], *, simplify: float = 0.5
) -> MeshData:
  """Apply one or more :class:`TextureJob` to ``mesh``, returning a new mesh.

  All jobs share a single subdivision pass (so a shared edge is split once), then
  each job displaces the vertices interior to its faces. Overlapping jobs: the
  last one wins on a shared vertex. ``simplify`` decimates the displaced result by
  that fraction of triangles (``0`` to keep the dense mesh); see
  :func:`simplify_mesh`.
  """
  if not jobs:
    return mesh

  verts = np.asarray(mesh.vertices, dtype=np.float64)
  faces = np.asarray(mesh.triangles, dtype=np.int64)
  num_faces = len(mesh.face_ranges)

  # Per-triangle source-face id, tracked through subdivision so each job knows
  # which triangles (and thus vertices) are its own.
  face_id = np.empty(len(faces), dtype=np.int64)
  for fi, (start, end) in enumerate(mesh.face_ranges):
    face_id[start:end] = fi

  # Per-face subdivision target: the finest max_edge of any job covering it,
  # inf for faces no job touches (those are never marked for splitting).
  target = np.full(num_faces, np.inf)
  for job in jobs:
    covered = range(num_faces) if job.face_ids is None else job.face_ids
    for fi in covered:
      target[fi] = min(target[fi], job.max_edge)

  max_tris = max(job.max_triangles for job in jobs)
  verts, faces, face_id = _subdivide_adaptive(verts, faces, face_id, target, max_tris)

  tri = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
  verts = np.asarray(tri.vertices, dtype=np.float64)
  normals = np.asarray(tri.vertex_normals, dtype=np.float64)

  disp = np.zeros(len(verts))
  pin_bed = np.zeros(len(verts), dtype=bool)
  zmin = float(verts[:, 2].min())
  for job in jobs:
    if job.face_ids is None:
      vert_in = np.ones(len(verts), dtype=bool)
    else:
      tri_in = np.isin(face_id, np.asarray(job.face_ids, dtype=face_id.dtype))
      # A vertex is "interior" to the job only if every incident triangle is
      # its own; boundary vertices (shared with other faces) stay pinned, which
      # keeps neighbours flat and the mesh watertight.
      vert_in = np.ones(len(verts), dtype=bool)
      vert_in[faces[~tri_in].ravel()] = False
    grey = _sample_projected(
      verts, normals, job.heightmap, job.mode, job.scale, job.offset, job.rotation
    )
    d = (grey - 0.5) * 2.0 * job.amplitude
    d *= _angle_mask(normals, job.top_angle, job.bottom_angle)
    disp[vert_in] = d[vert_in]
    if job.keep_bottom:
      pin_bed |= vert_in & (verts[:, 2] <= zmin + 1e-4)
  disp[pin_bed] = 0.0

  out_verts = verts + normals * disp[:, None]
  out = MeshData(
    vertices=out_verts,
    triangles=faces,
    face_ranges=[(0, len(faces))],
  )
  return simplify_mesh(out, simplify)


def _load_heightmap(image: ImageLike) -> np.ndarray:
  """Coerce ``image`` to a 2-D float array of grayscale values in ``[0, 1]``."""
  if isinstance(image, np.ndarray):
    arr = image.astype(np.float64)
    if arr.ndim == 3:  # collapse RGB(A) to luminance-ish average of colour planes
      arr = arr[..., :3].mean(axis=2)
    if not np.issubdtype(image.dtype, np.floating) or arr.max() > 1.0:
      arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)

  from PIL import Image as _PILImage

  img = image if isinstance(image, _PILImage.Image) else _PILImage.open(image)
  return np.asarray(img.convert("L"), dtype=np.float64) / 255.0


def _subdivide_adaptive(
  verts: np.ndarray,
  faces: np.ndarray,
  face_id: np.ndarray,
  face_target: np.ndarray,
  max_triangles: int,
  max_iter: int = 24,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
  """Subdivide until every targeted edge is <= its target, staying watertight.

  ``face_target`` gives a per-source-face max edge length (``inf`` to never
  split). An edge's target is the smallest target of its incident faces, so an
  edge shared between a targeted and an untargeted face is still split on both
  sides; the neighbour is retriangulated by how many of its edges are marked (0
  keeps it, 1 bisects, 2 fans into three, 3 is the classic 1->4 split), so no
  T-junctions appear. ``face_id`` is carried onto every child triangle.
  """
  verts = np.array(verts, dtype=np.float64, copy=True)
  faces = np.array(faces, dtype=np.int64, copy=True)
  face_id = np.array(face_id, dtype=np.int64, copy=True)

  for _ in range(max_iter):
    tri_edges = np.concatenate(
      [faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]], axis=0
    )
    keys = np.sort(tri_edges, axis=1)
    # Find unique undirected edges. Pack each (lo, hi) vertex-index pair into one
    # int64 key and dedup in 1-D rather than np.unique(keys, axis=0): the latter
    # lexsorts the rows as a void dtype and dominated the whole texturize runtime
    # (~75%); the packed 1-D sort is ~10x faster for the same edge<->triangle
    # mapping. Indices are < len(verts), so the packed keys stay well within int64.
    n = len(verts)
    packed = keys[:, 0].astype(np.int64) * n + keys[:, 1]
    uniq_packed, inv = np.unique(packed, return_inverse=True)
    inv = inv.reshape(-1)
    uniq = np.stack([uniq_packed // n, uniq_packed % n], axis=1)

    # Per-edge target = min over its incident triangles' (per-face) targets.
    tri_target = face_target[face_id]
    edge_target = np.full(len(uniq), np.inf)
    np.minimum.at(edge_target, inv, np.tile(tri_target, 3))

    d = verts[uniq[:, 0]] - verts[uniq[:, 1]]
    long_edge = (np.einsum("ij,ij->i", d, d) > edge_target * edge_target) & np.isfinite(
      edge_target
    )
    if not long_edge.any():
      break

    # Allocate one new midpoint vertex per marked edge.
    mid_index = np.full(len(uniq), -1, dtype=np.int64)
    long_idx = np.nonzero(long_edge)[0]
    mids = 0.5 * (verts[uniq[long_idx, 0]] + verts[uniq[long_idx, 1]])
    mid_index[long_idx] = np.arange(len(verts), len(verts) + len(long_idx))
    verts = np.concatenate([verts, mids], axis=0)

    per_face = inv.reshape(3, -1).T  # columns: edges ab, bc, ca
    m_ab, m_bc, m_ca = long_edge[per_face.T]
    mid_ab, mid_bc, mid_ca = mid_index[per_face.T]
    a, b, c = faces[:, 0], faces[:, 1], faces[:, 2]
    count = m_ab.astype(np.int64) + m_bc + m_ca

    def tri(u, v, w, m):  # stack three index columns under boolean mask ``m``
      return np.stack([u[m], v[m], w[m]], axis=1)

    out: list[np.ndarray] = []
    out_id: list[np.ndarray] = []

    def emit(child_faces: np.ndarray, m: np.ndarray) -> None:
      out.append(child_faces)
      out_id.append(face_id[m])

    keep = count == 0
    emit(faces[keep], keep)

    only_ab = (count == 1) & m_ab
    emit(tri(a, mid_ab, c, only_ab), only_ab)
    emit(tri(mid_ab, b, c, only_ab), only_ab)
    only_bc = (count == 1) & m_bc
    emit(tri(a, b, mid_bc, only_bc), only_bc)
    emit(tri(a, mid_bc, c, only_bc), only_bc)
    only_ca = (count == 1) & m_ca
    emit(tri(a, b, mid_ca, only_ca), only_ca)
    emit(tri(b, c, mid_ca, only_ca), only_ca)

    ab_bc = (count == 2) & m_ab & m_bc  # split corner b
    emit(tri(mid_ab, b, mid_bc, ab_bc), ab_bc)
    emit(tri(a, mid_ab, mid_bc, ab_bc), ab_bc)
    emit(tri(a, mid_bc, c, ab_bc), ab_bc)
    bc_ca = (count == 2) & m_bc & m_ca  # split corner c
    emit(tri(mid_bc, c, mid_ca, bc_ca), bc_ca)
    emit(tri(a, b, mid_bc, bc_ca), bc_ca)
    emit(tri(a, mid_bc, mid_ca, bc_ca), bc_ca)
    ca_ab = (count == 2) & m_ca & m_ab  # split corner a
    emit(tri(a, mid_ab, mid_ca, ca_ab), ca_ab)
    emit(tri(mid_ab, b, c, ca_ab), ca_ab)
    emit(tri(mid_ab, c, mid_ca, ca_ab), ca_ab)

    all3 = count == 3
    emit(tri(a, mid_ab, mid_ca, all3), all3)
    emit(tri(b, mid_bc, mid_ab, all3), all3)
    emit(tri(c, mid_ca, mid_bc, all3), all3)
    emit(tri(mid_ab, mid_bc, mid_ca, all3), all3)

    faces = np.concatenate(out, axis=0)
    face_id = np.concatenate(out_id, axis=0)
    if len(faces) > max_triangles:
      raise ValueError(
        f"texture subdivision exceeded max_triangles ({max_triangles:,}); "
        "increase the texture scale / max_edge, or raise max_triangles"
      )

  return verts, faces, face_id


def _sample_projected(
  verts: np.ndarray,
  normals: np.ndarray,
  heightmap: np.ndarray,
  mode: ProjectionMode,
  scale: tuple[float, float],
  offset: tuple[float, float],
  rotation: float,
) -> np.ndarray:
  """Per-vertex grayscale value via the chosen projection."""
  if mode is ProjectionMode.TRIPLANAR:
    weights = np.abs(normals) ** 4
    weights /= weights.sum(axis=1, keepdims=True) + 1e-12
    grey = np.zeros(len(verts))
    # normal axis 0/1/2 -> planes YZ/XZ/XY
    for axis, plane in enumerate(
      (ProjectionMode.PLANAR_YZ, ProjectionMode.PLANAR_XZ, ProjectionMode.PLANAR_XY)
    ):
      u, v = _planar_uv(verts, _PLANE_AXES[plane], scale, offset, rotation)
      grey += weights[:, axis] * _sample_bilinear(heightmap, u, v)
    return grey

  u, v = _planar_uv(verts, _PLANE_AXES[mode], scale, offset, rotation)
  return _sample_bilinear(heightmap, u, v)


def _planar_uv(
  verts: np.ndarray,
  axes: tuple[int, int],
  scale: tuple[float, float],
  offset: tuple[float, float],
  rotation: float,
) -> tuple[np.ndarray, np.ndarray]:
  """World coordinates -> tiled UV for one axis-aligned plane."""
  ai, aj = axes
  u = verts[:, ai] / scale[0] + offset[0]
  v = verts[:, aj] / scale[1] + offset[1]
  if rotation:
    rad = np.radians(rotation)
    cos, sin = np.cos(rad), np.sin(rad)
    u, v = u * cos - v * sin, u * sin + v * cos
  return u, v


def _sample_bilinear(img: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
  """Bilinearly sample ``img`` at tiled (wrapping) UV coordinates."""
  h, w = img.shape
  u = u - np.floor(u)
  v = v - np.floor(v)
  fx = u * w - 0.5
  fy = (1.0 - v) * h - 0.5  # flip V: image row 0 is the top
  x0 = np.floor(fx).astype(np.int64)
  y0 = np.floor(fy).astype(np.int64)
  tx, ty = fx - x0, fy - y0
  x0m, x1m = x0 % w, (x0 + 1) % w
  y0m, y1m = y0 % h, (y0 + 1) % h
  top = img[y0m, x0m] * (1 - tx) + img[y0m, x1m] * tx
  bot = img[y1m, x0m] * (1 - tx) + img[y1m, x1m] * tx
  return top * (1 - ty) + bot * ty


def _angle_mask(
  normals: np.ndarray, top_angle: float, bottom_angle: float
) -> np.ndarray:
  """Per-vertex displacement factor in [0, 1] from up/down facing limits.

  ``up`` is the normal's angle above horizontal (+90 = straight up, -90 = down).
  Surfaces past ``top_angle`` / below ``-bottom_angle`` fade to zero over a small
  band so the texture stops without a hard ring.
  """
  band = 5.0  # degrees of linear falloff at the limit
  up = np.degrees(np.arcsin(np.clip(normals[:, 2], -1.0, 1.0)))
  excess = np.maximum(up - top_angle, -up - bottom_angle)
  return np.clip(1.0 - excess / band, 0.0, 1.0)
