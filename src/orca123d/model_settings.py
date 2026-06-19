"""Writer for ``Metadata/model_settings.config`` -- per-object/per-part settings.

OrcaSlicer matches a ``<part id="P">`` to a volume by ``id`` == the mesh object id
referenced by the corresponding ``<component>`` in ``3dmodel.model`` (see
``_generate_volumes_new`` in ``bbs_3mf.cpp``). So a part's ``id`` here must equal
its mesh object id, and an object's ``id`` must equal its components-object id.

This file carries user-supplied names and setting values, so it is built with a
real XML library (``xml.etree.ElementTree``) which escapes attribute content for
us, rather than hand-rolled strings.
"""

import xml.etree.ElementTree as ET

import numpy as np

from .model_xml import _f
from .project import ResolvedObject

_XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _metadata(parent: ET.Element, key: str, value: str) -> None:
  ET.SubElement(parent, "metadata", {"key": key, "value": value})


def _assemble_transform(obj: ResolvedObject) -> str:
  """Assemble-View transform restoring the object to its design position.

  OrcaSlicer re-centers every imported object's mesh on its own bounding-box
  center (recording the discarded offset as ``source_offset_*``) and applies the
  assemble transform to that *re-centered* geometry. So the translation must be
  the object's design bounding-box center to put it back where it was designed;
  an identity transform would instead leave every object whose center is off the
  origin at the world origin (then dropped to the bed). The linear part stays
  identity -- any design rotation is already baked into the mesh vertices.
  """
  verts = np.concatenate([part.mesh.vertices for part in obj.parts])
  cx, cy, cz = (verts.min(axis=0) + verts.max(axis=0)) / 2.0
  return f"1 0 0 0 1 0 0 0 1 {_f(cx)} {_f(cy)} {_f(cz)}"


def build_model_settings_xml(resolved_objects: list[ResolvedObject]) -> str:
  """Render the model_settings.config XML for the resolved objects."""
  config = ET.Element("config")
  for obj in resolved_objects:
    obj_el = ET.SubElement(config, "object", {"id": str(obj.object_id)})
    _metadata(obj_el, "name", obj.name)
    for key, value in obj.settings.items():
      _metadata(obj_el, key, value)
    for part in obj.parts:
      part_el = ET.SubElement(
        obj_el, "part", {"id": str(part.mesh_id), "subtype": part.subtype.value}
      )
      _metadata(part_el, "name", part.name)
      if part.extruder is not None:
        _metadata(part_el, "extruder", str(part.extruder))
      for key, value in part.settings.items():
        _metadata(part_el, key, value)

  # Assembly View: pin every object back to its design (mesh) coordinates so the
  # Assembly View shows the assembled layout while the print bed uses the
  # per-object print_location. The assemble transform's translation is the
  # object's design bounding-box center -- NOT identity -- because OrcaSlicer
  # re-centers each imported mesh on that center (see _assemble_transform), so
  # identity would collapse every off-origin object onto the world origin.
  # This block is only needed once any object is placed for print: OrcaSlicer
  # otherwise copies each instance's *print* transform into its assemble
  # transform, and that transform has been group-centered and dropped to the bed
  # -- so a placed object would not line up with an unplaced one. With no placed
  # objects every instance is shifted by the same vector, so the copied
  # transforms stay aligned and no <assemble> block is required.
  if any(obj.print_location is not None for obj in resolved_objects):
    assemble_el = ET.SubElement(config, "assemble")
    for obj in resolved_objects:
      ET.SubElement(
        assemble_el,
        "assemble_item",
        {
          "object_id": str(obj.object_id),
          "instance_id": "0",
          "transform": _assemble_transform(obj),
          "offset": "0 0 0",
        },
      )

  ET.indent(config, space="  ")
  return _XML_DECLARATION + ET.tostring(config, encoding="unicode") + "\n"
