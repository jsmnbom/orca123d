"""Writer for ``3D/3dmodel.model`` -- the geometry part of an OrcaSlicer .3mf.

Each part becomes a mesh ``<object>``; each model object becomes a ``<components>``
object grouping its parts; each model object gets one ``<build>`` ``<item>``.

The ``Application`` metadata is deliberately generic (it must *not* start with
``BambuStudio-`` or ``OrcaSlicer-``). That makes OrcaSlicer classify the file as
``En3mfType::From_Other`` and import it silently, instead of popping a "generated
by BambuStudio, loading geometry data only" notice. ``model_settings.config`` is
still honored -- the importer finds it by path, not by the bbl/orca flag.

Painting (seam/support/color/fuzzy-skin) is carried as per-``<triangle>``
attributes (e.g. ``paint_seam``). The importer parses these unconditionally for
every triangle (``_handle_start_triangle`` in ``bbs_3mf.cpp``), so the generic
``From_Other`` file honors them too -- no need for an OrcaSlicer-tagged file.
"""

from .project import ResolvedObject

CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
BAMBU_NS = "http://schemas.bambulab.com/package/2021"
# Generic on purpose -- see the module docstring. Must NOT start with
# "BambuStudio-" or "OrcaSlicer-", or OrcaSlicer shows a vendor load notice.
APPLICATION = "orca123d-0.1.0"
BBS_3MF_VERSION = "1"

# 3MF transform attr: 3x3 rotation (row-major) followed by translation.
IDENTITY_TRANSFORM = "1 0 0 0 1 0 0 0 1 0 0 0"


def _f(value: float) -> str:
  return f"{value:.6f}"


def _transform(translate: tuple[float, float, float]) -> str:
  tx, ty, tz = translate
  return f"1 0 0 0 1 0 0 0 1 {_f(tx)} {_f(ty)} {_f(tz)}"


def build_model_xml(resolved_objects: list[ResolvedObject]) -> str:
  """Render the 3dmodel.model XML for the resolved objects."""
  out: list[str] = []
  out.append('<?xml version="1.0" encoding="UTF-8"?>')
  out.append(
    f'<model unit="millimeter" xml:lang="en-US" '
    f'xmlns="{CORE_NS}" xmlns:BambuStudio="{BAMBU_NS}">'
  )
  out.append(f' <metadata name="Application">{APPLICATION}</metadata>')
  out.append(f' <metadata name="BambuStudio:3mfVersion">{BBS_3MF_VERSION}</metadata>')
  out.append(" <resources>")

  for obj in resolved_objects:
    # Mesh objects first, so the components object below references existing ids.
    for part in obj.parts:
      out.append(f'  <object id="{part.mesh_id}" type="model">')
      out.append("   <mesh>")
      out.append("    <vertices>")
      out.extend(
        f'     <vertex x="{_f(x)}" y="{_f(y)}" z="{_f(z)}"/>'
        for x, y, z in part.mesh.vertices
      )
      out.append("    </vertices>")
      out.append("    <triangles>")
      for i, (a, b, c) in enumerate(part.mesh.triangles):
        attrs = "".join(
          f' {attr}="{tri_map[i]}"'
          for attr, tri_map in part.paint.items()
          if i in tri_map
        )
        out.append(f'     <triangle v1="{a}" v2="{b}" v3="{c}"{attrs}/>')
      out.append("    </triangles>")
      out.append("   </mesh>")
      out.append("  </object>")

    # Components object grouping the parts into one printed object.
    out.append(f'  <object id="{obj.object_id}" type="model">')
    out.append("   <components>")
    out.extend(
      f'    <component objectid="{part.mesh_id}" transform="{IDENTITY_TRANSFORM}"/>'
      for part in obj.parts
    )
    out.append("   </components>")
    out.append("  </object>")

  out.append(" </resources>")
  out.append(" <build>")
  out.extend(
    f'  <item objectid="{obj.object_id}" transform="{_transform(obj.translate)}" '
    f'printable="1" auto_drop="1"/>'
    for obj in resolved_objects
  )
  out.append(" </build>")
  out.append("</model>")
  out.append("")
  return "\n".join(out)
