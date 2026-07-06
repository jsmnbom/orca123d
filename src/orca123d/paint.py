"""Per-triangle "painting" for OrcaSlicer 3MF (seam / support / color / fuzzy).

OrcaSlicer stores painted regions as a string attribute on each ``<triangle>``
(``paint_seam``, ``paint_supports``, ``mmu_segmentation``, ``fuzzy_skin``). The
string encodes a recursive midpoint subdivision of that triangle, with each leaf
sub-triangle assigned a state. This module reproduces that encoding so paint can
be authored from build123d geometry.

Encoding (ported from ``TriangleSelector::serialize`` /
``FacetsAnnotation::get_triangle_as_string`` in OrcaSlicer):

* A painted triangle is a tree. Each node is serialized as a 4-bit nibble; bits
  are packed least-significant-first, and the final hex string is built by
  *prepending* each hex digit (so the first node ends up as the last character).
* Node nibble: low 2 bits = number of split sides (0 = leaf), next 2 bits = the
  leaf state, or (for a split) the "special side".
* Leaf states < 3 use those 2 bits directly: ``NONE``→``0``, ``ENFORCER``→``4``,
  ``BLOCKER``→``8``. State >= 3 (color extruders) sets both bits (``11``) as an
  escape and appends 4 more bits of ``state - 3``.
* We only ever emit full 3-way splits (split sides = 3, special side = 0), whose
  nibble is ``3`` followed by its 4 children serialized **in reverse order**.

The 3-way split geometry mirrors ``TriangleSelector::perform_split``: midpoints
``m01, m12, m20`` of edges (v0,v1), (v1,v2), (v2,v0) give children
``(v0,m01,m20)``, ``(m01,v1,m12)``, ``(m12,v2,m20)`` and centre ``(m01,m12,m20)``.
Because we split exactly the way OrcaSlicer reconstructs, the leaf we label is the
same sub-triangle OrcaSlicer colors on load.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Iterable, Sequence, Union

import numpy as np
from build123d.topology import Shape
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.Geom import Geom_Surface
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt
from OCP.ShapeAnalysis import ShapeAnalysis_Surface
from OCP.TopAbs import TopAbs_IN, TopAbs_ON
from OCP.TopoDS import TopoDS_Face

from build123d import Face, Plane, Vector

from .mesh import MeshData

__all__ = [
  "EnforcerBlockerType",
  "SEAM_ATTR",
  "SUPPORT_ATTR",
  "COLOR_ATTR",
  "FUZZY_ATTR",
  "encode_tree",
  "decode",
  "encode_region_paint",
]


class EnforcerBlockerType(IntEnum):
  """Per-triangle paint state, mirroring OrcaSlicer's ``EnforcerBlockerType``.

  Seam, support, and fuzzy-skin painting use ``NONE``/``ENFORCER``/``BLOCKER``.
  Color (MMU) painting reuses ``ENFORCER`` as extruder 1 and ``BLOCKER`` as
  extruder 2, with raw ints >= 3 for higher extruders (stored via the extended
  nibble form). An ``IntEnum`` so members pack into the bitstream as their value.
  """

  NONE = 0
  ENFORCER = 1
  BLOCKER = 2


# 3MF ``<triangle>`` attribute names per paint kind (bbs_3mf.cpp). Seam is wired
# up today; the rest are here so the shared core can drive them later.
SEAM_ATTR = "paint_seam"
SUPPORT_ATTR = "paint_supports"
COLOR_ATTR = "paint_color"
FUZZY_ATTR = "paint_fuzzy_skin"

Point = Union[tuple[float, float, float], np.ndarray]
AABB = tuple[Point, Point]  # (min corner, max corner)
# A paint tree: an ``int`` state (leaf) or a 4-tuple of child trees (3-way split).
Tree = Union[int, tuple["Tree", "Tree", "Tree", "Tree"]]

_HEX = "0123456789ABCDEF"


# --------------------------------------------------------------------------- #
# Bitstream encode / decode (exact inverse of OrcaSlicer's serialization).
# --------------------------------------------------------------------------- #
def _emit(node: Tree, bits: list[int]) -> None:
  if isinstance(node, int):
    bits += (0, 0)  # split sides = 0 -> leaf
    if node >= 3:
      bits += (1, 1)  # escape: state stored in the following nibble
      n = node - 3
      bits += ((n >> 0) & 1, (n >> 1) & 1, (n >> 2) & 1, (n >> 3) & 1)
    else:
      bits += (node & 1, (node >> 1) & 1)
  else:
    bits += (1, 1, 0, 0)  # split sides = 3, special side = 0
    for child in reversed(node):  # serialized in reverse order
      _emit(child, bits)


def encode_tree(tree: Tree) -> str:
  """Serialize a paint tree to OrcaSlicer's hex string form."""
  bits: list[int] = []
  _emit(tree, bits)
  out: list[str] = []
  for off in range(0, len(bits), 4):
    code = bits[off] | bits[off + 1] << 1 | bits[off + 2] << 2 | bits[off + 3] << 3
    out.insert(0, _HEX[code])
  return "".join(out)


def decode(s: str) -> Tree:
  """Parse a hex paint string back into a tree (mirror of ``deserialize``).

  Used by tests to verify round-tripping against OrcaSlicer's algorithm.
  """
  bits: list[int] = []
  for ch in reversed(s):
    dec = int(ch, 16)
    bits += ((dec >> 0) & 1, (dec >> 1) & 1, (dec >> 2) & 1, (dec >> 3) & 1)

  pos = 0

  def nibble() -> int:
    nonlocal pos
    n = bits[pos] | bits[pos + 1] << 1 | bits[pos + 2] << 2 | bits[pos + 3] << 3
    pos += 4
    return n

  def walk() -> Tree:
    code = nibble()
    split_sides = code & 0b11
    if split_sides == 0:
      state = nibble() + 3 if (code & 0b1100) == 0b1100 else code >> 2
      return state
    children = [walk() for _ in range(split_sides + 1)]
    children.reverse()  # undo reverse-order serialization
    return tuple(children)  # type: ignore[return-value]

  return walk()


# --------------------------------------------------------------------------- #
# Geometry: subdivide a triangle against an "inside region" predicate.
# --------------------------------------------------------------------------- #
def _mid(a: Point, b: Point) -> Point:
  return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)


def _centroid(p0: Point, p1: Point, p2: Point) -> Point:
  return (
    (p0[0] + p1[0] + p2[0]) / 3,
    (p0[1] + p1[1] + p2[1]) / 3,
    (p0[2] + p1[2] + p2[2]) / 3,
  )


def _aabb_overlaps_tri(aabb: AABB, p0: Point, p1: Point, p2: Point) -> bool:
  """True unless the triangle's axis-aligned box is disjoint from ``aabb``."""
  lo, hi = aabb
  for k in range(3):
    if max(p0[k], p1[k], p2[k]) < lo[k] or min(p0[k], p1[k], p2[k]) > hi[k]:
      return False
  return True


def subdivide_classify(
  p0: Point,
  p1: Point,
  p2: Point,
  inside: Callable[[Point], bool],
  state: EnforcerBlockerType | int,
  max_depth: int,
  aabb: AABB,
  depth: int = 0,
) -> Tree | None:
  """Recursively split a triangle, labelling leaves inside ``region`` as ``state``.

  Returns ``None`` when no part of the triangle is painted (so no attribute is
  emitted for it). Uses 3-way midpoint splits matching OrcaSlicer's geometry.
  ``aabb`` is the region's (padded) bounding box; a triangle whose own box is
  disjoint from it is pruned without recursing. This cull never discards a thin
  region that crosses a large triangle (unlike sampling a few interior points).
  """
  if not _aabb_overlaps_tri(aabb, p0, p1, p2):
    return None
  in0, in1, in2 = inside(p0), inside(p1), inside(p2)
  if in0 and in1 and in2:
    return state
  if depth >= max_depth:
    return state if inside(_centroid(p0, p1, p2)) else None

  m01, m12, m20 = _mid(p0, p1), _mid(p1, p2), _mid(p2, p0)
  children = (
    subdivide_classify(p0, m01, m20, inside, state, max_depth, aabb, depth + 1),
    subdivide_classify(m01, p1, m12, inside, state, max_depth, aabb, depth + 1),
    subdivide_classify(m12, p2, m20, inside, state, max_depth, aabb, depth + 1),
    subdivide_classify(m01, m12, m20, inside, state, max_depth, aabb, depth + 1),
  )
  if all(c is None for c in children):
    return None
  # Replace empty children with NONE leaves so the tree has all four branches.
  return tuple(  # type: ignore[return-value]
    EnforcerBlockerType.NONE if c is None else c for c in children
  )


# --------------------------------------------------------------------------- #
# Region -> {triangle index: hex string}.
#
# A paint region is a build123d shape. Three kinds are supported, picked in this
# order: a *solid* (paint surface points inside it -- spans multiple faces, e.g.
# a cylinder biasing the seam to a corner), a planar *face/sketch* (a 2D mask on
# coplanar faces), or an *edge/wire* (paint within ``within`` mm of the curve --
# the natural way to pin a seam to an edge). The first two are exact; the edge
# and sketch boundaries are approximated by subdividing triangles to ``max_depth``.
# --------------------------------------------------------------------------- #
@dataclass
class _PlanarRegion:
  """One planar build123d face used as a 2D paint mask, with a point test."""

  origin: Vector
  normal: Vector
  surface: Geom_Surface
  face: TopoDS_Face

  def inside(self, p: Point, plane_tol: float, uv_tol: float) -> bool:
    # Reject points off the face's plane first (cheap), so triangles on other
    # faces don't get painted just because they project into the 2D mask.
    if abs((Vector(*p) - self.origin).dot(self.normal)) > plane_tol:
      return False
    sas = ShapeAnalysis_Surface(self.surface)
    uv = sas.ValueOfUV(gp_Pnt(*p), uv_tol)
    cls = BRepClass_FaceClassifier(self.face, uv, uv_tol)
    return cls.State() in (TopAbs_IN, TopAbs_ON)


def _iter_items(region: Shape | list[Shape]) -> list[Shape]:
  return list(region) if isinstance(region, (list, tuple)) else [region]


def _face_plane(face: Face) -> tuple[Vector, Vector] | None:
  try:
    plane = Plane(face)
  except Exception:
    return None
  return plane.origin, plane.z_dir


def _coplanar(o1: Vector, n1: Vector, o2: Vector, n2: Vector, tol: float) -> bool:
  if abs(abs(n1.dot(n2)) - 1.0) > 1e-6:
    return False
  return abs((o1 - o2).dot(n2)) <= tol


def _region_aabb(items: Sequence[Shape], pad: float) -> AABB:
  lo = [float("inf")] * 3
  hi = [float("-inf")] * 3
  for item in items:
    bb = item.bounding_box()
    mn, mx = tuple(bb.min), tuple(bb.max)
    for k in range(3):
      lo[k] = min(lo[k], mn[k])
      hi[k] = max(hi[k], mx[k])
  return (
    (lo[0] - pad, lo[1] - pad, lo[2] - pad),
    (hi[0] + pad, hi[1] + pad, hi[2] + pad),
  )


def _paint_triangles(
  mesh: MeshData,
  indices: Iterable[int],
  inside: Callable[[Point], bool],
  state: EnforcerBlockerType | int,
  max_depth: int,
  aabb: AABB,
  out: dict[int, str],
) -> None:
  for i in indices:
    a, b, c = mesh.triangles[i]
    # subdivide_classify works in plain-Python-float Point tuples; convert the
    # numpy rows here (restores the declared tuple contract and keeps the
    # recursion's scalar math native rather than per-element numpy ops).
    p0, p1, p2 = (tuple(v) for v in mesh.vertices[[a, b, c]].tolist())
    tree = subdivide_classify(p0, p1, p2, inside, state, max_depth, aabb)
    if tree is not None:
      out[i] = encode_tree(tree)


def _face_signature(face: Face) -> tuple[float, float, float, float]:
  """A face's area centroid (x, y, z) and area -- a fingerprint that is both
  orientation- and topology-independent, computed in a single surface-property
  pass. Two faces with the same surface over the same region share it, so it
  survives a face being *rebuilt* (new ``TShape``, same geometry) by sewing.
  """
  props = GProp_GProps()
  BRepGProp.SurfaceProperties_s(face.wrapped, props)
  c = props.CentreOfMass()
  return (c.X(), c.Y(), c.Z(), props.Mass())


class _FaceMatcher:
  """Membership test: does a face coincide with one of a fixed set of faces?

  We can't match by topological identity (``IsSame``) because the faces you hand
  to ``paint_*`` are usually *not* the faces on the part: ``Solid(Shell([...]))``
  sews its input faces, rebuilding them into fresh ``TShape``s, so a wall face
  and its counterpart on the part are no longer the same OCCT object. Instead we
  match on a geometric signature (:func:`_face_signature`), which sewing
  preserves. Every face's signature is computed once up front -- recomputing per
  comparison is far too slow for parts with hundreds of faces.
  """

  def __init__(self, faces: Sequence[Face], tol: float = 1e-6) -> None:
    self._sig = np.array(
      [_face_signature(f) for f in faces], dtype=float
    ).reshape(-1, 4)
    self._tol = tol

  def contains(self, face: Face) -> bool:
    if not len(self._sig):
      return False
    diff = np.abs(self._sig - _face_signature(face))
    center_ok = (diff[:, :3] <= self._tol).all(axis=1)
    # Area scales with the face, so its tolerance is relative (with a floor).
    area_ok = diff[:, 3] <= self._tol * np.maximum(self._sig[:, 3], 1.0)
    return bool((center_ok & area_ok).any())


def _paint_whole_faces(
  mesh: MeshData,
  model_faces: list[Face],
  region_faces: list[Face],
  state: EnforcerBlockerType | int,
  out: dict[int, str],
) -> None:
  """Paint every triangle of each model face that coincides with a region face.

  Matched by geometry (:class:`_FaceMatcher`), so the region faces only need to
  *be* part faces, not the part's actual ``TShape``s -- they survive sewing.
  Curvature-agnostic and exact: a face's triangle range comes straight from the
  tessellation (``mesh.face_ranges``) -- no plane, UV mask, or subdivision --
  emitting one whole leaf (``state``) per triangle.
  """
  leaf = encode_tree(state)
  region = _FaceMatcher(region_faces)
  for mface, (start, end) in zip(model_faces, mesh.face_ranges):
    if region.contains(mface):
      for i in range(start, end):
        out[i] = leaf


def encode_region_paint(
  mesh: MeshData,
  model_faces: list[Face],
  region: Shape | list[Shape],
  state: EnforcerBlockerType | int,
  max_depth: int,
  *,
  within: float = 1.0,
  plane_tol: float = 1e-4,
  uv_tol: float = 1e-6,
  solid_tol: float = 1e-6,
) -> dict[int, str]:
  """Map a build123d ``region`` to ``{triangle_index: hex paint string}``.

  ``model_faces`` are the source shape's faces in ``shape.faces()`` order, which
  matches ``mesh.face_ranges``. ``region`` is a solid, planar face/sketch, or
  edge/wire (see this section's header); ``within`` is the edge proximity radius.

  Face regions auto-detect their mode per face. A region face that coincides
  with one of the part's faces (matched by geometry, so it survives the part
  being rebuilt -- e.g. sewn by ``Solid(Shell([...]))``) is painted *whole* --
  its entire triangle range, exact at any curvature, so curved faces just work.
  A face that isn't a part face (e.g. a ``BuildSketch`` mask) is treated as a
  planar 2D *stencil* projected onto coplanar model faces, and so must be planar.
  """
  items = _iter_items(region)
  out: dict[int, str] = {}

  solids = [s for item in items for s in item.solids()]
  if solids:
    classifiers = [BRepClass3d_SolidClassifier(s.wrapped) for s in solids]

    def inside(p: Point) -> bool:
      pt = gp_Pnt(*p)
      for clf in classifiers:
        clf.Perform(pt, solid_tol)
        if clf.State() in (TopAbs_IN, TopAbs_ON):
          return True
      return False

    aabb = _region_aabb(items, pad=plane_tol)
    _paint_triangles(
      mesh, range(len(mesh.triangles)), inside, state, max_depth, aabb, out
    )
    return out

  faces = [f for item in items for f in item.faces()]
  if faces:
    # A region face that coincides with one of the part's faces is painted whole
    # (works at any curvature); anything else (e.g. a BuildSketch mask) drives the
    # planar 2D-stencil projection below and so must be planar.
    part = _FaceMatcher(model_faces)
    whole = [f for f in faces if part.contains(f)]
    stencil = [f for f in faces if not part.contains(f)]
    if whole:
      _paint_whole_faces(mesh, model_faces, whole, state, out)
    if not stencil:
      return out

    regions: list[_PlanarRegion] = []
    for face in stencil:
      plane = _face_plane(face)
      if plane is None:
        raise ValueError("paint region faces must be planar")
      origin, normal = plane
      regions.append(
        _PlanarRegion(origin, normal, BRep_Tool.Surface_s(face.wrapped), face.wrapped)
      )

    def inside(p: Point) -> bool:
      return any(r.inside(p, plane_tol, uv_tol) for r in regions)

    aabb = _region_aabb(stencil, pad=plane_tol)
    for face, (start, end) in zip(model_faces, mesh.face_ranges):
      fp = _face_plane(face)
      if fp is None:
        continue  # non-planar faces can't be coplanar with a planar region
      forigin, fnormal = fp
      if any(
        _coplanar(forigin, fnormal, r.origin, r.normal, plane_tol) for r in regions
      ):
        _paint_triangles(mesh, range(start, end), inside, state, max_depth, aabb, out)
    return out

  edges = [e.wrapped for item in items for e in item.edges()]
  if edges:

    def inside(p: Point) -> bool:
      vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex()
      return any(
        BRepExtrema_DistShapeShape(vertex, edge).Value() <= within for edge in edges
      )

    aabb = _region_aabb(items, pad=within + plane_tol)
    _paint_triangles(
      mesh, range(len(mesh.triangles)), inside, state, max_depth, aabb, out
    )
    return out

  raise ValueError("paint region must contain a solid, planar face, or edge")
