"""Public builder API: Project / ModelObject / Part, and Project.save()."""

import copy
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path

from build123d.topology import Compound, Shape

from .mesh import MeshData, mesh_to_face, tessellate_shape
from .paint import FUZZY_ATTR, SEAM_ATTR, EnforcerBlockerType, encode_region_paint
from .print_settings import PrintSettings
from .texture import ImageLike, ProjectionMode, apply_textures, make_job

__all__ = ["ModelObject", "Part", "PartSubtype", "Project"]


@dataclass
class _PaintRequest:
  """A pending paint operation, evaluated against the mesh at resolve time."""

  attr: str  # the 3MF <triangle> attribute, e.g. "paint_seam"
  state: EnforcerBlockerType  # paint state to apply
  region: Shape | list[Shape]  # build123d solid / face / sketch / edge (or list)
  max_depth: int
  within: float  # edge proximity radius (mm); ignored for non-edge regions


@dataclass
class _TextureRequest:
  """A pending texture (surface displacement), applied to the mesh at resolve time.

  ``faces`` selects which of the part's faces to texture (``None`` = all of them);
  it is resolved to ``shape.faces()`` indices when the part is tessellated.
  """

  image: ImageLike  # grayscale heightmap: path / PIL image / numpy array
  faces: Shape | Sequence[Shape] | None
  amplitude: float
  scale: float | tuple[float, float]
  offset: tuple[float, float]
  rotation: float
  mode: ProjectionMode
  max_edge: float | None
  top_angle: float
  bottom_angle: float
  keep_bottom: bool
  max_triangles: int
  simplify: float


class PartSubtype(str, Enum):
  """Per-part subtypes understood by OrcaSlicer."""

  NORMAL = "normal_part"
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
    self._textures: list[_TextureRequest] = []

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

  def apply_texture(
    self,
    image: ImageLike,
    *,
    faces: Shape | Sequence[Shape] | None = None,
    amplitude: float = 0.3,
    scale: float | tuple[float, float] = 10.0,
    offset: tuple[float, float] = (0.0, 0.0),
    rotation: float = 0.0,
    mode: ProjectionMode = ProjectionMode.TRIPLANAR,
    max_edge: float | None = None,
    top_angle: float = 90.0,
    bottom_angle: float = 90.0,
    keep_bottom: bool = True,
    max_triangles: int = 2_000_000,
    simplify: float = 0.5,
  ) -> None:
    """Bake a grayscale heightmap into this part as real surface relief.

    The mesh is adaptively subdivided and its vertices displaced along their
    normals by the sampled texture: mid-gray is neutral, white pushes out and
    black pushes in, with ``amplitude`` the peak displacement in millimetres.
    ``scale`` is the world size (mm) of one texture tile; ``mode`` selects the
    projection (triplanar by default). See :func:`~orca123d.texture.texturize_mesh`
    for the full parameter reference.

    ``faces`` restricts the texture to specific faces of this part -- pass a
    build123d ``Face``/``ShapeList`` selected off this part's shape (e.g.
    ``box.faces().sort_by(Axis.Z)[-1]``); ``None`` textures the whole part. The
    relief tapers to flat at the boundary of the selected faces, leaving the rest
    untouched. Call this more than once to texture different faces (with
    different textures if you like).

    Texturing and painting (:meth:`paint_seam` / :meth:`paint_fuzzy_skin`) cannot
    be combined on the same part -- subdivision invalidates the painted triangles
    -- so split the geometry into separate parts if you need both.

    ``simplify`` decimates the displaced mesh by that fraction of triangles
    (default ~half; ``0`` keeps the dense mesh) so the part stays light in the
    viewer and the exported 3MF. Across several ``apply_texture`` calls the
    strongest (largest) ``simplify`` is applied once to the whole baked mesh.
    """
    self._textures.append(
      _TextureRequest(
        image,
        faces,
        amplitude,
        scale,
        offset,
        rotation,
        mode,
        max_edge,
        top_angle,
        bottom_angle,
        keep_bottom,
        max_triangles,
        simplify,
      )
    )

  def _resolve(
    self, mesh_id: int, tolerance: float, angular_tolerance: float
  ) -> "ResolvedPart":
    if self._textures and self._paints:
      raise ValueError(
        f"Part {self.name!r}: texturing and painting the same part is not "
        "supported (subdivision invalidates the painted triangles)"
      )
    mesh = tessellate_shape(self.shape, tolerance, angular_tolerance)
    if self._textures:
      jobs = [self._build_texture_job(req) for req in self._textures]
      simplify = max(req.simplify for req in self._textures)
      mesh = apply_textures(mesh, jobs, simplify=simplify)
    return ResolvedPart(
      self, mesh_id=mesh_id, mesh=mesh, paint=self._compute_paint(mesh)
    )

  def _build_texture_job(self, req: _TextureRequest):
    face_ids = None if req.faces is None else self._face_indices(req.faces)
    return make_job(
      req.image,
      amplitude=req.amplitude,
      scale=req.scale,
      offset=req.offset,
      rotation=req.rotation,
      mode=req.mode,
      max_edge=req.max_edge,
      top_angle=req.top_angle,
      bottom_angle=req.bottom_angle,
      keep_bottom=req.keep_bottom,
      max_triangles=req.max_triangles,
      face_ids=face_ids,
    )

  def _face_indices(self, selector: Shape | Sequence[Shape]) -> tuple[int, ...]:
    """Map selected build123d faces to indices in ``self.shape.faces()``.

    Matched by topological identity (``IsSame``), like paint's whole-face mode,
    so the faces must be selected off this part's own shape.
    """
    items = [selector] if isinstance(selector, Shape) else list(selector)
    selected = [f for item in items for f in item.faces()]
    model_faces = self.shape.faces()
    ids: set[int] = set()
    for face in selected:
      idx = next(
        (i for i, mf in enumerate(model_faces) if face.wrapped.IsSame(mf.wrapped)),
        None,
      )
      if idx is None:
        raise ValueError(
          f"Part {self.name!r}: apply_texture face is not part of this part's "
          "shape; select faces off the same shape passed to the part"
        )
      ids.add(idx)
    return tuple(sorted(ids))

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

  def __init__(self, *, name: str, settings: PrintSettings | None = None) -> None:
    self.name = name
    self.settings = settings or PrintSettings()
    self.parts: list[Part] = []
    # (z, layer_height) control points; z=0 is the object's bottom. None = uniform.
    self.layer_height_profile: list[tuple[float, float]] | None = None

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

  def set_layer_height_profile(self, points: Sequence[tuple[float, float]]) -> None:
    """Set a variable layer height directly from ``(z, height)`` control points.

    The profile is a piecewise-linear curve OrcaSlicer samples while slicing:
    ``z`` is measured from the object's bottom (objects are dropped to the bed)
    and must start at 0; equal ``z`` values make a step, differing ones a ramp.
    Heights are millimeters and must be positive (OrcaSlicer further clamps them
    to the active printer's min/max layer height). This is the low-level escape
    hatch; see :meth:`optimize_layer_height` to derive one from geometry.
    """
    pts = [(float(z), float(h)) for z, h in points]
    if len(pts) < 2:
      raise ValueError("layer height profile needs at least 2 (z, height) points")
    if abs(pts[0][0]) > 1e-6:
      raise ValueError("first control point must be at z=0 (the object's bottom)")
    for (z0, _), (z1, _) in zip(pts, pts[1:]):
      if z1 < z0 - 1e-9:
        raise ValueError("control-point z values must be non-decreasing")
    if any(h <= 0.0 for _, h in pts):
      raise ValueError("layer heights must be positive")
    self.layer_height_profile = pts

  def optimize_layer_height(
    self,
    faces: Shape | Sequence[Shape],
    *,
    min_layer_height: float = 0.08,
    base_height: float = 0.2,
    max_change: float = 0.04,
  ) -> None:
    """Print the z-span of ``faces`` at a finer layer height than the rest.

    Pass the build123d face(s) you care about (a ``Face``, a ``ShapeList`` from
    ``shape.faces()``, or any shape -- its faces are used). The z-range those faces
    occupy is taken to ``min_layer_height``; the height ramps from ``base_height``
    into that band and back out above it, changing at most ``max_change`` mm per
    layer so there is no abrupt step. Everything else prints at ``base_height``.

    ``base_height`` is the object's normal layer height and ``min_layer_height``
    the fine height for the band; both should suit the target printer/nozzle.
    """
    from .layer_heights import optimize_for_faces

    if not self.parts:
      raise ValueError(f"Object {self.name!r} has no parts to measure against")
    items = [faces] if isinstance(faces, Shape) else faces
    selected = [f for item in items for f in item.faces()]
    if not selected:
      raise ValueError("optimize_layer_height needs at least one face")
    face_meshes = [tessellate_shape(f) for f in selected]

    boxes = [part.shape.bounding_box(optimal=True) for part in self.parts]
    z_origin = min(bb.min.Z for bb in boxes)
    object_height = max(bb.max.Z for bb in boxes) - z_origin

    self.layer_height_profile = optimize_for_faces(
      face_meshes,
      z_origin=z_origin,
      object_height=object_height,
      min_layer_height=min_layer_height,
      base_height=base_height,
      max_change=max_change,
    )

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
    self.translate: tuple[float, float, float] = (0.0, 0.0, 0.0)
    self.layer_height_profile = obj.layer_height_profile


class Project:
  """A collection of objects exportable to an OrcaSlicer .3mf project file."""

  def __init__(self) -> None:
    self.objects: list[ModelObject] = []

  def add_object(
    self,
    shape: "Shape | None" = None,
    *,
    name: str | None = None,
    settings: PrintSettings | None = None,
  ) -> ModelObject:
    """Add an object. If ``shape`` is given it becomes the object's single part.

    When ``name`` is omitted, a given shape's ``label`` is used if it has one,
    otherwise a name is generated from the object index.
    """
    if name is None and shape is not None and shape.label:
      name = shape.label
    obj = ModelObject(name=name or f"Object {len(self.objects) + 1}", settings=settings)
    if shape is not None:
      obj.add_part(shape, name=obj.name)
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
    """Tessellate and write a model-only .3mf to ``path``."""
    from .layer_heights import build_layer_heights_profile
    from .model_settings import build_model_settings_xml
    from .model_xml import build_model_xml
    from .package import write_3mf

    if not self.objects:
      raise ValueError("Project has no objects to save")
    resolved = self._resolve(tolerance, angular_tolerance)
    model_xml_str = build_model_xml(resolved)
    settings_xml = build_model_settings_xml(resolved)
    layer_heights = build_layer_heights_profile(resolved)
    return write_3mf(path, model_xml_str, settings_xml, layer_heights)

  def to_compound(
    self,
    *,
    tolerance: float = 0.01,
    angular_tolerance: float = 0.1,
    textured: bool = True,
  ) -> Compound:
    """Build a build123d assembly mirroring the Project tree.

    Returns a nested :class:`~build123d.topology.Compound` (``Project`` ->
    objects -> parts) that you can hand to ``ocp_vscode.show()`` to preview the
    project, or to build123d's exporters. Each part keeps its name as the node
    ``label``.

    Textured parts are resolved to their displaced meshes -- i.e. exactly what
    :meth:`save` exports -- so the relief is visible; every other part is shown
    as its build123d shape (crisp edges, no faceting). Set ``textured=False`` to
    skip texturing and use the plain shapes only (faster). Plain shapes are
    copied so labelling them does not mutate the originals you passed in.
    """
    if not self.objects:
      raise ValueError("Project has no objects")
    obj_nodes: list[Compound] = []
    for obj in self.objects:
      part_shapes: list[Shape] = []
      for part in obj.parts:
        if textured and part._textures:
          mesh = part._resolve(1, tolerance, angular_tolerance).mesh
          shp = mesh_to_face(mesh)
        else:
          shp = copy.copy(part.shape)
        shp.label = part.name
        part_shapes.append(shp)
      obj_nodes.append(Compound(label=obj.name, children=part_shapes))
    return Compound(label="Project", children=obj_nodes)

  def __repr__(self) -> str:
    return f"Project(objects={len(self.objects)})"
