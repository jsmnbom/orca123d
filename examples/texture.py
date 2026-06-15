"""Generate a model-only .3mf demoing surface texturing (baked-in displacement).

Run with: uv run python examples/texture.py
Then open texture.3mf in OrcaSlicer. Unlike the fuzzy-skin gizmo, the texture is
real geometry here -- the meshes are subdivided and their surfaces displaced by a
grayscale heightmap, so the relief shows in the 3D view (and in any slicer).

Each object uses a different procedural heightmap, generated in numpy below so the
example needs no image files. ``scale`` is the world size (mm) of one texture
tile; mid-gray is flat, white pushes out and black pushes in by up to
``amplitude`` mm. The default triplanar projection wraps the texture cleanly
around every face of an arbitrary shape. The last object shows ``apply_texture``
restricted to selected faces (and called twice for two different textures).
"""

import numpy as np
from build123d import Axis, Box, Pos, Sphere

from orca123d import Project


def _grid(n: int) -> tuple[np.ndarray, np.ndarray]:
  """A seamless [0,1)^2 sample grid (endpoint excluded so patterns tile)."""
  g = np.linspace(0.0, 1.0, n, endpoint=False)
  return np.meshgrid(g, g)


def dots(n: int = 256, freq: int = 3) -> np.ndarray:
  """A grid of smooth raised bumps."""
  u, v = _grid(n)
  return 0.5 + 0.5 * np.cos(2 * np.pi * freq * u) * np.cos(2 * np.pi * freq * v)


def knurl(n: int = 256, freq: int = 5) -> np.ndarray:
  """A diagonal cross-hatch, like a knurled grip."""
  u, v = _grid(n)
  diag = np.sin(2 * np.pi * freq * (u + v)) + np.sin(2 * np.pi * freq * (u - v))
  return 0.5 + 0.25 * diag


def stripes(n: int = 256, freq: int = 4) -> np.ndarray:
  """Smooth parallel ridges."""
  u, _ = _grid(n)
  return 0.5 + 0.5 * np.sin(2 * np.pi * freq * u)


def main() -> None:
  proj = Project()

  # 1. A cube with a knurled cross-hatch grip on every face.
  cube = proj.add_object(Box(20, 20, 20), name="1 Knurled cube")
  cube.parts[0].apply_texture(knurl(), amplitude=0.5, scale=6.0)

  # 2. A sphere covered in raised bumps (triplanar wraps the texture around it).
  sphere = proj.add_object(Pos(40, 0, 0) * Sphere(12), name="2 Bumpy sphere")
  sphere.parts[0].apply_texture(dots(), amplitude=0.6, scale=8.0)

  # 3. A block with ridged stripes.
  block = proj.add_object(Pos(75, 0, 0) * Box(20, 20, 20), name="3 Ridged block")
  block.parts[0].apply_texture(stripes(), amplitude=0.4, scale=7.0)

  # 4. Per-face texturing: stripes on top, a knurled grip on one side wall, the
  #    rest left smooth. Two apply_texture calls, each targeting chosen faces.
  panel_shape = Pos(110, 0, 0) * Box(20, 20, 20)
  panel = proj.add_object(panel_shape, name="4 Per-face panel")
  panel.parts[0].apply_texture(
    stripes(), faces=panel_shape.faces().sort_by(Axis.Z)[-1], amplitude=0.5, scale=5.0
  )
  panel.parts[0].apply_texture(
    knurl(), faces=panel_shape.faces().sort_by(Axis.X)[-1], amplitude=0.4, scale=5.0
  )

  out = proj.save("texture.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()
