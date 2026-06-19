"""Decouple the assembled layout from the print layout.

Objects keep their build123d design coordinates as the *assembled* arrangement
(OrcaSlicer's Assembly View). A per-object ``print_location`` lays them out
differently *for printing* (the print bed). Preview either arrangement with
``Project.to_compound(layout=...)``.

Run with: uv run python examples/print_layout.py
Then open print_layout.3mf in OrcaSlicer and toggle the Assembly View.

On import OrcaSlicer may show "Multi-part object detected" because the base and
lid sit at different heights in the design -- choose **No** to keep them as
separate objects (Yes would merge them into one object and lose the print layout).
"""
#%%
from build123d import Box, Pos

from orca123d import Project


def main() -> None:
  proj = Project()

  # Assembled product (design coordinates): a base with a lid resting on top.
  # The base prints where it is designed; the lid is moved beside it for
  # printing, while the Assembly View still shows it seated on the base.
  proj.add_object(Box(40, 40, 10), name="Base")
  proj.add_object(
    Pos(0, 0, 6.5) * Box(40, 40, 3),  # seated on the base (top at z=5)
    name="Lid",
    print_location=Pos(50, 0, 0),  # printed 50 mm to the side
  )

  out = proj.save("export/print_layout.3mf")
  print(f"wrote {out}")

  # Optional preview (needs the 'preview' extra: uv sync --extra preview):
  # from ocp_vscode import show_object, reset_show
  # reset_show()
  # show_object(proj.to_compound(layout="assembly"), name="assembly")  # seated lid
  # show_object(proj.to_compound(layout="print"), name="print")     # spread out, bed-centered


if __name__ == "__main__":
  main()
