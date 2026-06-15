"""Assemble the .3mf (an OPC/zip package) from its parts.

OrcaSlicer's importer locates config files by their path inside the zip rather
than via OPC relationships, so a minimal package is: the OPC boilerplate
(``[Content_Types].xml`` + ``_rels/.rels``), the geometry, and the optional
``model_settings.config``. The boilerplate strings mirror what OrcaSlicer writes
(``_add_content_types_file_to_archive`` / ``_add_relationships_file_to_archive``).
"""

import zipfile
from os import PathLike
from pathlib import Path

CONTENT_TYPES_PATH = "[Content_Types].xml"
RELS_PATH = "_rels/.rels"
MODEL_PATH = "3D/3dmodel.model"
MODEL_SETTINGS_PATH = "Metadata/model_settings.config"
LAYER_HEIGHTS_PROFILE_PATH = "Metadata/layer_heights_profile.txt"

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""


def write_3mf(
  path: str | PathLike[str],
  model_xml: str,
  model_settings_xml: str | None = None,
  layer_heights_profile: str | None = None,
) -> Path:
  """Write a .3mf to ``path`` and return it."""
  path = Path(path)
  with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr(CONTENT_TYPES_PATH, CONTENT_TYPES_XML)
    archive.writestr(RELS_PATH, RELS_XML)
    archive.writestr(MODEL_PATH, model_xml)
    if model_settings_xml is not None:
      archive.writestr(MODEL_SETTINGS_PATH, model_settings_xml)
    if layer_heights_profile is not None:
      archive.writestr(LAYER_HEIGHTS_PROFILE_PATH, layer_heights_profile)
  return path
