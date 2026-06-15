"""Generate ``orca123d/print_settings.py`` from the vendored ``print.proto``.

Run with::

    uv run python -m orca123d._proto.codegen

The proto is OrcaSlicer's canonical print/process config schema (PR #13880). Each
field's name is the OrcaSlicer config key; its options carry the type hint,
defaults and (for enums) the allowed values and their display labels. We emit a
pydantic model whose fields are all optional, so only the keys a user explicitly
sets are serialized (sparse per-object overrides).

Serialization is delegated entirely to pydantic: every field is typed with one of
the :mod:`orca123d.coerce` annotated aliases, which carries a ``PlainSerializer``
that renders the value to OrcaSlicer's on-disk string. Enum-valued options become
real :class:`enum.Enum` classes (one per distinct value set).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

PRINT_PROTO_FILE = Path(__file__).parent / "print.proto"
OUTPUT_FILE = Path(__file__).parent.parent / "print_settings.py"

# print.proto's message mixes in machine-limit / kinematics / metadata keys; we
# keep only the fields that live on the slicer's "Print" tab -- the actual
# process settings a user overrides per object.
TAB_TYPE = "Print"

FIELD_RE = re.compile(r"^\s*(repeated\s+)?(\w+)\s+(\w+)\s*=\s*(\d+)\s*(\[|;)")
OPT_RE = re.compile(r"^\s*\((\w+)\)\s*=\s*(.+?)\s*$")
# enum_keys_map_ref looks like "ConfigOptionEnum<TimelapseType>::get_enum_values()"
ENUM_REF_RE = re.compile(r"<\s*([\w:]+)\s*>")
LIST_OPTS = {
  "enum_value_entries",
  "enum_label_entries",
  "invalidates",
  "list_membership",
}

# proto base type -> scalar co_type when no (co_type_hint) override is present
BASE_CO_TYPE = {
  "bool": "coBool",
  "int32": "coInt",
  "int64": "coInt",
  "uint32": "coInt",
  "float": "coFloat",
  "double": "coFloat",
  "string": "coString",
  "FloatOrPercent": "coFloatOrPercent",
  "Point2D": "coPoint",
}

# co_type -> the annotated alias in orca123d.coerce that types the field and
# carries its serializer. Enum co_types are handled separately (see annotation_of).
COERCE_ALIAS = {
  "coBool": "coerce.Bool",
  "coInt": "coerce.Int",
  "coFloat": "coerce.Float",
  "coString": "coerce.Str",
  "coPercent": "coerce.Percent",
  "coFloatOrPercent": "coerce.FloatOrPercent",
  "coPoint": "coerce.Point",
  "coBools": "coerce.Bools",
  "coInts": "coerce.Ints",
  "coFloats": "coerce.Floats",
  "coStrings": "coerce.Strs",
  "coPercents": "coerce.Percents",
  "coFloatOrPercents": "coerce.FloatsOrPercents",
  "coPoints": "coerce.Points",
}


@dataclass
class ProtoField:
  name: str
  proto_type: str
  repeated: bool
  opts: dict[str, object] = field(default_factory=dict)


@dataclass
class EnumDef:
  """A generated Python enum: a class name plus its ``(member, value)`` pairs."""

  name: str
  members: list[tuple[str, str]]


def _strip(raw: str) -> str:
  raw = raw.strip().rstrip(",").strip()
  if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
    return raw[1:-1]
  return raw


def parse(text: str) -> list[ProtoField]:
  fields: list[ProtoField] = []
  lines = text.splitlines()
  i = 0
  while i < len(lines):
    m = FIELD_RE.match(lines[i])
    if not m:
      i += 1
      continue
    pf = ProtoField(name=m.group(3), proto_type=m.group(2), repeated=bool(m.group(1)))
    if m.group(5) == "[":  # has an options block spanning following lines
      i += 1
      while i < len(lines) and "];" not in lines[i]:
        om = OPT_RE.match(lines[i].rstrip().rstrip(","))
        if om:
          _record_opt(pf, om.group(1), _strip(om.group(2)))
        i += 1
    fields.append(pf)
    i += 1
  return fields


def _record_opt(pf: ProtoField, key: str, value: str) -> None:
  if key in LIST_OPTS:
    cast("list[str]", pf.opts.setdefault(key, [])).append(value)
  else:
    pf.opts[key] = value


def co_type_of(pf: ProtoField) -> str:
  hint = pf.opts.get("co_type_hint")
  if isinstance(hint, str):
    return hint
  base = BASE_CO_TYPE[pf.proto_type]
  return base + "s" if pf.repeated else base


# --- enums ----------------------------------------------------------------


def _opt_str(pf: ProtoField, key: str) -> str | None:
  value = pf.opts.get(key)
  return value if isinstance(value, str) else None


def _opt_list(pf: ProtoField, key: str) -> list[str]:
  return cast("list[str]", pf.opts.get(key, []))


def _cpp_enum_name(pf: ProtoField) -> str | None:
  """The C++ enum type backing this field, e.g. ``TimelapseType``."""
  ref = _opt_str(pf, "enum_keys_map_ref")
  if ref and (m := ENUM_REF_RE.search(ref)):
    return m.group(1).split("::")[-1]
  return None


def _pascal(name: str) -> str:
  parts = [p for p in re.split(r"[^0-9a-zA-Z]+", name) if p]
  out = "".join(p[:1].upper() + p[1:] for p in parts)
  return f"_{out}" if out[:1].isdigit() else out


def _member_name(label: str, value: str) -> str:
  """A valid uppercase Python identifier for an enum member, from its label."""
  for source in (label, value):
    ident = re.sub(r"[^0-9a-zA-Z]+", "_", source).strip("_").upper()
    if not ident:
      continue
    if ident[0].isdigit():
      # Identifiers can't start with a digit; rotate leading numeric words to
      # the end ("3D Honeycomb" -> HONEYCOMB_3D) rather than prefix underscores.
      parts = ident.split("_")
      lead = [p for p in parts if p[0].isdigit()]
      rest = [p for p in parts if not p[0].isdigit()]
      ident = "_".join(rest + lead)
      if not ident or ident[0].isdigit():  # all-numeric, no word to lead with
        ident = f"_{ident}"
    return ident
  return "UNNAMED"


def _members(values: list[str], labels: list[str]) -> list[tuple[str, str]]:
  members: list[tuple[str, str]] = []
  used: set[str] = set()
  # Labels and values line up positionally; labels may be missing/shorter, in
  # which case we name the member after its value instead.
  for value, label in zip(values, labels + [""] * (len(values) - len(labels))):
    name = base = _member_name(label, value)
    n = 2
    while name in used:
      name, n = f"{base}_{n}", n + 1
    used.add(name)
    members.append((name, value))
  return members


def build_enums(fields: list[ProtoField]) -> tuple[list[EnumDef], dict[str, str]]:
  """Plan the enum classes to emit and which class each field is typed with.

  An enum field's allowed values come from ``enum_value_entries`` (the strings
  written to disk) paired with ``enum_label_entries`` (display names we turn into
  member names). Fields that share an identical value/label set share one class.
  A class is named after its C++ enum (``BrimType``); when one C++ enum is used
  with *different* value sets (e.g. ``InfillPattern`` per surface), each variant
  is named after the first field that uses it to keep names unambiguous.
  """
  enum_fields = [
    f
    for f in fields
    if co_type_of(f) in ("coEnum", "coEnums") and _opt_list(f, "enum_value_entries")
  ]

  signatures: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
  cpp_sigs: dict[str, set[tuple[tuple[str, ...], tuple[str, ...]]]] = {}
  for f in enum_fields:
    sig = (
      tuple(_opt_list(f, "enum_value_entries")),
      tuple(_opt_list(f, "enum_label_entries")),
    )
    signatures[f.name] = sig
    cpp_sigs.setdefault(_cpp_enum_name(f) or _pascal(f.name), set()).add(sig)

  defs: dict[tuple[tuple[str, ...], tuple[str, ...]], EnumDef] = {}
  field_enum: dict[str, str] = {}
  taken: set[str] = set()
  for f in enum_fields:
    sig = signatures[f.name]
    if sig in defs:
      field_enum[f.name] = defs[sig].name
      continue
    cpp = _cpp_enum_name(f) or _pascal(f.name)
    name = base = cpp if len(cpp_sigs[cpp]) == 1 else _pascal(f.name)
    n = 2
    while name in taken:  # different value set wants a name we've already used
      name, n = f"{base}_{n}", n + 1
    taken.add(name)
    defs[sig] = EnumDef(name, _members(list(sig[0]), list(sig[1])))
    field_enum[f.name] = name
  return list(defs.values()), field_enum


def annotation_of(pf: ProtoField, field_enum: dict[str, str]) -> str:
  """The field's optional type annotation, e.g. ``coerce.Float | None``."""
  co = co_type_of(pf)
  if co in ("coEnum", "coEnums"):
    cls = field_enum.get(pf.name)
    if cls is None:  # enum whose values live only in C++ -> accept any string
      inner = "coerce.Strs" if co == "coEnums" else "coerce.Str"
    elif co == "coEnums":
      inner = f"Annotated[list[{cls}], coerce.EnumValues]"
    else:
      inner = f"Annotated[{cls}, coerce.EnumValue]"
  else:
    inner = COERCE_ALIAS[co]
  return f"{inner} | None"


# --- emission -------------------------------------------------------------

HEADER = '''"""Typed OrcaSlicer print (process) settings.

GENERATED from print.proto -- do not edit by hand. Regenerate with::

    uv run python -m orca123d._proto.codegen

Covers the keys on the slicer's "Print" tab. Every field is optional; only the
keys you set are written to a project file, so an instance represents a sparse
set of per-object/per-part overrides. Unknown keys are accepted too
(``extra="allow"``) and passed through verbatim.

Values are validated/coerced by pydantic on input and serialized to OrcaSlicer's
string form on output (see :mod:`orca123d.coerce`); enum-valued options use the
generated :class:`~enum.Enum` classes below.
"""

from collections.abc import Iterator
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict

from . import coerce

'''

MODEL_OPEN = '''
class PrintSettings(BaseModel):
  """A sparse set of OrcaSlicer print (process) settings."""

  model_config = ConfigDict(
    extra="allow",
    validate_assignment=True,
    use_attribute_docstrings=True,
  )

'''

METHODS = '''
  def items(self) -> Iterator[tuple[str, str]]:
    """Yield ``(key, serialized_value)`` for every explicitly-set setting.

    Mirrors ``dict.items()``: each value is rendered to the exact string
    OrcaSlicer stores on disk. Known fields are serialized by their pydantic
    type; unknown ("extra") keys fall back to a best-effort conversion.
    """
    known = type(self).model_fields
    for name, value in self.model_dump(exclude_unset=True, exclude_none=True).items():
      yield name, value if name in known else coerce.coerce_generic(value)
'''


def _docstring(pf: ProtoField) -> str | None:
  doc = pf.opts.get("tooltip") or pf.opts.get("full_label") or pf.opts.get("label")
  if not isinstance(doc, str) or not doc:
    return None
  # The proto encodes newlines/tabs as escaped sequences (e.g. "\\n"); turn them
  # into real whitespace so the docstring renders cleanly on hover.
  return doc.replace("\\\\n", "\n").replace("\\\\t", "\t")


def _triple_quoted(text: str, indent: str = "") -> str:
  """Emit ``text`` as a triple-quoted literal, with real newlines preserved."""
  body = text.replace("\\", "\\\\")  # keep stray backslashes literal
  body = body.replace('"""', '\\"\\"\\"')  # don't close the docstring early
  if body.endswith('"'):
    body = body[:-1] + '\\"'
  if "\n" in body:
    lines = "\n".join(indent + line if line else "" for line in body.splitlines())
    return f'"""\n{lines}\n{indent}"""'
  return f'"""{body}"""'


def _emit_all(enums: list[EnumDef]) -> str:
  """Emit the module's ``__all__`` -- every enum class plus ``PrintSettings``."""
  names = [e.name for e in enums] + ["PrintSettings"]
  body = "".join(f'  "{name}",\n' for name in names)
  return f"__all__ = [\n{body}]\n"


def _emit_enums(enums: list[EnumDef]) -> str:
  if not enums:
    return ""
  out = ["\n"]
  for e in enums:
    out.append(f"class {e.name}(str, Enum):\n")
    for member, value in e.members:
      out.append(f"  {member} = {value!r}\n")
    out.append("\n\n")
  return "".join(out)


def generate(fields: list[ProtoField]) -> str:
  enums, field_enum = build_enums(fields)
  out = [HEADER, _emit_all(enums), _emit_enums(enums), MODEL_OPEN]
  for pf in fields:
    out.append(f"  {pf.name}: {annotation_of(pf, field_enum)} = None\n")
    doc = _docstring(pf)
    if doc is not None:
      out.append(f"  {_triple_quoted(doc, indent='  ')}\n")
  out.append(METHODS)
  return "".join(out)


def main() -> None:
  fields = [
    f for f in parse(PRINT_PROTO_FILE.read_text()) if f.opts.get("tab_type") == TAB_TYPE
  ]
  OUTPUT_FILE.write_text(generate(fields))
  print(f"wrote {OUTPUT_FILE} ({len(fields)} fields)")


if __name__ == "__main__":
  main()
