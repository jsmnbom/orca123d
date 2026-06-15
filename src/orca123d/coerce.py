"""Pydantic-native serialization of setting values into OrcaSlicer's on-disk strings.

OrcaSlicer stores every config value as a string. Rather than convert values by
hand, each setting's *type* carries a pydantic serializer (attached via
:data:`typing.Annotated`), so that ``PrintSettings.model_dump()`` already yields
the exact strings OrcaSlicer writes to a project file. This module defines those
annotated type aliases and the serializer functions behind them; the generated
:mod:`orca123d.print_settings` model is assembled entirely from them.

Each alias also gives pydantic the Python type to *validate/coerce into* on input
(e.g. ``"0.2"`` -> ``0.2``, ``1`` -> ``True``), so the model is the single source
of truth for both directions.

:func:`coerce_generic` is the fallback for unknown ("extra") keys, whose co_type
the schema doesn't know.
"""

import enum
from collections.abc import Callable, Iterable
from typing import Annotated, Any

from pydantic import PlainSerializer

LIST_SEP = ","
POINT_SEP = ";"


def _num(value: Any) -> str:
  """Format a number the way OrcaSlicer does -- no spurious trailing ``.0``."""
  if isinstance(value, bool):
    return "1" if value else "0"
  f = float(value)
  return str(int(f)) if f.is_integer() else repr(f)


def _bool(value: Any) -> str:
  return "1" if value else "0"


def _int(value: Any) -> str:
  return str(int(value))


def _percent(value: Any) -> str:
  if isinstance(value, str):
    return value if value.endswith("%") else f"{value}%"
  return f"{_num(value)}%"


def _float_or_percent(value: Any) -> str:
  return value if isinstance(value, str) else _num(value)


def _point(value: Any) -> str:
  x, y = value
  return f"{_num(x)},{_num(y)}"


def _enum(value: Any) -> str:
  return str(value.value) if isinstance(value, enum.Enum) else str(value)


def _joined(
  item: Callable[[Any], str], sep: str = LIST_SEP
) -> Callable[[Iterable[Any]], str]:
  """Wrap a scalar serializer into one that joins a sequence with ``sep``."""

  def serialize(values: Iterable[Any]) -> str:
    return sep.join(item(v) for v in values)

  return serialize


def _ser(func: Callable[[Any], str]) -> PlainSerializer:
  return PlainSerializer(func, return_type=str, when_used="always")


# --- scalar setting types -------------------------------------------------
# Each is the Python type pydantic coerces input into, annotated with the
# serializer that renders it back to OrcaSlicer's string form.
Bool = Annotated[bool, _ser(_bool)]
Int = Annotated[int, _ser(_int)]
Float = Annotated[float, _ser(_num)]
Str = Annotated[str, _ser(str)]
Percent = Annotated[float | str, _ser(_percent)]
FloatOrPercent = Annotated[float | str, _ser(_float_or_percent)]
Point = Annotated[tuple[float, float], _ser(_point)]

# Serializer metadata for enum fields. The enum class itself is generated
# per-schema, so scalar coEnum fields are typed ``Annotated[SomeEnum, EnumValue]``
# and repeated coEnums fields ``Annotated[list[SomeEnum], EnumValues]``.
EnumValue = _ser(_enum)
EnumValues = _ser(_joined(_enum))

# --- vector setting types -------------------------------------------------
Bools = Annotated[list[bool], _ser(_joined(_bool))]
Ints = Annotated[list[int], _ser(_joined(_int))]
Floats = Annotated[list[float], _ser(_joined(_num))]
Strs = Annotated[list[str], _ser(_joined(str))]
Percents = Annotated[list[float | str], _ser(_joined(_percent))]
FloatsOrPercents = Annotated[list[float | str], _ser(_joined(_float_or_percent))]
Points = Annotated[list[tuple[float, float]], _ser(_joined(_point, POINT_SEP))]


def coerce_generic(value: Any) -> str:
  """Best-effort serialization for unknown keys whose co_type we don't know."""
  if isinstance(value, bool):
    return _bool(value)
  if isinstance(value, enum.Enum):
    return str(value.value)
  if isinstance(value, float):
    return _num(value)
  if isinstance(value, Iterable) and not isinstance(value, str):
    return LIST_SEP.join(coerce_generic(v) for v in value)
  return str(value)
