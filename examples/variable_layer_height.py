"""Generate a model-only .3mf demoing variable (adaptive) layer height.

Run with: uv run python examples/variable_layer_height.py
Then open variable_layer_height.3mf in OrcaSlicer and open the "Variable layer
height" gizmo (the layers ruler on the left). The straight side walls keep the
base 0.2 mm layers, while the rounded fillet on top is refined toward 0.08 mm
where its surface goes shallow -- the same result as the gizmo's "Adaptive"
button, but driven by exactly the faces we hand it.
"""

from build123d import Axis, Box, GeomType, fillet

from orca123d import Project


def main() -> None:
  proj = Project()

  # A 30x30x20 block with the top perimeter rounded over. The fillet is the
  # shallow, near-horizontal surface that benefits from finer layers.
  block = Box(30, 30, 20)
  block = fillet(block.edges().group_by(Axis.Z)[-1], radius=6)

  obj = proj.add_object(block, name="Filleted block")

  # The fillet faces are the only curved (non-planar) faces; hand them to
  # optimize_layer_height and their z-span prints at 0.08 mm, ramping from the
  # 0.2 mm base into the band (and back out) at most 0.04 mm per layer.
  fillet_faces = block.faces().filter_by(GeomType.PLANE, reverse=True)
  obj.optimize_layer_height(
    fillet_faces,
    base_height=0.2,
    min_layer_height=0.08,
  )

  out = proj.save("variable_layer_height.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()
