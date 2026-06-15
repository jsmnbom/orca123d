"""Typed OrcaSlicer print (process) settings.

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

__all__ = [
  "BrimType",
  "PrintSequence",
  "PrintOrder",
  "FuzzySkinType",
  "FuzzySkinMode",
  "NoiseType",
  "DraftShield",
  "SkirtType",
  "TimelapseType",
  "SlicingMode",
  "WipeTowerWallType",
  "CounterboreHoleBridgingOption",
  "EnableExtraBridgeLayer",
  "InternalBridgeFilter",
  "WallSequence",
  "WallDirection",
  "IroningType",
  "IroningPattern",
  "SeamPosition",
  "SeamScarfType",
  "PerimeterGeneratorType",
  "SupportType",
  "SupportMaterialPattern",
  "SupportMaterialInterfacePattern",
  "SupportMaterialStyle",
  "GapFillTarget",
  "EnsureVerticalShellThickness",
  "TopSurfacePattern",
  "SparseInfillPattern",
  "PrintSettings",
]

class BrimType(str, Enum):
  AUTO = 'auto_brim'
  MOUSE_EAR = 'brim_ears'
  PAINTED = 'painted'
  OUTER_BRIM_ONLY = 'outer_only'
  INNER_BRIM_ONLY = 'inner_only'
  OUTER_AND_INNER_BRIM = 'outer_and_inner'
  NO_BRIM = 'no_brim'


class PrintSequence(str, Enum):
  BY_LAYER = 'by layer'
  BY_OBJECT = 'by object'


class PrintOrder(str, Enum):
  DEFAULT = 'default'
  AS_OBJECT_LIST = 'as_obj_list'


class FuzzySkinType(str, Enum):
  PAINTED_ONLY = 'none'
  CONTOUR = 'external'
  HOLE = 'hole'
  CONTOUR_AND_HOLE = 'all'
  ALL_WALLS = 'allwalls'
  DISABLED = 'disabled_fuzzy'


class FuzzySkinMode(str, Enum):
  DISPLACEMENT = 'displacement'
  EXTRUSION = 'extrusion'
  COMBINED = 'combined'


class NoiseType(str, Enum):
  CLASSIC = 'classic'
  PERLIN = 'perlin'
  BILLOW = 'billow'
  RIDGED_MULTIFRACTAL = 'ridgedmulti'
  VORONOI = 'voronoi'
  RIPPLE = 'ripple'


class DraftShield(str, Enum):
  DISABLED = 'disabled'
  ENABLED = 'enabled'


class SkirtType(str, Enum):
  COMBINED = 'combined'
  PER_OBJECT = 'perobject'


class TimelapseType(str, Enum):
  TRADITIONAL = '0'
  SMOOTH = '1'


class SlicingMode(str, Enum):
  REGULAR = 'regular'
  EVEN_ODD = 'even_odd'
  CLOSE_HOLES = 'close_holes'


class WipeTowerWallType(str, Enum):
  RECTANGLE = 'rectangle'
  CONE = 'cone'
  RIB = 'rib'


class CounterboreHoleBridgingOption(str, Enum):
  NONE = 'none'
  PARTIALLY_BRIDGED = 'partiallybridge'
  SACRIFICIAL_LAYER = 'sacrificiallayer'


class EnableExtraBridgeLayer(str, Enum):
  DISABLED = 'disabled'
  EXTERNAL_BRIDGE_ONLY = 'external_bridge_only'
  INTERNAL_BRIDGE_ONLY = 'internal_bridge_only'
  APPLY_TO_ALL = 'apply_to_all'


class InternalBridgeFilter(str, Enum):
  FILTER = 'disabled'
  LIMITED_FILTERING = 'limited'
  NO_FILTERING = 'nofilter'


class WallSequence(str, Enum):
  INNER_OUTER = 'inner wall/outer wall'
  OUTER_INNER = 'outer wall/inner wall'
  INNER_OUTER_INNER = 'inner-outer-inner wall'


class WallDirection(str, Enum):
  COUNTER_CLOCKWISE = 'ccw'
  CLOCKWISE = 'cw'


class IroningType(str, Enum):
  NO_IRONING = 'no ironing'
  TOP_SURFACES = 'top'
  TOPMOST_SURFACE = 'topmost'
  ALL_SOLID_LAYERS = 'solid'


class IroningPattern(str, Enum):
  RECTILINEAR = 'rectilinear'
  CONCENTRIC = 'concentric'


class SeamPosition(str, Enum):
  NEAREST = 'nearest'
  ALIGNED = 'aligned'
  ALIGNED_BACK = 'aligned_back'
  BACK = 'back'
  RANDOM = 'random'


class SeamScarfType(str, Enum):
  NONE = 'none'
  CONTOUR = 'external'
  CONTOUR_AND_HOLE = 'all'


class PerimeterGeneratorType(str, Enum):
  CLASSIC = 'classic'
  ARACHNE = 'arachne'


class SupportType(str, Enum):
  NORMAL_AUTO = 'normal(auto)'
  TREE_AUTO = 'tree(auto)'
  NORMAL_MANUAL = 'normal(manual)'
  TREE_MANUAL = 'tree(manual)'


class SupportMaterialPattern(str, Enum):
  DEFAULT = 'default'
  RECTILINEAR = 'rectilinear'
  RECTILINEAR_GRID = 'rectilinear-grid'
  HONEYCOMB = 'honeycomb'
  LIGHTNING = 'lightning'
  HOLLOW = 'hollow'


class SupportMaterialInterfacePattern(str, Enum):
  DEFAULT = 'auto'
  RECTILINEAR = 'rectilinear'
  CONCENTRIC = 'concentric'
  RECTILINEAR_INTERLACED = 'rectilinear_interlaced'
  GRID = 'grid'


class SupportMaterialStyle(str, Enum):
  DEFAULT_GRID_ORGANIC = 'default'
  GRID = 'grid'
  SNUG = 'snug'
  ORGANIC = 'organic'
  TREE_SLIM = 'tree_slim'
  TREE_STRONG = 'tree_strong'
  TREE_HYBRID = 'tree_hybrid'


class GapFillTarget(str, Enum):
  EVERYWHERE = 'everywhere'
  TOP_AND_BOTTOM_SURFACES = 'topbottom'
  NOWHERE = 'nowhere'


class EnsureVerticalShellThickness(str, Enum):
  NONE = 'none'
  CRITICAL_ONLY = 'ensure_critical_only'
  MODERATE = 'ensure_moderate'
  ALL = 'ensure_all'


class TopSurfacePattern(str, Enum):
  MONOTONIC = 'monotonic'
  MONOTONIC_LINE = 'monotonicline'
  RECTILINEAR = 'rectilinear'
  ALIGNED_RECTILINEAR = 'alignedrectilinear'
  CONCENTRIC = 'concentric'
  HILBERT_CURVE = 'hilbertcurve'
  ARCHIMEDEAN_CHORDS = 'archimedeanchords'
  OCTAGRAM_SPIRAL = 'octagramspiral'


class SparseInfillPattern(str, Enum):
  RECTILINEAR = 'rectilinear'
  ALIGNED_RECTILINEAR = 'alignedrectilinear'
  ZIG_ZAG = 'zigzag'
  CROSS_ZAG = 'crosszag'
  LOCKED_ZAG = 'lockedzag'
  LINE = 'line'
  GRID = 'grid'
  TRIANGLES = 'triangles'
  TRI_HEXAGON = 'tri-hexagon'
  CUBIC = 'cubic'
  ADAPTIVE_CUBIC = 'adaptivecubic'
  QUARTER_CUBIC = 'quartercubic'
  SUPPORT_CUBIC = 'supportcubic'
  LIGHTNING = 'lightning'
  HONEYCOMB = 'honeycomb'
  HONEYCOMB_3D = '3dhoneycomb'
  LATERAL_HONEYCOMB = 'lateral-honeycomb'
  LATERAL_LATTICE = 'lateral-lattice'
  CROSS_HATCH = 'crosshatch'
  TPMS_D = 'tpmsd'
  TPMS_FK = 'tpmsfk'
  GYROID = 'gyroid'
  CONCENTRIC = 'concentric'
  HILBERT_CURVE = 'hilbertcurve'
  ARCHIMEDEAN_CHORDS = 'archimedeanchords'
  OCTAGRAM_SPIRAL = 'octagramspiral'



class PrintSettings(BaseModel):
  """A sparse set of OrcaSlicer print (process) settings."""

  model_config = ConfigDict(
    extra="allow",
    validate_assignment=True,
    use_attribute_docstrings=True,
  )

  brim_width: coerce.Float | None = None
  """Distance from model to the outermost brim line."""
  brim_type: Annotated[BrimType, coerce.EnumValue] | None = None
  """This controls the generation of the brim at outer and/or inner side of models. Auto means the brim width is analyzed and calculated automatically."""
  brim_object_gap: coerce.Float | None = None
  """A gap between innermost brim line and object can make brim be removed more easily."""
  brim_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for brims.

  The actual brim flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.

  Note: The resulting value will not be affected by the first-layer flow ratio.
  """
  brim_use_efc_outline: coerce.Bool | None = None
  """
  When enabled, the brim is aligned with the first-layer perimeter geometry after Elephant Foot Compensation is applied.
  This option is intended for cases where Elephant Foot Compensation significantly alters the first-layer footprint.

  If your current setup already works well, enabling it may be unnecessary and can cause the brim to fuse with upper layers.
  """
  combine_brims: coerce.Bool | None = None
  """Combine multiple brims into one when they are close to each other. This can improve brim adhesion."""
  brim_ears_max_angle: coerce.Float | None = None
  """
  Maximum angle to let a brim ear appear.
  If set to 0, no brim will be created.
  If set to ~180, brim will be created on everything but straight sections.
  """
  brim_ears_detection_length: coerce.Float | None = None
  """
  The geometry will be decimated before detecting sharp angles. This parameter indicates the minimum length of the deviation for the decimation.
  0 to deactivate.
  """
  print_sequence: Annotated[PrintSequence, coerce.EnumValue] | None = None
  """Print sequence, layer by layer or object by object."""
  print_order: Annotated[PrintOrder, coerce.EnumValue] | None = None
  """Print order within a single layer."""
  fuzzy_skin: Annotated[FuzzySkinType, coerce.EnumValue] | None = None
  """Randomly jitter while printing the wall, so that the surface has a rough look. This setting controls the fuzzy position."""
  fuzzy_skin_thickness: coerce.Float | None = None
  """The width within which to jitter. It's advised to be below outer wall line width."""
  fuzzy_skin_point_distance: coerce.Float | None = None
  """The average distance between the random points introduced on each line segment."""
  fuzzy_skin_first_layer: coerce.Bool | None = None
  """Whether to apply fuzzy skin on the first layer."""
  fuzzy_skin_mode: Annotated[FuzzySkinMode, coerce.EnumValue] | None = None
  """
  Fuzzy skin generation mode. Works only with Arachne!
  Displacement: Сlassic mode when the pattern is formed by shifting the nozzle sideways from the original path.
  Extrusion: The mode when the pattern formed by the amount of extruded plastic. This is the fast and straight algorithm without unnecessary nozzle shake that gives a smooth pattern. But it is more useful for forming loose walls in the entire they array.
  Combined: Joint mode [Displacement] + [Extrusion]. The appearance of the walls is similar to [Displacement] Mode, but it leaves no pores between the perimeters.

  Attention! The [Extrusion] and [Combined] modes works only the fuzzy_skin_thickness parameter not more than the thickness of printed loop. At the same time, the width of the extrusion for a particular layer should also not be below a certain level. It is usually equal 15-25%% of a layer height. Therefore, the maximum fuzzy skin thickness with a perimeter width of 0.4 mm and a layer height of 0.2 mm will be 0.4-(0.2*0.25)=±0.35mm! If you enter a higher parameter than this, the error Flow::spacing() will displayed, and the model will not be sliced. You can choose this number until this error is repeated.
  """
  fuzzy_skin_noise_type: Annotated[NoiseType, coerce.EnumValue] | None = None
  """
  Noise type to use for fuzzy skin generation:
  Classic: Classic uniform random noise.
  Perlin: Perlin noise, which gives a more consistent texture.
  Billow: Similar to perlin noise, but clumpier.
  Ridged Multifractal: Ridged noise with sharp, jagged features. Creates marble-like textures.
  Voronoi: Divides the surface into voronoi cells, and displaces each one by a random amount. Creates a patchwork texture.
  Ripple: Uniform ripple pattern that ripples left and right of the original path. Repeating pattern, woven appearance.
  """
  fuzzy_skin_scale: coerce.Float | None = None
  """The base size of the coherent noise features, in mm. Higher values will result in larger features."""
  fuzzy_skin_octaves: coerce.Int | None = None
  """The number of octaves of coherent noise to use. Higher values increase the detail of the noise, but also increase computation time."""
  fuzzy_skin_persistence: coerce.Float | None = None
  """The decay rate for higher octaves of the coherent noise. Lower values will result in smoother noise."""
  fuzzy_skin_ripples_per_layer: coerce.Int | None = None
  """Controls how many full cycles of ripples will be added per layer."""
  fuzzy_skin_ripple_offset: coerce.Percent | None = None
  """
  Shifts the ripple phase forward along the print path by the specified percentage of a wavelength each layer period.
  - 0% keeps every layer identical.
  - 50% shifts the pattern by half a wavelength, effectively inverting the phase.
  - 100% shifts the pattern by a full wavelength, returning to the original phase.

  The shift is applied once every number of layers set by Layers between ripple offset, so layers within the same group are printed identically.
  """
  fuzzy_skin_layers_between_ripple_offset: coerce.Int | None = None
  """
  Specifies how many consecutive layers share the same ripple phase before the offset is applied.
  For example:
  - 1 = Layer 1 is printed with the base ripple pattern, then layer 2 is shifted by the configured offset, then layer 3 returns to the base pattern, and so on.
  - 3 = Layers 1 to 3 are printed with the base ripple pattern, then layers 4 to 6 are shifted by the configured offset, then layers 7 to 9 return to the base pattern, etc.
  """
  gcode_add_line_number: coerce.Bool | None = None
  """Enable this to add line number(Nx) at the beginning of each G-code line."""
  gcode_label_objects: coerce.Bool | None = None
  """Enable this to add comments into the G-code labeling print moves with what object they belong to, which is useful for the Octoprint CancelObject plug-in. This setting is NOT compatible with Single Extruder Multi Material setup and Wipe into Object / Wipe into Infill."""
  exclude_object: coerce.Bool | None = None
  """Enable this option to add EXCLUDE OBJECT command in G-code."""
  gcode_comments: coerce.Bool | None = None
  """Enable this to get a commented G-code file, with each line explained by a descriptive text. If you print from SD card, the additional weight of the file could make your firmware slow down."""
  enable_wrapping_detection: coerce.Bool | None = None
  """Enable clumping detection"""
  notes: coerce.Str | None = None
  """You can put here your personal notes. This text will be added to the G-code header comments."""
  reduce_infill_retraction: coerce.Bool | None = None
  """Don't retract when the travel is entirely within an infill area. That means the oozing can't been seen. This can reduce times of retraction for complex model and save printing time, but make slicing and G-code generating slower. Note that z-hop is also not performed in areas where retraction is skipped."""
  filename_format: coerce.Str | None = None
  """Users can define the project file name when exporting."""
  post_process: coerce.Strs | None = None
  """If you want to process the output G-code through custom scripts, just list their absolute paths here. Separate multiple scripts with a semicolon. Scripts will be passed the absolute path to the G-code file as the first argument, and they can access the Orca Slicer config settings by reading environment variables."""
  process_change_extrusion_role_gcode: coerce.Str | None = None
  """This G-code is inserted when the extrusion role is changed. It runs after the machine and filament extrusion role G-code."""
  skirt_distance: coerce.Float | None = None
  """The distance from the skirt to the brim or the object."""
  skirt_start_angle: coerce.Float | None = None
  """Angle from the object center to skirt start point. Zero is the most right position, counter clockwise is positive angle."""
  skirt_height: coerce.Int | None = None
  """How many layers of skirt. Usually only one layer."""
  single_loop_draft_shield: coerce.Bool | None = None
  """Limits the skirt/draft shield loops to one wall after the first layer. This is useful, on occasion, to conserve filament but may cause the draft shield/skirt to warp / crack."""
  draft_shield: Annotated[DraftShield, coerce.EnumValue] | None = None
  """
  A draft shield is useful to protect an ABS or ASA print from warping and detaching from print bed due to wind draft. It is usually needed only with open frame printers, i.e. without an enclosure.

  Enabled = skirt is as tall as the highest printed object. Otherwise 'Skirt height' is used.
  Note: With the draft shield active, the skirt will be printed at skirt distance from the object. Therefore, if brims are active it may intersect with them. To avoid this, increase the skirt distance value.
  """
  skirt_type: Annotated[SkirtType, coerce.EnumValue] | None = None
  """Combined - single skirt for all objects, Per object - individual object skirt."""
  skirt_loops: coerce.Int | None = None
  """Number of loops for the skirt. Zero means disabling skirt."""
  skirt_speed: coerce.Float | None = None
  """Speed of skirt, in mm/s. Zero means use default layer extrusion speed."""
  min_skirt_length: coerce.Float | None = None
  """
  Minimum filament extrusion length in mm when printing the skirt. Zero means this feature is disabled.

  Using a non-zero value is useful if the printer is set up to print without a prime line.
  Final number of loops is not taking into account while arranging or validating objects distance. Increase loop number in such case.
  """
  spiral_mode: coerce.Bool | None = None
  """Spiralize smooths out the Z moves of the outer contour. And turns a solid model into a single walled print with solid bottom layers. The final generated model has no seam."""
  spiral_mode_smooth: coerce.Bool | None = None
  """Smooth Spiral smooths out X and Y moves as well, resulting in no visible seam at all, even in the XY directions on walls that are not vertical."""
  spiral_mode_max_xy_smoothing: coerce.FloatOrPercent | None = None
  """Maximum distance to move points in XY to try to achieve a smooth spiral. If expressed as a %, it will be computed over nozzle diameter."""
  spiral_starting_flow_ratio: coerce.Float | None = None
  """Sets the starting flow ratio while transitioning from the last bottom layer to the spiral. Normally the spiral transition scales the flow ratio from 0% to 100% during the first loop which can in some cases lead to under extrusion at the start of the spiral."""
  spiral_finishing_flow_ratio: coerce.Float | None = None
  """Sets the finishing flow ratio while ending the spiral. Normally the spiral transition scales the flow ratio from 100% to 0% during the last loop which can in some cases lead to under extrusion at the end of the spiral."""
  timelapse_type: Annotated[TimelapseType, coerce.EnumValue] | None = None
  """If smooth or traditional mode is selected, a timelapse video will be generated for each print. After each layer is printed, a snapshot is taken with the chamber camera. All of these snapshots are composed into a timelapse video when printing completes. If smooth mode is selected, the toolhead will move to the excess chute after each layer is printed and then take a snapshot. Since the melt filament may leak from the nozzle during the process of taking a snapshot, a prime tower is required for smooth mode to wipe nozzle."""
  slicing_mode: Annotated[SlicingMode, coerce.EnumValue] | None = None
  """Use \\\\\\"Even-odd\\\\\\" for 3DLabPrint airplane models. Use \\\\\\"Close holes\\\\\\" to close all holes in the model."""
  sparse_infill_filament: coerce.Int | None = None
  """Filament to print internal sparse infill."""
  interface_shells: coerce.Bool | None = None
  """Force the generation of solid shells between adjacent materials/volumes. Useful for multi-extruder prints with translucent materials or manual soluble support material."""
  mmu_segmented_region_max_width: coerce.Float | None = None
  """Maximum width of a segmented region. Zero disables this feature."""
  mmu_segmented_region_interlocking_depth: coerce.Float | None = None
  """Interlocking depth of a segmented region. It will be ignored if \\\\\\"mmu_segmented_region_max_width\\\\\\" is zero or if \\\\\\"mmu_segmented_region_interlocking_depth\\\\\\" is bigger than \\\\\\"mmu_segmented_region_max_width\\\\\\". Zero disables this feature."""
  interlocking_beam: coerce.Bool | None = None
  """Generate interlocking beam structure at the locations where different filaments touch. This improves the adhesion between filaments, especially models printed in different materials."""
  interlocking_beam_width: coerce.Float | None = None
  """The width of the interlocking structure beams."""
  interlocking_orientation: coerce.Float | None = None
  """Orientation of interlock beams."""
  interlocking_beam_layer_count: coerce.Int | None = None
  """The height of the beams of the interlocking structure, measured in number of layers. Less layers is stronger, but more prone to defects."""
  interlocking_depth: coerce.Int | None = None
  """The distance from the boundary between filaments to generate interlocking structure, measured in cells. Too few cells will result in poor adhesion."""
  interlocking_boundary_avoidance: coerce.Int | None = None
  """The distance from the outside of a model where interlocking structures will not be generated, measured in cells."""
  ooze_prevention: coerce.Bool | None = None
  """This option will drop the temperature of the inactive extruders to prevent oozing."""
  wall_filament: coerce.Int | None = None
  """Filament to print walls."""
  solid_infill_filament: coerce.Int | None = None
  """Filament to print solid infill."""
  standby_temperature_delta: coerce.Int | None = None
  """Temperature difference to be applied when an extruder is not active. The value is not used when 'idle_temperature' in filament settings is set to non-zero value."""
  preheat_time: coerce.Float | None = None
  """To reduce the waiting time after tool change, Orca can preheat the next tool while the current tool is still in use. This setting specifies the time in seconds to preheat the next tool. Orca will insert a M104 command to preheat the tool in advance."""
  preheat_steps: coerce.Int | None = None
  """Insert multiple preheat commands (e.g. M104.1). Only useful for Prusa XL. For other printers, please set it to 1."""
  wipe_tower_no_sparse_layers: coerce.Bool | None = None
  """If enabled, the wipe tower will not be printed on layers with no tool changes. On layers with a tool change, extruder will travel downward to print the wipe tower. User is responsible for ensuring there is no collision with the print."""
  single_extruder_multi_material_priming: coerce.Bool | None = None
  """If enabled, all printing extruders will be primed at the front edge of the print bed at the start of the print."""
  enable_prime_tower: coerce.Bool | None = None
  """The wiping tower can be used to clean up the residue on the nozzle and stabilize the chamber pressure inside the nozzle, in order to avoid appearance defects when printing objects."""
  prime_tower_enable_framework: coerce.Bool | None = None
  """Enable internal ribs to increase the stability of the prime tower."""
  prime_volume: coerce.Float | None = None
  """The volume of material to prime extruder on tower."""
  prime_tower_width: coerce.Float | None = None
  """Width of the prime tower."""
  wipe_tower_rotation_angle: coerce.Float | None = None
  """Wipe tower rotation angle with respect to X axis."""
  prime_tower_brim_width: coerce.Float | None = None
  """Brim width of prime tower, negative number means auto calculated width based on the height of prime tower."""
  wipe_tower_cone_angle: coerce.Float | None = None
  """Angle at the apex of the cone that is used to stabilize the wipe tower. Larger angle means wider base."""
  wipe_tower_max_purge_speed: coerce.Float | None = None
  """
  The maximum print speed when purging in the wipe tower and printing the wipe tower sparse layers. When purging, if the sparse infill speed or calculated speed from the filament max volumetric speed is lower, the lowest will be used instead.

  When printing the sparse layers, if the internal perimeter speed or calculated speed from the filament max volumetric speed is lower, the lowest will be used instead.

  Increasing this speed may affect the tower's stability as well as increase the force with which the nozzle collides with any blobs that may have formed on the wipe tower.

  Before increasing this parameter beyond the default of 90 mm/s, make sure your printer can reliably bridge at the increased speeds and that ooze when tool changing is well controlled.

  For the wipe tower external perimeters the internal perimeter speed is used regardless of this setting.
  """
  wipe_tower_wall_type: Annotated[WipeTowerWallType, coerce.EnumValue] | None = None
  """
  Wipe tower outer wall type.
  1. Rectangle: The default wall type, a rectangle with fixed width and height.
  2. Cone: A cone with a fillet at the bottom to help stabilize the wipe tower.
  3. Rib: Adds four ribs to the tower wall for enhanced stability.
  """
  wipe_tower_extra_rib_length: coerce.Float | None = None
  """Positive values can increase the size of the rib wall, while negative values can reduce the size. However, the size of the rib wall can not be smaller than that determined by the cleaning volume."""
  wipe_tower_rib_width: coerce.Float | None = None
  """Rib width is always less than half the prime tower side length."""
  wipe_tower_fillet_wall: coerce.Bool | None = None
  """The wall of prime tower will fillet."""
  wipe_tower_filament: coerce.Int | None = None
  """The extruder to use when printing perimeter of the wipe tower. Set to 0 to use the one that is available (non-soluble would be preferred)."""
  prime_tower_skip_points: coerce.Bool | None = None
  """The wall of prime tower will skip the start points of wipe path."""
  enable_tower_interface_features: coerce.Bool | None = None
  """Enable optimized prime tower interface behavior when different materials meet."""
  enable_tower_interface_cooldown_during_tower: coerce.Bool | None = None
  """When interface-layer temperature boost is active, set the nozzle back to print temperature at the start of the prime tower so it cools down during the tower."""
  prime_tower_infill_gap: coerce.Percent | None = None
  """Infill gap."""
  flush_into_infill: coerce.Bool | None = None
  """Purging after filament change will be done inside objects' infills. This may lower the amount of waste and decrease the print time. If the walls are printed with transparent filament, the mixed color infill will be seen outside. It will not take effect, unless the prime tower is enabled."""
  flush_into_support: coerce.Bool | None = None
  """Purging after filament change will be done inside objects' support. This may lower the amount of waste and decrease the print time. It will not take effect, unless the prime tower is enabled."""
  flush_into_objects: coerce.Bool | None = None
  """This object will be used to purge the nozzle after a filament change to save filament and decrease the print time. Colors of the objects will be mixed as a result. It will not take effect unless the prime tower is enabled."""
  wipe_tower_bridging: coerce.Float | None = None
  """Maximal distance between supports on sparse infill sections."""
  wipe_tower_extra_spacing: coerce.Percent | None = None
  """Spacing of purge lines on the wipe tower."""
  wipe_tower_extra_flow: coerce.Percent | None = None
  """Extra flow used for the purging lines on the wipe tower. This makes the purging lines thicker or narrower than they normally would be. The spacing is adjusted automatically."""
  reduce_crossing_wall: coerce.Bool | None = None
  """Detour to avoid traveling across walls, which may cause blobs on the surface."""
  max_travel_detour_distance: coerce.FloatOrPercent | None = None
  """Maximum detour distance for avoiding crossing wall. Don't detour if the detour distance is larger than this value. Detour length could be specified either as an absolute value or as percentage (for example 50%) of a direct travel path. Zero to disable."""
  bridge_density: coerce.Percent | None = None
  """
  Controls the density (spacing) of external bridge lines. Default is 100%.

  Lower density external bridges can help improve reliability as there is more space for air to circulate around the extruded bridge, improving its cooling speed. Minimum is 10%.

  Higher densities can produce smoother bridge surfaces, as overlapping lines provide additional support during printing. Maximum is 120%.
  Note: Bridge density that is too high can cause warping or overextrusion.
  """
  internal_bridge_density: coerce.Percent | None = None
  """
  Controls the density (spacing) of internal bridge lines. 100% means solid bridge. Default is 100%.

  Lower density internal bridges can help reduce top surface pillowing and improve internal bridge reliability as there is more space for air to circulate around the extruded bridge, improving its cooling speed.

  This option works particularly well when combined with the second internal bridge over infill option, further improving internal bridging structure before solid infill is extruded.
  """
  bridge_flow: coerce.Float | None = None
  """
  Decrease this value slightly (for example 0.9) to reduce the amount of material for bridge, to improve sag.

  The actual bridge flow used is calculated by multiplying this value with the filament flow ratio, and if set, the object's flow ratio.
  """
  internal_bridge_flow: coerce.Float | None = None
  """
  This value governs the thickness of the internal bridge layer. This is the first layer over sparse infill. Decrease this value slightly (for example 0.9) to improve surface quality over sparse infill.

  The actual internal bridge flow used is calculated by multiplying this value with the bridge flow ratio, the filament flow ratio, and if set, the object's flow ratio.
  """
  top_solid_infill_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for top solid infill. You can decrease it slightly to have smooth surface finish.

  The actual top surface flow used is calculated by multiplying this value with the filament flow ratio, and if set, the object's flow ratio.
  """
  bottom_solid_infill_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for bottom solid infill.

  The actual bottom solid infill flow used is calculated by multiplying this value with the filament flow ratio, and if set, the object's flow ratio.
  """
  set_other_flow_ratios: coerce.Bool | None = None
  """Change flow ratios for other extrusion path types."""
  first_layer_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material on the first layer for the extrusion path roles listed in this section.

  For the first layer, the actual flow ratio for each path role (does not affect brims and skirts) will be multiplied by this value.
  """
  outer_wall_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for outer walls.

  The actual outer wall flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  inner_wall_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for inner walls.

  The actual inner wall flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  overhang_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for overhangs.

  The actual overhang flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  sparse_infill_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for sparse infill.

  The actual sparse infill flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  internal_solid_infill_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for internal solid infill.

  The actual internal solid infill flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  gap_fill_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for filling the gaps.

  The actual gap filling flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  support_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for support.

  The actual support flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  support_interface_flow_ratio: coerce.Float | None = None
  """
  This factor affects the amount of material for the support interface.

  The actual support interface flow used is calculated by multiplying this value by the filament flow ratio, and if set, the object's flow ratio.
  """
  precise_outer_wall: coerce.Bool | None = None
  """Improve shell precision by adjusting outer wall spacing. This also improves layer consistency. NOTE: This option will be ignored for outer-inner or inner-outer-inner wall sequences."""
  only_one_wall_top: coerce.Bool | None = None
  """Use only one wall on flat top surfaces, to give more space to the top infill pattern."""
  min_width_top_surface: coerce.FloatOrPercent | None = None
  """
  If a top surface has to be printed and it's partially covered by another layer, it won't be considered at a top layer where its width is below this value. This can be useful to not let the 'one perimeter on top' trigger on surface that should be covered only by perimeters. This value can be a mm or a % of the perimeter extrusion width.
  Warning: If enabled, artifacts can be created if you have some thin features on the next layer, like letters. Set this setting to 0 to remove these artifacts.
  """
  only_one_wall_first_layer: coerce.Bool | None = None
  """Use only one wall on first layer, to give more space to the bottom infill pattern."""
  extra_perimeters_on_overhangs: coerce.Bool | None = None
  """Create additional perimeter paths over steep overhangs and areas where bridges cannot be anchored."""
  overhang_reverse: coerce.Bool | None = None
  """
  Extrude perimeters that have a part over an overhang in the reverse direction on even layers. This alternating pattern can drastically improve steep overhangs.

  This setting can also help reduce part warping due to the reduction of stresses in the part walls.
  """
  overhang_reverse_internal_only: coerce.Bool | None = None
  """
  Apply the reverse perimeters logic only on internal perimeters.

  This setting greatly reduces part stresses as they are now distributed in alternating directions. This should reduce part warping while also maintaining external wall quality. This feature can be very useful for warp prone material, like ABS/ASA, and also for elastic filaments, like TPU and Silk PLA. It can also help reduce warping on floating regions over supports.

  For this setting to be the most effective, it is recommended to set the Reverse Threshold to 0 so that all internal walls print in alternating directions on even layers irrespective of their overhang degree.
  """
  counterbore_hole_bridging: Annotated[CounterboreHoleBridgingOption, coerce.EnumValue] | None = None
  """
  This option creates bridges for counterbore holes, allowing them to be printed without support. Available modes include:
  1. None: No bridge is created
  2. Partially Bridged: Only a part of the unsupported area will be bridged
  3. Sacrificial Layer: A full sacrificial bridge layer is created
  """
  overhang_reverse_threshold: coerce.FloatOrPercent | None = None
  """
  Number of mm the overhang need to be for the reversal to be considered useful. Can be a % of the perimeter width.
  Value 0 enables reversal on every even layers regardless.
  When Detect overhang wall is not enabled, this option is ignored and reversal happens on every even layers regardless.
  """
  thick_bridges: coerce.Bool | None = None
  """If enabled, bridges are more reliable, can bridge longer distances, but may look worse. If disabled, bridges look better but are reliable just for shorter bridged distances."""
  thick_internal_bridges: coerce.Bool | None = None
  """If enabled, thick internal bridges will be used. It's usually recommended to have this feature turned on. However, consider turning it off if you are using large nozzles."""
  enable_extra_bridge_layer: Annotated[EnableExtraBridgeLayer, coerce.EnumValue] | None = None
  """
  This option enables the generation of an extra bridge layer over internal and/or external bridges.

  Extra bridge layers help improve bridge appearance and reliability, as the solid infill is better supported. This is especially useful in fast printers, where the bridge and solid infill speeds vary greatly. The extra bridge layer results in reduced pillowing on top surfaces, as well as reduced separation of the external bridge layer from its surrounding perimeters.

  It is generally recommended to set this to at least 'External bridge only', unless specific issues with the sliced model are found.

  Options:
  1. Disabled - does not generate second bridge layers. This is the default and is set for compatibility purposes
  2. External bridge only - generates second bridge layers for external-facing bridges only. Please note that small bridges that are shorter or narrower than the set number of perimeters will be skipped as they would not benefit from a second bridge layer. If generated, the second bridge layer will be extruded parallel to the first bridge layer to reinforce the bridge strength
  3. Internal bridge only - generates second bridge layers for internal bridges over sparse infill only. Please note that the internal bridges count towards the top shell layer count of your model. The second internal bridge layer will be extruded as close to perpendicular to the first as possible. If multiple regions in the same island, with varying bridge angles are present, the last region of that island will be selected as the angle reference
  4. Apply to all - generates second bridge layers for both internal and external-facing bridges
  """
  dont_filter_internal_bridges: Annotated[InternalBridgeFilter, coerce.EnumValue] | None = None
  """
  This option can help reduce pillowing on top surfaces in heavily slanted or curved models.
  By default, small internal bridges are filtered out and the internal solid infill is printed directly over the sparse infill. This works well in most cases, speeding up printing without too much compromise on top surface quality.
  However, in heavily slanted or curved models, especially where too low a sparse infill density is used, this may result in curling of the unsupported solid infill, causing pillowing.
  Enabling limited filtering or no filtering will print internal bridge layer over slightly unsupported internal solid infill. The options below control the sensitivity of the filtering, i.e. they control where internal bridges are created:
  1. Filter - enables this option. This is the default behavior and works well in most cases
  2. Limited filtering - creates internal bridges on heavily slanted surfaces while avoiding unnecessary bridges. This works well for most difficult models
  3. No filtering - creates internal bridges on every potential internal overhang. This option is useful for heavily slanted top surface models; however, in most cases, it creates too many 
  """
  outer_wall_line_width: coerce.FloatOrPercent | None = None
  """Line width of outer wall. If expressed as a %, it will be computed over the nozzle diameter."""
  wall_sequence: Annotated[WallSequence, coerce.EnumValue] | None = None
  """
  Print sequence of the internal (inner) and external (outer) walls.

  Use Inner/Outer for best overhangs. This is because the overhanging walls can adhere to a neighbouring perimeter while printing. However, this option results in slightly reduced surface quality as the external perimeter is deformed by being squashed to the internal perimeter.

  Use Inner/Outer/Inner for the best external surface finish and dimensional accuracy as the external wall is printed undisturbed from an internal perimeter. However, overhang performance will reduce as there is no internal perimeter to print the external wall against. This option requires a minimum of 3 walls to be effective as it prints the internal walls from the 3rd perimeter onwards first, then the external perimeter and, finally, the first internal perimeter. This option is recommended against the Outer/Inner option in most cases.

  Use Outer/Inner for the same external wall quality and dimensional accuracy benefits of Inner/Outer/Inner option. However, the Z seams will appear less consistent as the first extrusion of a new layer starts on a visible surface.
  """
  is_infill_first: coerce.Bool | None = None
  """
  Order of wall/infill. When the tickbox is unchecked the walls are printed first, which works best in most cases.

  Printing infill first may help with extreme overhangs as the walls have the neighbouring infill to adhere to. However, the infill will slightly push out the printed walls where it is attached to them, resulting in a worse external surface finish. It can also cause the infill to shine through the external surfaces of the part.
  """
  wall_direction: Annotated[WallDirection, coerce.EnumValue] | None = None
  """
  The direction which the contour wall loops are extruded when looking down from the top.
  Holes are printed in the opposite direction to the contour to maintain alignment with layers whose contour polygons are incomplete and change direction, also partially forming the contour of a hole.

  This option will be disabled if spiral vase mode is enabled.
  """
  print_flow_ratio: coerce.Float | None = None
  """
  The material may have volumetric change after switching between molten and crystalline states. This setting changes all extrusion flow of this filament in G-code proportionally. The recommended value range is between 0.95 and 1.05. You may be able to tune this value to get a nice flat surface if there is slight overflow or underflow.

  The final object flow ratio is this value multiplied by the filament flow ratio.
  """
  line_width: coerce.FloatOrPercent | None = None
  """Default line width if other line widths are set to 0. If expressed as a %, it will be computed over the nozzle diameter."""
  initial_layer_line_width: coerce.FloatOrPercent | None = None
  """Line width of the first layer. If expressed as a %, it will be computed over the nozzle diameter."""
  initial_layer_print_height: coerce.Float | None = None
  """Height of the first layer. Making the first layer height thicker can improve build plate adhesion."""
  precise_z_height: coerce.Bool | None = None
  """Enable this to get precise Z height of object after slicing. It will get the precise object height by fine-tuning the layer heights of the last few layers. Note that this is an experimental parameter."""
  enable_arc_fitting: coerce.Bool | None = None
  """
  Enable this to get a G-code file which has G2 and G3 moves. The fitting tolerance is same as the resolution.

  Note: For Klipper machines, this option is recommended to be disabled. Klipper does not benefit from arc commands as these are split again into line segments by the firmware. This results in a reduction in surface quality as line segments are converted to arcs by the slicer and then back to line segments by the firmware.
  """
  sparse_infill_line_width: coerce.FloatOrPercent | None = None
  """Line width of internal sparse infill. If expressed as a %, it will be computed over the nozzle diameter."""
  ironing_type: Annotated[IroningType, coerce.EnumValue] | None = None
  """Ironing is using small flow to print on same height of surface again to make flat surface more smooth. This setting controls which layer being ironed."""
  ironing_pattern: Annotated[IroningPattern, coerce.EnumValue] | None = None
  """The pattern that will be used when ironing."""
  ironing_flow: coerce.Percent | None = None
  """The amount of material to extrude during ironing. Relative to flow of normal layer height. Too high value results in overextrusion on the surface."""
  ironing_spacing: coerce.Float | None = None
  """The distance between the lines of ironing."""
  ironing_inset: coerce.Float | None = None
  """The distance to keep from the edges. A value of 0 sets this to half of the nozzle diameter."""
  ironing_angle: coerce.Float | None = None
  """The angle of ironing lines offset from the top surface."""
  ironing_angle_fixed: coerce.Bool | None = None
  """Use a fixed absolute angle for ironing."""
  zaa_enabled: coerce.Bool | None = None
  """Enable Z-layer contouring (aka Z-layer anti-aliasing)."""
  zaa_minimize_perimeter_height: coerce.Float | None = None
  """
  Reduce the height of top-surface perimeters to match the model edge height.
  Affects perimeters with a slope less than this angle (degrees).
  A reasonable value is 35. Set to 0 to disable.
  """
  zaa_dont_alternate_fill_direction: coerce.Bool | None = None
  """Disable alternating fill direction when using Z contouring."""
  zaa_min_z: coerce.Float | None = None
  """
  Minimum Z-layer height.
  Also controls the slicing plane.
  """
  small_area_infill_flow_compensation: coerce.Bool | None = None
  """Enable flow compensation for small infill areas."""
  small_area_infill_flow_compensation_model: coerce.Strs | None = None
  """Flow Compensation Model, used to adjust the flow for small infill areas. The model is expressed as a comma separated pair of values for extrusion length and flow correction factor. Each pair is on a separate line, followed by a semicolon, in the following format: \\\\\\"1.234, 5.678;\\\\\\\""""
  make_overhang_printable: coerce.Bool | None = None
  """Modify the geometry to print overhangs without support material."""
  make_overhang_printable_angle: coerce.Float | None = None
  """Maximum angle of overhangs to allow after making more steep overhangs printable.90° will not change the model at all and allow any overhang, while 0 will replace all overhangs with conical material."""
  make_overhang_printable_hole_size: coerce.Float | None = None
  """Maximum area of a hole in the base of the model before it's filled by conical material. A value of 0 will fill all the holes in the model base."""
  detect_overhang_wall: coerce.Bool | None = None
  """Detect the overhang percentage relative to line width and use different speed to print. For 100%% overhang, bridge speed is used."""
  inner_wall_line_width: coerce.FloatOrPercent | None = None
  """Line width of inner wall. If expressed as a %, it will be computed over the nozzle diameter."""
  resolution: coerce.Float | None = None
  """The G-code path is generated after simplifying the contour of models to avoid too many points and G-code lines. Smaller value means higher resolution and more time to slice."""
  seam_position: Annotated[SeamPosition, coerce.EnumValue] | None = None
  """The start position to print each part of outer wall."""
  staggered_inner_seams: coerce.Bool | None = None
  """This option causes the inner seams to be shifted backwards based on their depth, forming a zigzag pattern."""
  seam_gap: coerce.FloatOrPercent | None = None
  """
  In order to reduce the visibility of the seam in a closed loop extrusion, the loop is interrupted and shortened by a specified amount.
  This amount can be specified in millimeters or as a percentage of the current extruder diameter. The default value for this parameter is 10%.
  """
  seam_slope_type: Annotated[SeamScarfType, coerce.EnumValue] | None = None
  """Use scarf joint to minimize seam visibility and increase seam strength."""
  seam_slope_conditional: coerce.Bool | None = None
  """Apply scarf joints only to smooth perimeters where traditional seams do not conceal the seams at sharp corners effectively."""
  scarf_angle_threshold: coerce.Int | None = None
  """
  This option sets the threshold angle for applying a conditional scarf joint seam.
  If the maximum angle within the perimeter loop exceeds this value (indicating the absence of sharp corners), a scarf joint seam will be used. The default value is 155°.
  """
  scarf_overhang_threshold: coerce.Percent | None = None
  """This option determines the overhang threshold for the application of scarf joint seams. If the unsupported portion of the perimeter is less than this threshold, scarf joint seams will be applied. The default threshold is set at 40% of the external wall's width. Due to performance considerations, the degree of overhang is estimated."""
  scarf_joint_speed: coerce.FloatOrPercent | None = None
  """This option sets the printing speed for scarf joints. It is recommended to print scarf joints at a slow speed (less than 100 mm/s). It's also advisable to enable 'Extrusion rate smoothing' if the set speed varies significantly from the speed of the outer or inner walls. If the speed specified here is higher than the speed of the outer or inner walls, the printer will default to the slower of the two speeds. When specified as a percentage (e.g., 80%), the speed is calculated based on the respective outer or inner wall speed. The default value is set to 100%."""
  scarf_joint_flow_ratio: coerce.Float | None = None
  """This factor affects the amount of material for scarf joints."""
  seam_slope_start_height: coerce.FloatOrPercent | None = None
  """
  Start height of the scarf.
  This amount can be specified in millimeters or as a percentage of the current layer height. The default value for this parameter is 0.
  """
  seam_slope_entire_loop: coerce.Bool | None = None
  """The scarf extends to the entire length of the wall."""
  seam_slope_min_length: coerce.Float | None = None
  """Length of the scarf. Setting this parameter to zero effectively disables the scarf."""
  seam_slope_steps: coerce.Int | None = None
  """Minimum number of segments of each scarf."""
  seam_slope_inner_walls: coerce.Bool | None = None
  """Use scarf joint for inner walls as well."""
  role_based_wipe_speed: coerce.Bool | None = None
  """The wipe speed is determined by the speed of the current extrusion role. e.g. if a wipe action is executed immediately following an outer wall extrusion, the speed of the outer wall extrusion will be utilized for the wipe action."""
  wipe_on_loops: coerce.Bool | None = None
  """To minimize the visibility of the seam in a closed loop extrusion, a small inward movement is executed before the extruder leaves the loop."""
  wipe_before_external_loop: coerce.Bool | None = None
  """
  To minimize visibility of potential overextrusion at the start of an external perimeter when printing with Outer/Inner or Inner/Outer/Inner wall print order, the de-retraction is performed slightly on the inside from the start of the external perimeter. That way any potential over extrusion is hidden from the outside surface.

  This is useful when printing with Outer/Inner or Inner/Outer/Inner wall print order as in these modes it is more likely an external perimeter is printed immediately after a de-retraction move.
  """
  wipe_speed: coerce.FloatOrPercent | None = None
  """The wipe speed is determined by the speed setting specified in this configuration. If the value is expressed as a percentage (e.g. 80%), it will be calculated based on the travel speed setting above. The default value for this parameter is 80%."""
  internal_solid_infill_line_width: coerce.FloatOrPercent | None = None
  """Line width of internal solid infill. If expressed as a %, it will be computed over the nozzle diameter."""
  slice_closing_radius: coerce.Float | None = None
  """Cracks smaller than 2x gap closing radius are being filled during the triangle mesh slicing. The gap closing operation may reduce the final print resolution, therefore it is advisable to keep the value reasonably low."""
  support_line_width: coerce.FloatOrPercent | None = None
  """Line width of support. If expressed as a %, it will be computed over the nozzle diameter."""
  top_surface_line_width: coerce.FloatOrPercent | None = None
  """Line width for top surfaces. If expressed as a %, it will be computed over the nozzle diameter."""
  xy_hole_compensation: coerce.Float | None = None
  """Holes in objects will expand or contract in the XY plane by the configured value. Positive values make holes bigger, negative values make holes smaller. This function is used to adjust sizes slightly when the objects have assembling issues."""
  xy_contour_compensation: coerce.Float | None = None
  """Contours of objects will expand or contract in the XY plane by the configured value. Positive values make contours bigger, negative values make contours smaller. This function is used to adjust sizes slightly when the objects have assembling issues."""
  hole_to_polyhole: coerce.Bool | None = None
  """
  Search for almost-circular holes that span more than one layer and convert the geometry to polyholes. Use the nozzle size and the (biggest) diameter to compute the polyhole.
  See http://hydraraptor.blogspot.com/2011/02/polyholes.html
  """
  hole_to_polyhole_threshold: coerce.FloatOrPercent | None = None
  """
  Maximum defection of a point to the estimated radius of the circle.
  As cylinders are often exported as triangles of varying size, points may not be on the circle circumference. This setting allows you some leeway to broaden the detection.
  In mm or in % of the radius.
  """
  hole_to_polyhole_twisted: coerce.Bool | None = None
  """Rotate the polyhole every layer."""
  wall_generator: Annotated[PerimeterGeneratorType, coerce.EnumValue] | None = None
  """Classic wall generator produces walls with constant extrusion width and for very thin areas is used gap-fill. Arachne engine produces walls with variable extrusion width."""
  wall_transition_length: coerce.Percent | None = None
  """When transitioning between different numbers of walls as the part becomes thinner, a certain amount of space is allotted to split or join the wall segments. It's expressed as a percentage over nozzle diameter."""
  wall_transition_filter_deviation: coerce.Percent | None = None
  """Prevent transitioning back and forth between one extra wall and one less. This margin extends the range of extrusion widths which follow to [Minimum wall width - margin, 2 * Minimum wall width + margin]. Increasing this margin reduces the number of transitions, which reduces the number of extrusion starts/stops and travel time. However, large extrusion width variation can lead to under- or overextrusion problems. It's expressed as a percentage over nozzle diameter."""
  wall_transition_angle: coerce.Float | None = None
  """When to create transitions between even and odd numbers of walls. A wedge shape with an angle greater than this setting will not have transitions and no walls will be printed in the center to fill the remaining space. Reducing this setting reduces the number and length of these center walls, but may leave gaps or overextrude."""
  wall_distribution_count: coerce.Int | None = None
  """The number of walls, counted from the center, over which the variation needs to be spread. Lower values mean that the outer walls don't change in width."""
  min_feature_size: coerce.Percent | None = None
  """Minimum thickness of thin features. Model features that are thinner than this value will not be printed, while features thicker than than this value will be widened to the minimum wall width. It's expressed as a percentage over nozzle diameter."""
  min_length_factor: coerce.Float | None = None
  """
  Adjust this value to prevent short, unclosed walls from being printed, which could increase print time. Higher values remove more and longer walls.

  NOTE: Bottom and top surfaces will not be affected by this value to prevent visual gaps on the outside of the model. Adjust 'One wall threshold' in the Advanced settings below to adjust the sensitivity of what is considered a top-surface. 'One wall threshold' is only visible if this setting is set above the default value of 0.5, or if single-wall top surfaces is enabled.
  """
  wall_maximum_resolution: coerce.Float | None = None
  """This value determines the smallest wall line segment length in mm. The smaller you set this value, the more accurate and precise the walls will be."""
  wall_maximum_deviation: coerce.Float | None = None
  """The maximum deviation allowed when reducing the resolution for the 'Maximum wall resolution' setting. If you increase this, the print will be less accurate, but the G-Code will be smaller. 'Maximum wall deviation' limits 'Maximum wall resolution', so if the two conflict, 'Maximum wall deviation' takes precedence."""
  initial_layer_min_bead_width: coerce.Percent | None = None
  """The minimum wall width that should be used for the first layer is recommended to be set to the same size as the nozzle. This adjustment is expected to enhance adhesion."""
  min_bead_width: coerce.Percent | None = None
  """Width of the wall that will replace thin features (according to the Minimum feature size) of the model. If the Minimum wall width is thinner than the thickness of the feature, the wall will become as thick as the feature itself. It's expressed as a percentage over nozzle diameter."""
  enable_overhang_speed: coerce.Bool | None = None
  """Enable this option to slow printing down for different overhang degree."""
  slowdown_for_curled_perimeters: coerce.Bool | None = None
  """
  Enable this option to slow down printing in areas where perimeters may have curled upwards. For example, additional slowdown will be applied when printing overhangs on sharp corners like the front of the Benchy hull, reducing curling which compounds over multiple layers.

  It is generally recommended to have this option switched on unless your printer cooling is powerful enough or the print speed slow enough that perimeter curling does not happen. If printing with a high external perimeter speed, this parameter may introduce slight artifacts when slowing down due to the large variance in print speeds. If you notice artifacts, ensure your pressure advance is tuned correctly.

  Note: When this option is enabled, overhang perimeters are treated like overhangs, meaning the overhang speed is applied even if the overhanging perimeter is part of a bridge. For example, when the perimeters are 100% overhanging, with no wall supporting them from underneath, the 100% overhang speed will be applied.
  """
  overhang_1_4_speed: coerce.FloatOrPercent | None = None
  """10%"""
  overhang_2_4_speed: coerce.FloatOrPercent | None = None
  """25%"""
  overhang_3_4_speed: coerce.FloatOrPercent | None = None
  """50%"""
  overhang_4_4_speed: coerce.FloatOrPercent | None = None
  """75%"""
  bridge_speed: coerce.Float | None = None
  """
  Speed of the externally visible bridge extrusions.

  In addition, if Slow down for curled perimeters is disabled or Classic overhang mode is enabled, it will be the print speed of overhang walls that are supported by less than 13%, whether they are part of a bridge or an overhang.
  """
  internal_bridge_speed: coerce.FloatOrPercent | None = None
  """Speed of internal bridges. If the value is expressed as a percentage, it will be calculated based on the bridge_speed. Default value is 150%."""
  default_acceleration: coerce.Float | None = None
  """The default acceleration of both normal printing and travel except initial layer."""
  outer_wall_speed: coerce.Float | None = None
  """Speed of outer wall which is outermost and visible. It's used to be slower than inner wall speed to get better quality."""
  small_perimeter_speed: coerce.FloatOrPercent | None = None
  """This separate setting will affect the speed of perimeters having radius <= small_perimeter_threshold (usually holes). If expressed as percentage (for example: 80%) it will be calculated on the outer wall speed setting above. Set to zero for auto."""
  small_perimeter_threshold: coerce.Float | None = None
  """This sets the threshold for small perimeter length. Default threshold is 0mm."""
  inner_wall_acceleration: coerce.Float | None = None
  """Acceleration of inner walls."""
  travel_acceleration: coerce.Float | None = None
  """Acceleration of travel moves."""
  top_surface_acceleration: coerce.Float | None = None
  """Acceleration of top surface infill. Using a lower value may improve top surface quality."""
  outer_wall_acceleration: coerce.Float | None = None
  """Acceleration of outer wall. Using a lower value can improve quality."""
  bridge_acceleration: coerce.FloatOrPercent | None = None
  """Acceleration of bridges. If the value is expressed as a percentage (e.g. 50%), it will be calculated based on the outer wall acceleration."""
  sparse_infill_acceleration: coerce.FloatOrPercent | None = None
  """Acceleration of sparse infill. If the value is expressed as a percentage (e.g. 100%), it will be calculated based on the default acceleration."""
  internal_solid_infill_acceleration: coerce.FloatOrPercent | None = None
  """Acceleration of internal solid infill. If the value is expressed as a percentage (e.g. 100%), it will be calculated based on the default acceleration."""
  initial_layer_acceleration: coerce.Float | None = None
  """Acceleration of the first layer. Using a lower value can improve build plate adhesion."""
  initial_layer_travel_acceleration: coerce.FloatOrPercent | None = None
  """
  Travel acceleration of first layer.
  The percentage value is relative to Travel Acceleration.
  """
  accel_to_decel_enable: coerce.Bool | None = None
  """Klipper's max_accel_to_decel will be adjusted automatically."""
  accel_to_decel_factor: coerce.Percent | None = None
  """Klipper's max_accel_to_decel will be adjusted to this %% of acceleration."""
  default_jerk: coerce.Float | None = None
  """Default jerk."""
  default_junction_deviation: coerce.Float | None = None
  """Marlin Firmware Junction Deviation (replaces the traditional XY Jerk setting)."""
  outer_wall_jerk: coerce.Float | None = None
  """Jerk of outer walls."""
  inner_wall_jerk: coerce.Float | None = None
  """Jerk of inner walls."""
  top_surface_jerk: coerce.Float | None = None
  """Jerk for top surface."""
  infill_jerk: coerce.Float | None = None
  """Jerk for infill."""
  initial_layer_jerk: coerce.Float | None = None
  """Jerk for the first layer."""
  travel_jerk: coerce.Float | None = None
  """Jerk for travel."""
  initial_layer_travel_jerk: coerce.FloatOrPercent | None = None
  """
  Travel jerk of first layer.
  The percentage value is relative to Travel Jerk.
  """
  initial_layer_speed: coerce.Float | None = None
  """Speed of the first layer except the solid infill part."""
  initial_layer_infill_speed: coerce.Float | None = None
  """Speed of solid infill part of the first layer."""
  initial_layer_travel_speed: coerce.FloatOrPercent | None = None
  """Travel speed of the first layer."""
  slow_down_layers: coerce.Int | None = None
  """The first few layers are printed slower than normal. The speed is gradually increased in a linear fashion over the specified number of layers."""
  gap_infill_speed: coerce.Float | None = None
  """Speed of gap infill. Gap usually has irregular line width and should be printed more slowly."""
  sparse_infill_speed: coerce.Float | None = None
  """Speed of internal sparse infill."""
  ironing_speed: coerce.Float | None = None
  """Print speed of ironing lines."""
  max_volumetric_extrusion_rate_slope: coerce.Float | None = None
  """
  This parameter smooths out sudden extrusion rate changes that happen when the printer transitions from printing a high flow (high speed/larger width) extrusion to a lower flow (lower speed/smaller width) extrusion and vice versa.

  It defines the maximum rate by which the extruded volumetric flow in mm³/s can change over time. Higher values mean higher extrusion rate changes are allowed, resulting in faster speed transitions.

  A value of 0 disables the feature.

  For a high speed, high flow direct drive printer (like the Bambu lab or Voron) this value is usually not needed. However it can provide some marginal benefit in certain cases where feature speeds vary greatly. For example, when there are aggressive slowdowns due to overhangs. In these cases a high value of around 300-350 mm³/s² is recommended as this allows for just enough smoothing to assist pressure advance achieve a smoother flow transition.

  For slower printers without pressure advance, the value should be set much lower. A value of 10-15 mm³/s² is a good starting point for direct drive extruders and 5-10 mm³/s² for Bowden style.

  This feature is known as Pressure Equalizer in Prusa slicer.

  Note: this parameter disables arc fitting.
  """
  max_volumetric_extrusion_rate_slope_segment_length: coerce.Float | None = None
  """
  A lower value results in smoother extrusion rate transitions. However, this results in a significantly larger G-code file and more instructions for the printer to process.

  Default value of 3 works well for most cases. If your printer is stuttering, increase this value to reduce the number of adjustments made.

  Allowed values: 0.5-5
  """
  extrusion_rate_smoothing_external_perimeter_only: coerce.Bool | None = None
  """Applies extrusion rate smoothing only on external perimeters and overhangs. This can help reduce artefacts due to sharp speed transitions on externally visible overhangs without impacting the print speed of features that will not be visible to the user."""
  inner_wall_speed: coerce.Float | None = None
  """Speed of inner wall."""
  internal_solid_infill_speed: coerce.Float | None = None
  """Speed of internal solid infill, not the top and bottom surface."""
  support_interface_speed: coerce.Float | None = None
  """Speed of support interface."""
  support_speed: coerce.Float | None = None
  """Speed of support."""
  top_surface_speed: coerce.Float | None = None
  """Speed of top surface infill which is solid."""
  travel_speed: coerce.Float | None = None
  """Speed of travel which is faster and without extrusion."""
  bridge_no_support: coerce.Bool | None = None
  """Don't support the whole bridge area which make support very large. Bridges can usually be printed directly without support if not very long."""
  max_bridge_length: coerce.Float | None = None
  """Max length of bridges that don't need support. Set it to 0 if you want all bridges to be supported, and set it to a very large value if you don't want any bridges to be supported."""
  raft_contact_distance: coerce.Float | None = None
  """Z gap between raft and object. If Support Top Z Distance is 0, this value is ignored and the object is printed in direct contact with the raft (no gap)."""
  raft_first_layer_density: coerce.Percent | None = None
  """Density of the first raft or support layer."""
  raft_first_layer_expansion: coerce.Float | None = None
  """Expand the first raft or support layer to improve bed plate adhesion."""
  raft_layers: coerce.Int | None = None
  """Object will be raised by this number of support layers. Use this function to avoid warping when printing ABS."""
  enable_support: coerce.Bool | None = None
  """Enable support generation."""
  support_type: Annotated[SupportType, coerce.EnumValue] | None = None
  """Normal (auto) and Tree (auto) are used to generate support automatically. If Normal (manual) or Tree (manual) is selected, only support enforcers are generated."""
  support_object_xy_distance: coerce.Float | None = None
  """XY separation between an object and its support."""
  support_object_first_layer_gap: coerce.Float | None = None
  """XY separation between an object and its support at the first layer."""
  support_angle: coerce.Float | None = None
  """Use this setting to rotate the support pattern on the horizontal plane."""
  support_on_build_plate_only: coerce.Bool | None = None
  """Don't create support on model surface, only on build plate."""
  support_critical_regions_only: coerce.Bool | None = None
  """Only create support for critical regions including sharp tail, cantilever, etc."""
  support_remove_small_overhang: coerce.Bool | None = None
  """Ignore small overhangs that possibly don't require support."""
  support_top_z_distance: coerce.Float | None = None
  """Z gap between the support's top and object."""
  support_bottom_z_distance: coerce.Float | None = None
  """Z gap between the object and the support bottom. If Support Top Z Distance is 0 and the bottom has interface layers, this value is ignored and the support is printed in direct contact with the object (no gap)."""
  support_filament: coerce.Int | None = None
  """Filament to print support base and raft. \\\\\\"Default\\\\\\" means no specific filament for support and current filament is used."""
  support_interface_not_for_body: coerce.Bool | None = None
  """Avoid using support interface filament to print support base if possible."""
  support_interface_filament: coerce.Int | None = None
  """Filament to print support interface. \\\\\\"Default\\\\\\" means no specific filament for support interface and current filament is used."""
  support_interface_top_layers: coerce.Int | None = None
  """Number of top interface layers."""
  support_interface_bottom_layers: coerce.Int | None = None
  """Number of bottom interface layers."""
  support_interface_spacing: coerce.Float | None = None
  """
  Spacing of interface lines. Zero means solid interface.
  Force using solid interface when support ironing is enabled.
  """
  support_bottom_interface_spacing: coerce.Float | None = None
  """Spacing of bottom interface lines. Zero means solid interface."""
  support_base_pattern: Annotated[SupportMaterialPattern, coerce.EnumValue] | None = None
  """
  Line pattern of support.

  The Default option for Tree supports is Hollow, which means no base pattern. For other support types, the Default option is the Rectilinear pattern.

  NOTE: For Organic supports, the two walls are supported only with the Hollow/Default base pattern. The Lightning base pattern is supported only by Tree Slim/Strong/Hybrid supports. For the other support types, the Rectilinear will be used instead of Lightning.
  """
  support_interface_pattern: Annotated[SupportMaterialInterfacePattern, coerce.EnumValue] | None = None
  """Line pattern of support interface. Default pattern for non-soluble support interface is Rectilinear, while default pattern for soluble support interface is Concentric."""
  support_base_pattern_spacing: coerce.Float | None = None
  """Spacing between support lines."""
  support_expansion: coerce.Float | None = None
  """Expand (+) or shrink (-) the horizontal span of normal support."""
  support_style: Annotated[SupportMaterialStyle, coerce.EnumValue] | None = None
  """
  Style and shape of the support. For normal support, projecting the supports into a regular grid will create more stable supports (default), while snug support towers will save material and reduce object scarring.
  For tree support, slim and organic style will merge branches more aggressively and save a lot of material (default organic), while hybrid style will create similar structure to normal support under large flat overhangs.
  """
  independent_support_layer_height: coerce.Bool | None = None
  """Support layer uses layer height independent with object layer. This is to support customizing Z-gap and save print time. This option will be invalid when the prime tower is enabled."""
  support_threshold_angle: coerce.Int | None = None
  """
  Support will be generated for overhangs whose slope angle is below the threshold. The smaller this value is, the steeper the overhang that can be printed without support.
  Note: If set to 0, normal supports use the Threshold overlap instead, while tree supports fall back to a default value of 30.
  """
  support_threshold_overlap: coerce.FloatOrPercent | None = None
  """If threshold angle is zero, support will be generated for overhangs whose overlap is below the threshold. The smaller this value is, the steeper the overhang that can be printed without support."""
  tree_support_branch_angle: coerce.Float | None = None
  """This setting determines the maximum overhang angle that the branches of tree support are allowed to make. If the angle is increased, the branches can be printed more horizontally, allowing them to reach farther."""
  tree_support_branch_angle_organic: coerce.Float | None = None
  """This setting determines the maximum overhang angle that the branches of tree support are allowed to make. If the angle is increased, the branches can be printed more horizontally, allowing them to reach farther."""
  tree_support_angle_slow: coerce.Float | None = None
  """The preferred angle of the branches, when they do not have to avoid the model. Use a lower angle to make them more vertical and more stable. Use a higher angle for branches to merge faster."""
  tree_support_branch_distance: coerce.Float | None = None
  """This setting determines the distance between neighboring tree support nodes."""
  tree_support_branch_distance_organic: coerce.Float | None = None
  """This setting determines the distance between neighboring tree support nodes."""
  tree_support_top_rate: coerce.Percent | None = None
  """Adjusts the density of the support structure used to generate the tips of the branches. A higher value results in better overhangs but the supports are harder to remove, thus it is recommended to enable top support interfaces instead of a high branch density value if dense interfaces are needed."""
  tree_support_auto_brim: coerce.Bool | None = None
  """Enabling this option means the width of the brim for tree support will be automatically calculated."""
  tree_support_brim_width: coerce.Float | None = None
  """Distance from tree branch to the outermost brim line."""
  tree_support_tip_diameter: coerce.Float | None = None
  """Branch tip diameter for organic supports."""
  tree_support_branch_diameter: coerce.Float | None = None
  """This setting determines the initial diameter of support nodes."""
  tree_support_branch_diameter_angle: coerce.Float | None = None
  """The angle of the branches' diameter as they gradually become thicker towards the bottom. An angle of 0 will cause the branches to have uniform thickness over their length. A bit of an angle can increase stability of the organic support."""
  tree_support_branch_diameter_organic: coerce.Float | None = None
  """This setting determines the initial diameter of support nodes."""
  tree_support_wall_count: coerce.Int | None = None
  """This setting specifies the count of support walls in the range of [0,2]. 0 means auto."""
  support_ironing: coerce.Bool | None = None
  """Ironing is using small flow to print on same height of support interface again to make it more smooth. This setting controls whether support interface being ironed. When enabled, support interface will be extruded as solid too."""
  support_ironing_pattern: Annotated[IroningPattern, coerce.EnumValue] | None = None
  """The pattern that will be used when ironing."""
  support_ironing_flow: coerce.Percent | None = None
  """The amount of material to extrude during ironing. Relative to flow of normal support interface layer height. Too high value results in overextrusion on the surface."""
  support_ironing_spacing: coerce.Float | None = None
  """The distance between the lines of ironing."""
  bottom_shell_layers: coerce.Int | None = None
  """This is the number of solid layers of bottom shell, including the bottom surface layer. When the thickness calculated by this value is thinner than bottom shell thickness, the bottom shell layers will be increased."""
  bottom_shell_thickness: coerce.Float | None = None
  """The number of bottom solid layers is increased when slicing if the thickness calculated by bottom shell layers is thinner than this value. This can avoid having too thin shell when layer height is small. 0 means that this setting is disabled and thickness of bottom shell is absolutely determined by bottom shell layers."""
  gap_fill_target: Annotated[GapFillTarget, coerce.EnumValue] | None = None
  """
  Enables gap fill for the selected solid surfaces. The minimum gap length that will be filled can be controlled from the filter out tiny gaps option below.

  Options:
  1. Everywhere: Applies gap fill to top, bottom and internal solid surfaces for maximum strength
  2. Top and Bottom surfaces: Applies gap fill to top and bottom surfaces only, balancing print speed, reducing potential over extrusion in the solid infill and making sure the top and bottom surfaces have no pinhole gaps
  3. Nowhere: Disables gap fill for all solid infill areas

  Note that if using the classic perimeter generator, gap fill may also be generated between perimeters, if a full width line cannot fit between them. That perimeter gap fill is not controlled by this setting.

  If you would like all gap fill, including the classic perimeter generated one, removed, set the filter out tiny gaps value to a large number, like 999999.

  However this is not advised, as gap fill between perimeters is contributing to the model's strength. For models where excessive gap fill is generated between perimeters, a better option would be to switch to the arachne wall generator and use this option to control whether the cosmetic top and bottom surface gap fill is generated.
  """
  bridge_angle: coerce.Float | None = None
  """Bridging angle override. If left to zero, the bridging angle will be calculated automatically. Otherwise the provided angle will be used for external bridges. Use 180° for zero angle."""
  internal_bridge_angle: coerce.Float | None = None
  """
  Internal bridging angle override. If left to zero, the bridging angle will be calculated automatically. Otherwise the provided angle will be used for internal bridges. Use 180° for zero angle.

  It is recommended to leave it at 0 unless there is a specific model need not to.
  """
  ensure_vertical_shell_thickness: Annotated[EnsureVerticalShellThickness, coerce.EnumValue] | None = None
  """
  Add solid infill near sloping surfaces to guarantee the vertical shell thickness (top+bottom solid layers)
  None: No solid infill will be added anywhere. Caution: Use this option carefully if your model has sloped surfaces
  Critical Only: Avoid adding solid infill for walls
  Moderate: Add solid infill for heavily sloping surfaces only
  All: Add solid infill for all suitable sloping surfaces
  Default value is All.
  """
  top_surface_pattern: Annotated[TopSurfacePattern, coerce.EnumValue] | None = None
  """Line pattern of top surface infill."""
  bottom_surface_pattern: Annotated[TopSurfacePattern, coerce.EnumValue] | None = None
  """Line pattern of bottom surface infill, not bridge infill."""
  internal_solid_infill_pattern: Annotated[TopSurfacePattern, coerce.EnumValue] | None = None
  """Line pattern of internal solid infill. if the detect narrow internal solid infill be enabled, the concentric pattern will be used for the small area."""
  infill_direction: coerce.Float | None = None
  """Angle for sparse infill pattern, which controls the start or main direction of line."""
  solid_infill_direction: coerce.Float | None = None
  """Angle for solid infill pattern, which controls the start or main direction of line."""
  sparse_infill_density: coerce.Percent | None = None
  """Density of internal sparse infill, 100% turns all sparse infill into solid infill and internal solid infill pattern will be used."""
  align_infill_direction_to_model: coerce.Bool | None = None
  """Aligns infill and surface fill directions to follow the model's orientation on the build plate. When enabled, fill directions rotate with the model to maintain optimal strength characteristics."""
  extra_solid_infills: coerce.Str | None = None
  """Insert solid infill at specific layers. Use N to insert every Nth layer, N#K to insert K consecutive solid layers every N layers (K is optional, e.g. '5#' equals '5#1'), or a comma-separated list (e.g. 1,7,9) to insert at explicit layers. Layers are 1-based."""
  fill_multiline: coerce.Int | None = None
  """Using multiple lines for the infill pattern, if supported by infill pattern."""
  gyroid_optimized: coerce.Bool | None = None
  """Tightens the gyroid wave along the Z (vertical) axis at low infill density to shorten the effective vertical column length and improve Z-axis compression buckling resistance. Filament use is preserved. No effect at ~30% sparse infill density and above. Only applies when Sparse infill pattern is set to Gyroid."""
  sparse_infill_pattern: Annotated[SparseInfillPattern, coerce.EnumValue] | None = None
  """Line pattern for internal sparse infill."""
  lateral_lattice_angle_1: coerce.Float | None = None
  """The angle of the first set of Lateral lattice elements in the Z direction. Zero is vertical."""
  lateral_lattice_angle_2: coerce.Float | None = None
  """The angle of the second set of Lateral lattice elements in the Z direction. Zero is vertical."""
  infill_overhang_angle: coerce.Float | None = None
  """The angle of the infill angled lines. 60° will result in a pure honeycomb."""
  infill_anchor: coerce.FloatOrPercent | None = None
  """
  Connect an infill line to an internal perimeter with a short segment of an additional perimeter. If expressed as percentage (example: 15%) it is calculated over infill extrusion width. Orca Slicer tries to connect two close infill lines to a short perimeter segment. If no such perimeter segment shorter than infill_anchor_max is found, the infill line is connected to a perimeter segment at just one side and the length of the perimeter segment taken is limited to this parameter, but no longer than anchor_length_max.
  Set this parameter to zero to disable anchoring perimeters connected to a single infill line.
  """
  infill_anchor_max: coerce.FloatOrPercent | None = None
  """
  Connect an infill line to an internal perimeter with a short segment of an additional perimeter. If expressed as percentage (example: 15%) it is calculated over infill extrusion width. Orca Slicer tries to connect two close infill lines to a short perimeter segment. If no such perimeter segment shorter than this parameter is found, the infill line is connected to a perimeter segment at just one side and the length of the perimeter segment taken is limited to infill_anchor, but no longer than this parameter.
  If set to 0, the old algorithm for infill connection will be used, it should create the same result as with 1000 & 0.
  """
  filter_out_gap_fill: coerce.Float | None = None
  """Don't print gap fill with a length is smaller than the threshold specified (in mm). This setting applies to top, bottom and solid infill and, if using the classic perimeter generator, to wall gap fill."""
  infill_combination: coerce.Bool | None = None
  """Automatically Combine sparse infill of several layers to print together to reduce time. Wall is still printed with original layer height."""
  infill_shift_step: coerce.Float | None = None
  """This parameter adds a slight displacement to each layer of infill to create a cross texture."""
  sparse_infill_rotate_template: coerce.Str | None = None
  """Rotate the sparse infill direction per layer using a template of angles. Enter comma-separated degrees (e.g., '0,30,60,90'). Angles are applied in order by layer and repeat when the list ends. Advanced syntax is supported: '+5' rotates +5° every layer; '+5#5' rotates +5° every 5 layers. See the Wiki for details. """
  solid_infill_rotate_template: coerce.Str | None = None
  """This parameter adds a rotation of solid infill direction to each layer according to the specified template. The template is a comma-separated list of angles in degrees, e.g. '0,90'. The first angle is applied to the first layer, the second angle to the second layer, and so on. If there are more layers than angles, the angles will be repeated. Note that not all solid infill patterns support rotation."""
  skeleton_infill_density: coerce.Percent | None = None
  """The remaining part of the model contour after removing a certain depth from the surface is called the skeleton. This parameter is used to adjust the density of this section. When two regions have the same sparse infill settings but different skeleton densities, their skeleton areas will develop overlapping sections. Default is as same as infill density."""
  skin_infill_density: coerce.Percent | None = None
  """The portion of the model's outer surface within a certain depth range is called the skin. This parameter is used to adjust the density of this section. When two regions have the same sparse infill settings but different skin densities, this area will not be split into two separate regions. Default is as same as infill density."""
  skin_infill_depth: coerce.Float | None = None
  """The parameter sets the depth of skin."""
  infill_lock_depth: coerce.Float | None = None
  """The parameter sets the overlapping depth between the interior and skin."""
  skin_infill_line_width: coerce.FloatOrPercent | None = None
  """Adjust the line width of the selected skin paths."""
  skeleton_infill_line_width: coerce.FloatOrPercent | None = None
  """Adjust the line width of the selected skeleton paths."""
  symmetric_infill_y_axis: coerce.Bool | None = None
  """If the model has two parts that are symmetric about the Y axis, and you want these parts to have symmetric textures, please click this option on one of the parts."""
  infill_combination_max_layer_height: coerce.FloatOrPercent | None = None
  """
  Maximum layer height for the combined sparse infill.

  Set it to 0 or 100% to use the nozzle diameter (for maximum reduction in print time) or a value of ~80% to maximize sparse infill strength.

  The number of layers over which infill is combined is derived by dividing this value with the layer height and rounded down to the nearest decimal.

  Use either absolute mm values (eg. 0.32mm for a 0.4mm nozzle) or % values (eg 80%). This value must not be larger than the nozzle diameter.
  """
  infill_wall_overlap: coerce.Percent | None = None
  """Infill area is enlarged slightly to overlap with wall for better bonding. The percentage value is relative to line width of sparse infill. Set this value to ~10-15% to minimize potential over extrusion and accumulation of material resulting in rough top surfaces."""
  top_bottom_infill_wall_overlap: coerce.Percent | None = None
  """Top solid infill area is enlarged slightly to overlap with wall for better bonding and to minimize the appearance of pinholes where the top infill meets the walls. A value of 25-30% is a good starting point, minimizing the appearance of pinholes. The percentage value is relative to line width of sparse infill."""
  wall_loops: coerce.Int | None = None
  """Number of walls of every layer."""
  alternate_extra_wall: coerce.Bool | None = None
  """
  This setting adds an extra wall to every other layer. This way the infill gets wedged vertically between the walls, resulting in stronger prints.

  When this option is enabled, the ensure vertical shell thickness option needs to be disabled.

  Using lightning infill together with this option is not recommended as there is limited infill to anchor the extra perimeters to.
  """
  minimum_sparse_infill_area: coerce.Float | None = None
  """Sparse infill areas smaller than this threshold value are replaced by internal solid infill."""
  detect_thin_wall: coerce.Bool | None = None
  """Detect thin walls which can't contain two line widths, and use single line to print. Maybe not printed very well, because it's not a closed loop."""
  top_shell_layers: coerce.Int | None = None
  """This is the number of solid layers of top shell, including the top surface layer. When the thickness calculated by this value is thinner than top shell thickness, the top shell layers will be increased."""
  top_shell_thickness: coerce.Float | None = None
  """The number of top solid layers is increased when slicing if the thickness calculated by top shell layers is thinner than this value. This can avoid having too thin shell when layer height is small. 0 means that this setting is disabled and thickness of top shell is absolutely determined by top shell layers."""
  top_surface_density: coerce.Percent | None = None
  """Density of top surface layer. A value of 100% creates a fully solid, smooth top layer. Reducing this value results in a textured top surface, according to the chosen top surface pattern. A value of 0% will result in only the walls on the top layer being created. Intended for aesthetic or functional purposes, not to fix issues such as over-extrusion."""
  bottom_surface_density: coerce.Percent | None = None
  """
  Density of the bottom surface layer. Intended for aesthetic or functional purposes, not to fix issues such as over-extrusion.
  WARNING: Lowering this value may negatively affect bed adhesion.
  """
  detect_narrow_internal_solid_infill: coerce.Bool | None = None
  """This option will auto-detect narrow internal solid infill areas. If enabled, the concentric pattern will be used for the area to speed up printing. Otherwise, the rectilinear pattern will be used by default."""

  def items(self) -> Iterator[tuple[str, str]]:
    """Yield ``(key, serialized_value)`` for every explicitly-set setting.

    Mirrors ``dict.items()``: each value is rendered to the exact string
    OrcaSlicer stores on disk. Known fields are serialized by their pydantic
    type; unknown ("extra") keys fall back to a best-effort conversion.
    """
    known = type(self).model_fields
    for name, value in self.model_dump(exclude_unset=True, exclude_none=True).items():
      yield name, value if name in known else coerce.coerce_generic(value)
