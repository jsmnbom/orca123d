"""Generate a model-only .3mf demoing every seam-paint region type.

Run with: uv run python examples/seam_paint.py
Then open seam_paint.3mf in OrcaSlicer and open the Seam painting gizmo. Each box
on the plate shows one way to select where the seam goes:

  1. a whole build123d Face      -> the seam is biased onto that entire face;
  2. a BuildSketch on a face     -> any 2D sketch becomes the painted area;
  3. an Edge                     -> a thin strip is painted within a few mm of the
                                    edge, on both adjacent faces (pins the seam to
                                    a corner -- the closest thing to a seam line);
  4. a solid (e.g. a Cylinder)   -> paint where the surface lies inside the solid,
                                    which naturally spans multiple faces.

enforce = "put the seam here", block = "keep the seam off here".
"""

from build123d import Axis, Box, BuildSketch, Circle, Cylinder, Pos

from orca123d import EnforcerBlockerType, Project


def main() -> None:
  proj = Project()

  # 1. Whole face: enforce the seam onto the entire left (-X) face.
  b1 = Box(20, 20, 10)
  proj.add_object(b1, name="1 Whole face").parts[0].paint_seam(
    b1.faces().sort_by(Axis.X)[0], mode=EnforcerBlockerType.ENFORCER
  )

  # 2. Sketch on a face: block the seam from a circular patch on the top.
  b2 = Pos(30, 0, 0) * Box(20, 20, 10)
  with BuildSketch(b2.faces().sort_by(Axis.Z)[-1]) as patch:
    Circle(4)
  proj.add_object(b2, name="2 Sketched patch").parts[0].paint_seam(
    patch.sketch, mode=EnforcerBlockerType.BLOCKER
  )

  # 3. Edge: pin the seam to the +X/+Y vertical corner, painting a thin strip
  #    within 1.5 mm of the edge on both adjacent faces.
  b3 = Pos(60, 0, 0) * Box(20, 20, 10)
  corner = b3.edges().filter_by(Axis.Z).group_by(Axis.X)[-1].sort_by(Axis.Y)[-1]
  proj.add_object(b3, name="3 Edge strip").parts[0].paint_seam(
    corner, mode=EnforcerBlockerType.ENFORCER, within=1.5, max_depth=6
  )

  # 4. Solid: a vertical cylinder centred on the +X/+Y corner of b4 (world edge
  #    at x=100, y=10) enforces a rounded swath across both corner faces.
  b4 = Pos(90, 0, 0) * Box(20, 20, 10)
  tool = Pos(100, 10, 0) * Cylinder(radius=5, height=24)
  proj.add_object(b4, name="4 Corner cylinder").parts[0].paint_seam(
    tool, mode=EnforcerBlockerType.ENFORCER
  )

  out = proj.save("seam_paint.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()
