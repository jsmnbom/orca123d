"""Generate a minimal model-only OrcaSlicer .3mf.

Run with: uv run python examples/basic.py
Then open basic.3mf in OrcaSlicer.
"""

from build123d import Box, Cylinder, Pos

from orca123d import Project, PrintSettings


def main() -> None:
  proj = Project()

  # A single-solid object with a per-object override.
  proj.add_object(Box(20, 20, 10), name="Base", settings=PrintSettings(wall_loops=4, sparse_infill_density="20%"))

  # A two-part object: body + pin, each on its own extruder. Positioned away
  # from the base in build123d coords -- relative layout is preserved on save.
  tag = proj.add_object(name="Two Color Tag")
  tag.add_part(Pos(0, 30, 0) * Box(30, 12, 3), name="Body", extruder=1)
  tag.add_part(
    Pos(10, 30, 1.5) * Cylinder(3, 4),
    name="Pin",
    extruder=2,
    settings=PrintSettings(sparse_infill_density="100%"),
  )

  out = proj.save("export/basic.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()
