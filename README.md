# orca123d

Project to help when working with [build123d](https://github.com/gumyr/build123d) models in [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer). Generate `.3mf` files with geometry **plus** per-object and per-part slicer settings and painted regions — directly from Python.

```python
from build123d import Box, Cylinder, Pos
from orca123d import Project, PrintSettings

# Project is just a convenient wrapper around the 3MF structure: objects, parts, settings, and painted regions.
proj = Project()

# A single-solid object with a per-object override.
proj.add_object(Box(20, 20, 10), name="Base",
                settings=PrintSettings(wall_loops=4, sparse_infill_density="20%"))

# A two-part object: body + pin, each on its own extruder. Relative layout in
# build123d coords is preserved on save.
tag = proj.add_object(name="Two Color Tag")
tag.add_part(Pos(0, 30, 0) * Box(30, 12, 3), name="Body", extruder=1)
tag.add_part(Pos(10, 30, 1.5) * Cylinder(3, 4), name="Pin", extruder=2,
             settings=PrintSettings(sparse_infill_density="100%"))

proj.save("basic.3mf")  # open in OrcaSlicer
```

## What it does

`orca123d` writes **model-only** projects: geometry and per-object/per-part settings in `Metadata/model_settings.config`, with no `project_settings.config`. OrcaSlicer opens these using whatever printer / filament / print presets you currently have active, and overlays the settings shipped in the file. So you keep choosing the machine and filament in OrcaSlicer, while the model brings its own structure and overrides.

## Features

- **Objects and parts** — a `Project` holds objects; each object is one or more parts ("volumes" in OrcaSlicer). Parts carry an extruder assignment and a `subtype` (`NORMAL`, `NEGATIVE` to carve material away, `MODIFIER` to apply settings to an overlapping region, `SUPPORT_ENFORCER`, `SUPPORT_BLOCKER`). `add_object(shape, subtype=…)` sets it for a single-part object; `add_part(shape, subtype=…)` for each volume.
- **Typed print settings** — `PrintSettings` is a pydantic model generated from OrcaSlicer's own definitions, covering the slicer's *Print* tab. Every field is optional, so an instance is a sparse set of overrides; values are validated/coerced to OrcaSlicer's string form, and unknown keys pass through. Attach settings per object or per part.
- **Print layout vs. assembly view** — objects keep their build123d coordinates as the *assembled* arrangement (OrcaSlicer's Assembly View); an optional per-object `print_location` lays them out differently *for printing*. OrcaSlicer auto-centers the whole group on a single plate, so this sets the **relative** print layout, not absolute bed coordinates (model-only files import onto one plate — they can't split objects across plates).
- **Seam painting** — `part.paint_seam(region, ...)` biases (or blocks) the seam using build123d geometry as the selector: a whole **face**, a 2D **sketch** on a face, an **edge/wire** (paint within N mm), or a **solid** (paint where the surface lies inside it).
- **Fuzzy-skin painting** — `part.paint_fuzzy_skin(region, ...)` enables/disables fuzzy skin over the same kinds of regions.
- **Project info** — `Project(info=ProjectInfo(...))` attaches design metadata (`title`, `designer`, `description`, `copyright`, `license`) written as `<model>` metadata, which OrcaSlicer surfaces in its Project / Auxiliaries panels. `license` takes a `License` member (the CC options) or a raw string; any other 3MF metadata key can be passed as an extra keyword and is written verbatim.
- **Preview** — `project.to_compound()` builds a build123d `Compound` mirroring the project tree (objects → parts). Pass `layout="print"` to preview the bed layout (print locations applied, group bed-centered) instead of the default `"assembly"` view. Hand it to `ocp_vscode.show()` to preview in the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) VS Code extension, or to build123d's exporters.

## Install

Requires Python ≥ 3.13. Using [uv](https://github.com/astral-sh/uv):

```bash
uv sync                    # core
uv sync --extra dev        # + pytest and type stubs
uv sync --extra preview    # + ocp_vscode for previewing Project.to_compound()
```

## Usage by feature

### Multi-part objects and per-part settings

```python
from orca123d import PartSubtype, PrintSettings

obj = proj.add_object(name="Bracket")
obj.add_part(body, name="Body")
obj.add_part(rib,  name="Rib")
obj.add_part(core, name="Dense core", subtype=PartSubtype.MODIFIER,
             settings=PrintSettings(sparse_infill_density="100%"))  # 100% infill where it overlaps
obj.add_part(cut,  name="Pocket", subtype=PartSubtype.NEGATIVE)     # carves material away
```

### Project info

```python
from orca123d import License, Project, ProjectInfo

proj = Project(info=ProjectInfo(
    title="Two Color Tag",
    designer="Jas",
    description="A two-part name tag.",
    license=License.CC_BY_SA,        # or a raw string
    Origin="MakerWorld",             # any other 3MF metadata key, written verbatim
))
```

### Print layout vs. assembly view

```python
from build123d import Box, Pos

# Base prints where it's designed; the lid is moved aside for printing, but the
# Assembly View still shows it seated on the base.
proj.add_object(Box(40, 40, 10), name="Base")
proj.add_object(Pos(0, 0, 6.5) * Box(40, 40, 3), name="Lid",
                print_location=Pos(50, 0, 0))

proj.to_compound(layout="assembly")  # preview the assembled product
proj.to_compound(layout="print")     # preview the print bed (spread, centered)
```

> Model-only files always import onto a single, auto-centered plate, so
> `print_location` controls the *relative* bed layout (not absolute coordinates),
> and objects can't be split across multiple plates from a model-only file.

### Seam / fuzzy-skin painting

```python
from build123d import Axis, Box
from orca123d import EnforcerBlockerType

box = Box(20, 20, 10)
part = proj.add_object(box, name="Box").parts[0]

# Pin the seam to a vertical corner edge (paint within 1.5 mm of it).
corner = box.edges().filter_by(Axis.Z).sort_by(Axis.X)[-1]
part.paint_seam(corner, mode=EnforcerBlockerType.ENFORCER, within=1.5)
```

## Examples

Runnable scripts live in [`examples/`](examples/); each writes a `.3mf` to open in OrcaSlicer:

| Example | Shows |
| --- | --- |
| `examples/basic.py` | objects, multi-part volumes, per-object/part settings |
| `examples/print_layout.py` | assembled layout vs. print-bed layout (`print_location`) |
| `examples/seam_paint.py` | every seam-paint region type (face / sketch / edge / solid) |
| `examples/fuzzy_skin_paint.py` | fuzzy-skin painting region types |

```bash
uv run python examples/basic.py
```

## Development

```bash
uv run pytest      # tests live in tests/
uv run ruff check  # lint (2-space indent)
```

`PrintSettings` and its enums are generated from `src/orca123d/_proto/print.proto`. Regenerate with:

```bash
uv run python -m orca123d._proto.codegen
```
