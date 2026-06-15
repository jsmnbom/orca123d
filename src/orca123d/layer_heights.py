"""Variable layer height -- ``Metadata/layer_heights_profile.txt``.

OrcaSlicer stores a per-object variable layer height as one line per object::

    object_id=<N>|z0;h0;z1;h1;z2;h2;...

a flat list of ``(z, layer_height)`` control points describing a piecewise-linear
curve the slicer samples while marching up in z (``generate_object_layers`` in
``Slicing.cpp``). Two details this module mirrors from ``bbs_3mf.cpp``:

* ``<N>`` is the **1-based ordinal of the object in the build**, *not* the mesh /
  components-object id used in ``model_settings.config`` (the importer maps it via
  ``find(object_index + 1)``). We emit it as the ``enumerate`` position over the
  resolved objects, which matches ``Project.objects`` order.
* z is measured from the object's bottom (objects are dropped to the bed), the
  first control point is at z=0, and the importer requires at least 4 numbers and
  an even count.

``optimize_for_faces`` takes the z-band spanned by a set of faces and ramps the
layer height from ``base_height`` down to ``min_layer_height`` across it (and back
out above it), limiting the change to ``max_change`` mm per layer so the
transition is gradual rather than an abrupt step.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .mesh import MeshData

if TYPE_CHECKING:
  from .project import ResolvedObject

# Mirrors libslic3r: EPSILON (libslic3r.h) and the per-step rate limit (Slicing.cpp).
_EPSILON = 1e-4
_LAYER_HEIGHT_CHANGE_STEP = 0.04


def build_layer_heights_profile(resolved_objects: list["ResolvedObject"]) -> str | None:
  """Render ``layer_heights_profile.txt``, or ``None`` if no object has a profile.

  Objects are indexed by their 1-based position in the build (``enumerate``),
  matching how OrcaSlicer's importer keys this file -- which differs from the
  mesh ids used in ``model_settings.config``.
  """
  lines: list[str] = []
  for ordinal, obj in enumerate(resolved_objects, start=1):
    profile = obj.layer_height_profile
    if not profile:
      continue
    flat = ";".join(f"{value:.6f}" for point in profile for value in point)
    lines.append(f"object_id={ordinal}|{flat}")
  if not lines:
    return None
  return "\n".join(lines) + "\n"


def optimize_for_faces(
  face_meshes: list[MeshData],
  *,
  z_origin: float,
  object_height: float,
  min_layer_height: float,
  base_height: float,
  max_change: float = _LAYER_HEIGHT_CHANGE_STEP,
) -> list[tuple[float, float]]:
  """Ramp ``base_height`` -> ``min_layer_height`` across the faces' z-span.

  The selected faces define a z-band that should print fine: the height steps down
  from ``base_height`` to ``min_layer_height`` on the way into the band and back up
  above it, never changing more than ``max_change`` mm between layers, so there is
  no abrupt layer-height jump. Everything outside the band stays at ``base_height``.
  z is object-relative (``z_origin`` is the object's bottom).
  """
  columns = [mesh.vertices[:, 2] for mesh in face_meshes if len(mesh.vertices)]
  if not columns:
    raise ValueError("no triangles in the selected faces to optimize for")
  zs = np.concatenate(columns) - z_origin
  band_lo = float(zs.min())
  band_hi = float(zs.max())

  def target(z: float) -> float:
    in_band = band_lo - _EPSILON <= z <= band_hi + _EPSILON
    return min_layer_height if in_band else base_height

  # March the object layer by layer, easing toward the target height. Storing a
  # control point per layer is fine -- _simplify collapses the flat/linear runs.
  points: list[tuple[float, float]] = []
  print_z = 0.0
  prev_h = base_height
  while print_z + _EPSILON < object_height:
    height = target(print_z)
    if prev_h - height > max_change:
      height = prev_h - max_change
    elif height - prev_h > max_change:
      height = prev_h + max_change
    height = max(height, min_layer_height)
    points.append((print_z, height))
    print_z += height
    prev_h = height
  points.append((object_height, prev_h))
  return _simplify(points)


def _simplify(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
  """Drop duplicate and collinear interior points -- the profile is piecewise
  linear, so a point on the segment between its neighbors carries no information.
  Keeps genuine ramps (whose interior points are not collinear) and steps."""
  out: list[tuple[float, float]] = []
  for z, h in points:
    # Drop exact duplicates first.
    if out and abs(out[-1][0] - z) <= _EPSILON and abs(out[-1][1] - h) <= _EPSILON:
      continue
    # If the previous point lies on the line from out[-2] to (z, h), replace it.
    while len(out) >= 2:
      (z0, h0), (z1, h1) = out[-2], out[-1]
      if z - z0 <= _EPSILON:  # same-z stack (a step) -- never collapse
        break
      t = (z1 - z0) / (z - z0)
      if abs(h0 + (h - h0) * t - h1) > 1e-6:
        break
      out.pop()
    out.append((z, h))
  return out
