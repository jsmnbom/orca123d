"""Public builder API: Project / ModelObject / Part, and Project.save()."""

import copy
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Literal

from build123d import Location
from build123d.topology import Compound, Shape

from .mesh import MeshData, tessellate_shape
from .paint import FUZZY_ATTR, SEAM_ATTR, EnforcerBlockerType, encode_region_paint
from .print_settings import PrintSettings
from .project_info import ProjectInfo

__all__ = ["ModelObject", "Part", "PartSubtype", "Project"]


@dataclass
class _PaintRequest:
  """A pending paint operation, evaluated against the mesh at resolve time."""

  attr: str  # the 3MF <triangle> attribute, e.g. "paint_seam"
  state: EnforcerBlockerType  # paint state to apply
  region: Shape | list[Shape]  # build123d solid / face / sketch / edge (or list)
  max_depth: int
  within: float  # edge proximity radius (mm); ignored for non-edge regions


class PartSubtype(str, Enum):
  """Per-part subtypes understood by OrcaSlicer (its ``ModelVolumeType``).

  ``NORMAL`` adds solid material; ``NEGATIVE`` carves it back out of the other
  parts in the same object; ``MODIFIER`` leaves the geometry alone but applies
  its own settings to whatever overlaps it; the two ``SUPPORT_*`` subtypes force
  support to be generated (``ENFORCER``) or suppressed (``BLOCKER``) in their
  volume. All but ``NORMAL`` only make sense alongside a normal part to act on.
  """

  NORMAL = "normal_part"
  NEGATIVE = "negative_part"
  MODIFIER = "modifier_part"
  SUPPORT_ENFORCER = "support_enforcer"
  SUPPORT_BLOCKER = "support_blocker"


class Part:
  """One build123d shape within a printed object (a "volume" in OrcaSlicer)."""

  def __init__(
    self,
    shape: "Shape",
    *,
    name: str,
    extruder: int | None = None,
    settings: PrintSettings | None = None,
    subtype: PartSubtype = PartSubtype.NORMAL,
  ) -> None:
    self.shape = shape
    self.name = name
    self.extruder = extruder
    self.subtype = subtype
    self.settings = settings or PrintSettings()
    self._paints: list[_PaintRequest] = []

  def __repr__(self) -> str:
    return f"Part(name={self.name!r}, subtype={self.subtype!r})"

  def paint_seam(
    self,
    region: Shape | list[Shape],
    *,
    mode: EnforcerBlockerType = EnforcerBlockerType.ENFORCER,
    max_depth: int = 5,
    within: float = 1.0,
  ) -> None:
    """Paint a seam region from build123d geometry.

    ``region`` (or a list of regions) selects where to paint:

    * a **solid** -- paint surface points inside it (spans multiple faces, e.g.
      a cylinder at a corner to bias the seam there);
    * a planar **face**/**sketch** -- a whole face, or a 2D region sketched on a
      face with ``BuildSketch``;
    * an **edge**/**wire** -- paint within ``within`` mm of the curve, the natural
      way to pin a seam to an edge.

    ``mode`` is an :class:`~orca123d.paint.EnforcerBlockerType`:
    ``ENFORCER`` biases the seam onto the region, ``BLOCKER`` keeps it away.
    Sketch/edge boundaries are approximated by subdividing boundary triangles up
    to ``max_depth`` times (higher = crisper edge, larger file).
    """
    self._paints.append(_PaintRequest(SEAM_ATTR, mode, region, max_depth, within))

  def paint_fuzzy_skin(
    self,
    region: Shape | list[Shape],
    *,
    mode: EnforcerBlockerType = EnforcerBlockerType.ENFORCER,
    max_depth: int = 5,
    within: float = 1.0,
  ) -> None:
    """Paint a fuzzy-skin region from build123d geometry.

    ``region`` selects where to paint (same kinds as :meth:`paint_seam`):

    * a **solid** -- paint surface points inside it;
    * a planar **face**/**sketch** -- a whole face or a 2D sketch region;
    * an **edge**/**wire** -- paint within ``within`` mm of the curve.

    ``mode`` is an :class:`~orca123d.paint.EnforcerBlockerType`:
    ``ENFORCER`` enables fuzzy skin on the region, ``BLOCKER`` disables it.
    """
    self._paints.append(_PaintRequest(FUZZY_ATTR, mode, region, max_depth, within))

  def _resolve(
    self, mesh_id: int, tolerance: float, angular_tolerance: float
  ) -> "ResolvedPart":
    mesh = tessellate_shape(self.shape, tolerance, angular_tolerance)
    return ResolvedPart(
      self, mesh_id=mesh_id, mesh=mesh, paint=self._compute_paint(mesh)
    )

  def _compute_paint(self, mesh: MeshData) -> dict[str, dict[int, str]]:
    """Evaluate pending paint requests against the tessellated mesh.

    Returns ``{attribute: {triangle_index: hex string}}``. For a given attribute,
    a later request wins on any triangle it shares with an earlier one.
    """
    if not self._paints:
      return {}
    model_faces = self.shape.faces()  # same order as mesh.face_ranges
    paint: dict[str, dict[int, str]] = {}
    for req in self._paints:
      result = encode_region_paint(
        mesh, model_faces, req.region, req.state, req.max_depth, within=req.within
      )
      paint.setdefault(req.attr, {}).update(result)
    return paint


class ResolvedPart(Part):
  """A Part that has been tessellated and assigned a 3MF mesh id."""

  def __init__(
    self,
    part: Part,
    *,
    mesh_id: int,
    mesh: MeshData,
    paint: dict[str, dict[int, str]] | None = None,
  ) -> None:
    super().__init__(
      part.shape,
      name=part.name,
      extruder=part.extruder,
      settings=part.settings,
      subtype=part.subtype,
    )
    self.mesh_id = mesh_id
    self.mesh = mesh
    # {attribute: {triangle_index: hex paint string}}, consumed by model_xml.
    self.paint: dict[str, dict[int, str]] = paint or {}


class ModelObject:
  """A printed object on the plate, made of one or more parts."""

  def __init__(
    self,
    *,
    name: str,
    settings: PrintSettings | None = None,
    print_location: Location | None = None,
  ) -> None:
    self.name = name
    self.settings = settings or PrintSettings()
    self.parts: list[Part] = []
    # Where this object is placed *for printing*, relative to its build123d
    # design coordinates. ``None`` prints at the design position (which is also
    # the assembled position). Set it to lay the object out for printing while
    # the Assembly View keeps the design arrangement -- see ``Project.save``.
    self.print_location = print_location

  def add_part(
    self,
    shape: "Shape",
    *,
    name: str | None = None,
    extruder: int | None = None,
    settings: PrintSettings | None = None,
    subtype: PartSubtype = PartSubtype.NORMAL,
  ) -> Part:
    """Add a sub-part (volume) to this object.

    When ``name`` is omitted, the shape's ``label`` is used if it has one,
    otherwise a name is generated from the object name and part index.
    """
    part = Part(
      shape,
      name=name or shape.label or f"{self.name} part {len(self.parts) + 1}",
      extruder=extruder,
      settings=settings,
      subtype=subtype,
    )
    self.parts.append(part)
    return part

  def __repr__(self) -> str:
    return f"ModelObject(name={self.name!r}, parts={len(self.parts)})"

  def _resolve(
    self, first_id: int, tolerance: float, angular_tolerance: float
  ) -> "ResolvedObject":
    if not self.parts:
      raise ValueError(f"Object {self.name!r} has no parts to export")
    resolved_parts = [
      part._resolve(first_id + i, tolerance, angular_tolerance)
      for i, part in enumerate(self.parts)
    ]
    return ResolvedObject(
      self, object_id=first_id + len(self.parts), parts=resolved_parts
    )


class ResolvedObject(ModelObject):
  """A ModelObject resolved with mesh ids and a plate translation."""

  def __init__(
    self, obj: ModelObject, *, object_id: int, parts: list[ResolvedPart]
  ) -> None:
    super().__init__(name=obj.name, settings=obj.settings)
    self.parts: list[ResolvedPart] = parts  # type: ignore[assignment]
    self.object_id = object_id
    self.print_location = obj.print_location


class Project:
  """A collection of objects exportable to an OrcaSlicer .3mf project file."""

  def __init__(self, info: ProjectInfo | None = None) -> None:
    self.objects: list[ModelObject] = []
    # Project-level design metadata (name, designer, license, ...). Written as
    # <model> metadata in 3dmodel.model; None writes none. See ProjectInfo.
    self.info = info

  def add_object(
    self,
    shape: "Shape | None" = None,
    *,
    name: str | None = None,
    extruder: int | None = None,
    settings: PrintSettings | None = None,
    subtype: PartSubtype = PartSubtype.NORMAL,
    print_location: Location | None = None,
  ) -> ModelObject:
    """Add an object. If ``shape`` is given it becomes the object's single part.

    When ``name`` is omitted, a given shape's ``label`` is used if it has one,
    otherwise a name is generated from the object index.

    ``extruder`` and ``subtype`` apply to that single part -- ``subtype`` is a
    :class:`PartSubtype` such as ``NEGATIVE`` or ``MODIFIER`` -- and are ignored
    when no ``shape`` is given (use :meth:`~ModelObject.add_part` per part
    instead). ``settings`` attaches to the *object* (so it cascades to every
    part), matching the multi-part workflow.

    ``print_location`` is a build123d ``Location``/``Pos``/``Rot`` placing the
    object *for printing*, applied on top of its design coordinates; the
    Assembly View still shows the object at its design position. ``None`` (the
    default) prints at the design position. See :meth:`save`.
    """
    if name is None and shape is not None and shape.label:
      name = shape.label
    obj = ModelObject(
      name=name or f"Object {len(self.objects) + 1}",
      settings=settings,
      print_location=print_location,
    )
    if shape is not None:
      obj.add_part(shape, name=obj.name, extruder=extruder, subtype=subtype)
    self.objects.append(obj)
    return obj

  def _resolve(
    self, tolerance: float, angular_tolerance: float
  ) -> list[ResolvedObject]:
    """Tessellate parts and assign 3MF ids.

    Part mesh ids are allocated before the object's components-object id so
    that, as in OrcaSlicer's own files, parts have lower ids than the object
    that references them.
    """
    resolved: list[ResolvedObject] = []
    next_id = 1
    for obj in self.objects:
      resolved_obj = obj._resolve(next_id, tolerance, angular_tolerance)
      next_id += len(obj.parts) + 1
      resolved.append(resolved_obj)
    return resolved

  def save(
    self,
    path: str | PathLike[str],
    *,
    tolerance: float = 0.01,
    angular_tolerance: float = 0.1,
  ) -> Path:
    """Tessellate and write a model-only .3mf to ``path``.

    Objects keep their build123d design coordinates as the assembled layout. An
    object with a :attr:`~ModelObject.print_location` is additionally placed
    there for printing (the build ``<item>`` transform); when any object is
    placed, an ``<assemble>`` block pins *every* object's Assembly-View position
    back to its design coordinates so the two views can differ. OrcaSlicer still
    auto-centers the whole group on a single plate on import, so
    ``print_location`` controls the *relative* print layout rather than absolute
    bed coordinates.
    """
    from .model_settings import build_model_settings_xml
    from .model_xml import build_model_xml
    from .package import write_3mf

    if not self.objects:
      raise ValueError("Project has no objects to save")
    resolved = self._resolve(tolerance, angular_tolerance)
    model_xml_str = build_model_xml(resolved, self.info)
    settings_xml = build_model_settings_xml(resolved)
    return write_3mf(path, model_xml_str, settings_xml)

  def to_compound(
    self,
    *,
    layout: Literal["assembly", "print"] = "assembly",
  ) -> Compound:
    """Build a build123d assembly mirroring the Project tree.

    Returns a nested :class:`~build123d.topology.Compound` (``Project`` ->
    objects -> parts) that you can hand to ``ocp_vscode.show()`` to preview the
    project, or to build123d's exporters. Each part keeps its name as the node
    ``label``.

    ``layout`` selects which OrcaSlicer view the compound mirrors:

    * ``"assembly"`` (default) -- parts at their build123d design coordinates,
      i.e. the assembled arrangement shown in OrcaSlicer's Assembly View.
    * ``"print"`` -- each object's :attr:`~ModelObject.print_location` applied,
      then the whole group centered in XY, i.e. what lands on the print bed
      (OrcaSlicer auto-centers the group on the plate). Objects without a
      ``print_location`` stay at their design position.

    Plain shapes are copied so labelling them does not mutate the originals you
    passed in.
    """
    if not self.objects:
      raise ValueError("Project has no objects")
    obj_nodes: list[Compound] = []
    for obj in self.objects:
      place = obj.print_location if layout == "print" else None
      part_shapes: list[Shape] = []
      for part in obj.parts:
        shp = copy.copy(part.shape)
        if place is not None:
          shp = place * shp
        shp.label = part.name
        part_shapes.append(shp)
      obj_nodes.append(Compound(label=obj.name, children=part_shapes))
    project = Compound(label="Project", children=obj_nodes)
    if layout == "print":
      center = project.bounding_box().center()
      project.move(Location((-center.X, -center.Y, 0.0)))
    return project

  def __repr__(self) -> str:
    return f"Project(objects={len(self.objects)})"
