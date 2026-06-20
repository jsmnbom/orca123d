"""Tessellation of build123d shapes into triangle meshes for 3MF export."""

from dataclasses import dataclass

import numpy as np
from build123d.topology import Shape
from OCP.BRep import BRep_Tool
from OCP.TopAbs import TopAbs_Orientation
from OCP.TopLoc import TopLoc_Location

# Quantization used to weld coincident vertices. Nodes shared along an edge of a
# whole-shape triangulation are computed once, so equal positions land in the
# same bucket; 1e-5 mm (10 nm) is far below any printable feature size.
_WELD_DECIMALS = 5


@dataclass(eq=False)  # eq disabled: numpy fields make the generated __eq__ raise
class MeshData:
  """A triangulated mesh plus provenance back to the source build123d faces.

  Attributes:
    vertices: ``(N, 3)`` float64 array of ``(x, y, z)`` coordinates in
      millimeters, welded (shared).
    triangles: ``(M, 3)`` int64 array of zero-based vertex indices.
    face_ranges: one ``(start, end)`` half-open triangle-index range per
      source face, in ``shape.faces()`` order. Enables per-face painting
      (seam / support / fuzzy skin) without re-tessellating.
  """

  vertices: np.ndarray
  triangles: np.ndarray
  face_ranges: list[tuple[int, int]]


def tessellate_shape(
  shape: Shape, tolerance: float = 0.01, angular_tolerance: float = 0.1
) -> MeshData:
  """Tessellate a build123d shape into a manifold, welded triangle mesh.

  The whole shape is triangulated at once (via ``Shape.mesh``) so that edges
  shared between faces get a single, consistent discretization. Coincident
  vertices are then welded into one shared index buffer, which is what makes
  the exported mesh manifold (per-face tessellation would duplicate every
  shared edge vertex and read as non-manifold in the slicer).

  Winding is corrected per face for reversed orientations, mirroring
  build123d's own ``Shape.tessellate``.
  """
  shape.mesh(tolerance, angular_tolerance)

  vertices: list[tuple[float, float, float]] = []
  triangles: list[tuple[int, int, int]] = []
  face_ranges: list[tuple[int, int]] = []
  index_of: dict[tuple[float, float, float], int] = {}

  for face in shape.faces():
    assert face.wrapped is not None
    loc = TopLoc_Location()
    poly = BRep_Tool.Triangulation_s(face.wrapped, loc)
    start = len(triangles)
    if poly is None:
      face_ranges.append((start, start))
      continue

    trsf = loc.Transformation()
    reverse = face.wrapped.Orientation() == TopAbs_Orientation.TopAbs_REVERSED

    # Map this face's local node indices (1-based) to welded global indices.
    local_to_global: list[int] = []
    for i in range(1, poly.NbNodes() + 1):
      pnt = poly.Node(i).Transformed(trsf)
      xyz = (pnt.X(), pnt.Y(), pnt.Z())
      key = (
        round(xyz[0], _WELD_DECIMALS),
        round(xyz[1], _WELD_DECIMALS),
        round(xyz[2], _WELD_DECIMALS),
      )
      gi = index_of.get(key)
      if gi is None:
        gi = len(vertices)
        index_of[key] = gi
        vertices.append(xyz)
      local_to_global.append(gi)

    for tri in poly.Triangles():
      a = local_to_global[tri.Value(1) - 1]
      b = local_to_global[tri.Value(2) - 1]
      c = local_to_global[tri.Value(3) - 1]
      if reverse:
        a, b, c = a, c, b
      # Skip triangles made degenerate by welding.
      if a == b or b == c or a == c:
        continue
      triangles.append((a, b, c))

    face_ranges.append((start, len(triangles)))

  if not triangles:
    raise ValueError("Shape produced no triangles when tessellated")
  return MeshData(
    np.asarray(vertices, dtype=np.float64),
    np.asarray(triangles, dtype=np.int64),
    face_ranges,
  )
