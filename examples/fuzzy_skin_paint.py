"""Generate a model-only .3mf demoing fuzzy-skin painting region types.

Run with: uv run python examples/fuzzy_skin_paint.py
Then open fuzzy_skin_paint.3mf in OrcaSlicer and open the Fuzzy skin painting
gizmo. Each box on the plate shows one region type:

  1. a whole build123d Face      -> fuzzy skin on that entire face only;
  2. a BuildSketch on a face     -> fuzzy skin inside a circular patch;
  3. an Edge                     -> fuzzy strip within a few mm of the edge;
  4. a solid (e.g. a Cylinder)   -> fuzzy skin where the surface is inside the solid.

ENFORCER = "apply fuzzy skin here", BLOCKER = "suppress fuzzy skin here".
"""

from build123d import Axis, Box, BuildSketch, Circle, Cylinder, Pos

from orca123d import EnforcerBlockerType, Project, PrintSettings, FuzzySkinType


def main() -> None:
  proj = Project()

  # 1. Whole face: enable fuzzy skin on the entire front (+Y) face.
  b1 = Box(20, 20, 10)
  proj.add_object(
    b1,
    name="1 Whole face",
    settings=PrintSettings(fuzzy_skin=FuzzySkinType.PAINTED_ONLY),
  ).parts[0].paint_fuzzy_skin(
    b1.faces().sort_by(Axis.Y)[-1], mode=EnforcerBlockerType.ENFORCER
  )

  # 2. Sketch on a face: fuzzy skin inside a circular patch on the top.
  b2 = Pos(30, 0, 0) * Box(20, 20, 10)
  with BuildSketch(b2.faces().sort_by(Axis.Z)[-1]) as patch:
    Circle(6)
  proj.add_object(b2, name="2 Sketched patch").parts[0].paint_fuzzy_skin(
    patch.sketch, mode=EnforcerBlockerType.ENFORCER
  )

  # 3. Edge: fuzzy strip within 2 mm of the top front edge.
  b3 = Pos(60, 0, 0) * Box(20, 20, 10)
  top_front = b3.edges().filter_by(Axis.X).group_by(Axis.Z)[-1].sort_by(Axis.Y)[-1]
  proj.add_object(b3, name="3 Edge strip").parts[0].paint_fuzzy_skin(
    top_front, mode=EnforcerBlockerType.ENFORCER, within=2.0, max_depth=6
  )

  # 4. Solid: a cylinder centred on the +X/+Y corner applies fuzzy skin where
  #    the box surface lies inside it, naturally spanning both corner faces.
  b4 = Pos(90, 0, 0) * Box(20, 20, 10)
  tool = Pos(100, 10, 0) * Cylinder(radius=6, height=24)
  proj.add_object(b4, name="4 Corner cylinder").parts[0].paint_fuzzy_skin(
    tool, mode=EnforcerBlockerType.ENFORCER
  )

  out = proj.save("export/fuzzy_skin_paint.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()
