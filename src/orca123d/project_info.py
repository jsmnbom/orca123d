"""Project-level design metadata for an OrcaSlicer .3mf.

These fields ride as plain ``<metadata name="...">`` children of ``<model>`` in
``3D/3dmodel.model`` -- the same place the ``Application`` tag goes -- so they
need no ``project_settings.config`` and stay within a model-only file. OrcaSlicer
reads them unconditionally (``_handle_start_model_metadata`` in ``bbs_3mf.cpp``)
into its ``model_info`` / ``design_info``, where they surface in the Project and
Auxiliaries panels.

Each field carries a ``serialization_alias`` naming the 3MF metadata key it maps
to, so :meth:`ProjectInfo.metadata_items` is just ``model_dump(by_alias=True)``.
Any other metadata key OrcaSlicer should carry is passed as an extra field
(``extra="allow"``) and emitted verbatim.

Picture / Bill-of-Materials / Assembly-Guide attachments live as files under the
zip's ``Auxiliaries/`` tree instead and are out of scope here -- this covers the
text fields only.
"""

from collections.abc import Iterator
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["License", "ProjectInfo"]


class License(str, Enum):
  """The Creative Commons licenses OrcaSlicer offers in its License dropdown.

  OrcaSlicer stores the bare code (e.g. ``BY-SA``); a value outside this list is
  still written verbatim but shows as "no license" in the UI's fixed dropdown.
  """

  CC0 = "CC0"
  CC_BY = "BY"
  CC_BY_SA = "BY-SA"
  CC_BY_ND = "BY-ND"
  CC_BY_NC = "BY-NC"
  CC_BY_NC_SA = "BY-NC-SA"
  CC_BY_NC_ND = "BY-NC-ND"


class ProjectInfo(BaseModel):
  """Design metadata describing the whole project (model name, author, etc.).

  Every field is optional; only the ones you set are written. ``license`` accepts
  a :class:`License` member or a raw string. Any other 3MF ``<metadata>`` key can
  be supplied as an extra keyword (e.g. ``ProjectInfo(Origin="MakerWorld")``),
  which is written verbatim under that name.
  """

  model_config = ConfigDict(
    extra="allow",
    validate_assignment=True,
    use_enum_values=True,
    use_attribute_docstrings=True,
  )

  title: str | None = Field(default=None, serialization_alias="Title")
  """Display name of the model (3MF ``Title``)."""
  designer: str | None = Field(default=None, serialization_alias="Designer")
  """Author / designer name (3MF ``Designer``)."""
  description: str | None = Field(default=None, serialization_alias="Description")
  """Free-text description (3MF ``Description``)."""
  copyright: str | None = Field(default=None, serialization_alias="Copyright")
  """Copyright notice (3MF ``Copyright``)."""
  license: License | str | None = Field(default=None, serialization_alias="License")
  """License code -- a :class:`License` member or raw string (3MF ``License``)."""

  def metadata_items(self) -> Iterator[tuple[str, str]]:
    """Yield ``(metadata_name, value)`` for every field that is set.

    Typed fields come first under their 3MF names, then any extra keys in the
    order given (so an extra wins on a duplicate name, matching OrcaSlicer's
    last-write-wins read).
    """
    for name, value in self.model_dump(by_alias=True, exclude_none=True).items():
      yield name, str(value)
