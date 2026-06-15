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

from .project import ResolvedObject

_XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _metadata(parent: ET.Element, key: str, value: str) -> None:
  ET.SubElement(parent, "metadata", {"key": key, "value": value})


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

  ET.indent(config, space="  ")
  return _XML_DECLARATION + ET.tostring(config, encoding="unicode") + "\n"
