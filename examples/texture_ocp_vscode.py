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
#%%
import numpy as np
from build123d import Axis, Box, Cylinder, GeomType, Pos, Sphere

from orca123d import Project
#%%

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
  from ocp_vscode import show, Render

  proj = Project()


  # a cylinder with dots on sides
  cyl = Cylinder(20, 40)
  cyl_obj = proj.add_object(cyl, name="cylinder with dots")
  cyl_obj.parts[0].apply_texture(
    knurl(), faces=cyl.faces().filter_by(GeomType.CYLINDER), amplitude=0.4, scale=10.0
  )

  show(proj.to_compound(), modes=[Render.FACES])

  out = proj.save("export/texture.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()

# %%
