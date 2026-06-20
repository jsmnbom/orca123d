"""Attach project-level design metadata (name, designer, license, ...).

Run with: uv run python examples/project_info.py
Then open export/project_info.3mf in OrcaSlicer and check the Project /
Auxiliaries panels for the title, designer, description and license.
"""

from build123d import Box, Cylinder, Pos

from orca123d import License, Project, ProjectInfo


def main() -> None:
  proj = Project(
    info=ProjectInfo(
      title="Two Color Tag",
      designer="Jas",
      description="A two-part name tag: body on extruder 1, pin on extruder 2.",
      copyright="(c) 2026 Jas",
      license=License.CC_BY_SA,  # or a raw string like "BY-NC"
    )
  )

  tag = proj.add_object(name="Two Color Tag")
  tag.add_part(Pos(0, 0, 0) * Box(30, 12, 3), name="Body", extruder=1)
  tag.add_part(Pos(10, 0, 1.5) * Cylinder(3, 4), name="Pin", extruder=2)

  out = proj.save("export/project_info.3mf")
  print(f"wrote {out}")


if __name__ == "__main__":
  main()
