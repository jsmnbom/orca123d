"""Tests for part subtypes (modifier / negative / support volumes)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from build123d import Box, Pos

from orca123d import PartSubtype, Project


def _parts(cfg: str) -> dict[str, str]:
  """Map each ``<part>`` name -> its ``subtype`` attribute."""
  root = ET.fromstring(cfg)
  out: dict[str, str] = {}
  for part in root.findall(".//part"):
    name = part.find("metadata[@key='name']").get("value")
    out[name] = part.get("subtype")
  return out


def test_partsubtype_values_match_orcaslicer():
  # The strings OrcaSlicer's ModelVolumeType serializes to in model_settings.
  assert PartSubtype.NORMAL.value == "normal_part"
  assert PartSubtype.NEGATIVE.value == "negative_part"
  assert PartSubtype.MODIFIER.value == "modifier_part"
  assert PartSubtype.SUPPORT_ENFORCER.value == "support_enforcer"
  assert PartSubtype.SUPPORT_BLOCKER.value == "support_blocker"


def test_add_part_subtypes_written_to_config(tmp_path):
  from orca123d.model_settings import build_model_settings_xml

  proj = Project()
  obj = proj.add_object(name="Bracket")
  obj.add_part(Box(10, 10, 10), name="Body")
  obj.add_part(Pos(0, 0, 8) * Box(6, 6, 6), name="Pocket", subtype=PartSubtype.NEGATIVE)
  obj.add_part(Box(4, 4, 12), name="Core", subtype=PartSubtype.MODIFIER)

  cfg = build_model_settings_xml(proj._resolve(0.1, 0.5))

  assert _parts(cfg) == {
    "Body": "normal_part",  # default
    "Pocket": "negative_part",
    "Core": "modifier_part",
  }


def test_add_object_subtype_applies_to_single_part(tmp_path):
  from orca123d.model_settings import build_model_settings_xml

  proj = Project()
  proj.add_object(Box(10, 10, 10), name="Blocker", subtype=PartSubtype.SUPPORT_BLOCKER)

  cfg = build_model_settings_xml(proj._resolve(0.1, 0.5))
  assert _parts(cfg) == {"Blocker": "support_blocker"}
