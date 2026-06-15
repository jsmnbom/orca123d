# orca123d

Turn [build123d](https://github.com/gumyr/build123d) models into [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) project (`.3mf`) files — geometry **plus** per-object and per-part slicer settings, painted regions, variable layer height, and baked-in surface textures — straight from Python.

You design parametrically in build123d, then describe how each object should be printed in code. `orca123d` tessellates the shapes and writes a `.3mf` you open directly in OrcaSlicer, with your overrides already applied.

```python
from build123d import Box, Cylinder, Pos
from orca123d import Project, PrintSettings

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

- **Objects and parts** — a `Project` holds objects; each object is one or more parts ("volumes" in OrcaSlicer). Parts carry an extruder assignment and a `subtype` (`NORMAL`, `MODIFIER`, `SUPPORT_ENFORCER`, `SUPPORT_BLOCKER`).
- **Typed print settings** — `PrintSettings` is a pydantic model generated from OrcaSlicer's own definitions, covering the slicer's *Print* tab. Every field is optional, so an instance is a sparse set of overrides; values are validated/coerced to OrcaSlicer's string form, and unknown keys pass through. Attach settings per object or per part.
- **Seam painting** — `part.paint_seam(region, ...)` biases (or blocks) the seam using build123d geometry as the selector: a whole **face**, a 2D **sketch** on a face, an **edge/wire** (paint within N mm), or a **solid** (paint where the surface lies inside it).
- **Fuzzy-skin painting** — `part.paint_fuzzy_skin(region, ...)` enables/disables fuzzy skin over the same kinds of regions.
- **Variable layer height** — `object.optimize_layer_height(faces, ...)` prints the z-span of chosen faces at a finer layer height (ramping in and out smoothly), the same result as OrcaSlicer's "Adaptive" button but driven by exactly the faces you hand it. `set_layer_height_profile(...)` is the low-level escape hatch.
- **Surface texturing** — `part.apply_texture(heightmap, ...)` bakes a grayscale heightmap into the part as **real** surface relief: the mesh is adaptively subdivided and its vertices displaced along their normals (white pushes out, black pushes in). Triplanar projection by default; restrict to selected faces, or call it more than once for different textures.
- **Preview** — `project.to_compound()` builds a build123d `Compound` mirroring the project tree (objects → parts), with textured parts shown as their displaced meshes (exactly what `save()` exports). Hand it to `ocp_vscode.show()` to preview in the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) VS Code extension, or to build123d's exporters.

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
obj.add_part(rib,  name="Rib", settings=PrintSettings(sparse_infill_density="100%"))
obj.add_part(cut,  name="Pocket", subtype=PartSubtype.MODIFIER)
```

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

### Variable layer height

```python
from build123d import GeomType

obj = proj.add_object(block, name="Filleted block")
curved = block.faces().filter_by(GeomType.PLANE, reverse=True)
obj.optimize_layer_height(curved, base_height=0.2, min_layer_height=0.08)
```

### Surface texture

```python
obj = proj.add_object(Box(20, 20, 20), name="Knurled cube")
obj.parts[0].apply_texture(heightmap, amplitude=0.5, scale=6.0)
```

> Texturing and painting can't be combined on the *same* part — subdivision invalidates painted triangles — so split the geometry into separate parts if you need both.

## Examples

Runnable scripts live in [`examples/`](examples/); each writes a `.3mf` to open in OrcaSlicer:

| Example | Shows |
| --- | --- |
| `examples/basic.py` | objects, multi-part volumes, per-object/part settings |
| `examples/seam_paint.py` | every seam-paint region type (face / sketch / edge / solid) |
| `examples/fuzzy_skin_paint.py` | fuzzy-skin painting region types |
| `examples/variable_layer_height.py` | adaptive layer height from selected faces |
| `examples/texture.py` | baked-in surface textures, including per-face |

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
