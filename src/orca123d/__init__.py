"""orca123d -- turn build123d models into OrcaSlicer project (.3mf) files.

v1 writes "model-only" projects: geometry plus per-object/per-part settings in
``Metadata/model_settings.config``, and no ``project_settings.config``. OrcaSlicer
opens these using whatever printer/filament/print presets are currently active and
overlays the per-object settings we ship.
"""

from . import print_settings as _print_settings
from .paint import EnforcerBlockerType
from .print_settings import *  # noqa: F403  -- PrintSettings + the print-setting enums
from .project import ModelObject, Part, PartSubtype, Project
from .texture import ProjectionMode

__all__ = [
  "EnforcerBlockerType",
  "ModelObject",
  "Part",
  "PartSubtype",
  "ProjectionMode",
  "Project",
]
__all__ += _print_settings.__all__
