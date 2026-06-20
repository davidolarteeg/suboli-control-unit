#!/usr/bin/env python3
"""Extract normalized geometry from the SUBOLI KiCad board.

Primary extraction uses KiCad's pcbnew Python API. A narrow S-expression
fallback is included so the data can still be regenerated on machines where the
KiCad app bundle is present but its Python extension cannot be loaded.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_BOARD = Path("kicad/suboli_control.kicad_pcb")
DEFAULT_OUTPUT = Path("suboli_geometry.json")
KICAD_APP_SITE_PACKAGES = Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/"
    "Python.framework/Versions/3.9/lib/python3.9/site-packages"
)
EPSILON = 1e-9


def round_mm(value: float) -> float:
    rounded = round(float(value), 6)
    rounded_to_micron = round(rounded, 3)
    if abs(rounded - rounded_to_micron) <= 1e-6:
        return rounded_to_micron
    return rounded


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def circle_from_3_points(
    a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]
) -> tuple[tuple[float, float], float] | None:
    ax, ay = a
    bx, by = b
    cx, cy = c
    determinant = 2.0 * (
        ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)
    )

    if abs(determinant) < EPSILON:
        return None

    a_sq = ax * ax + ay * ay
    b_sq = bx * bx + by * by
    c_sq = cx * cx + cy * cy
    ux = (
        a_sq * (by - cy) + b_sq * (cy - ay) + c_sq * (ay - by)
    ) / determinant
    uy = (
        a_sq * (cx - bx) + b_sq * (ax - cx) + c_sq * (bx - ax)
    ) / determinant
    center = (ux, uy)
    return center, distance(center, a)


def normalized_angle(angle: float) -> float:
    return angle % (2.0 * math.pi)


def angle_on_ccw_arc(start: float, end: float, angle: float) -> bool:
    start = normalized_angle(start)
    end = normalized_angle(end)
    angle = normalized_angle(angle)

    if end < start:
        end += 2.0 * math.pi
    if angle < start:
        angle += 2.0 * math.pi

    return start - EPSILON <= angle <= end + EPSILON


def arc_points_for_bbox(
    start: tuple[float, float],
    mid: tuple[float, float],
    end: tuple[float, float],
) -> tuple[list[tuple[float, float]], tuple[float, float] | None, float | None]:
    circle = circle_from_3_points(start, mid, end)
    if circle is None:
        return [start, mid, end], None, None

    center, radius = circle
    angles = {
        "start": math.atan2(start[1] - center[1], start[0] - center[0]),
        "mid": math.atan2(mid[1] - center[1], mid[0] - center[0]),
        "end": math.atan2(end[1] - center[1], end[0] - center[0]),
    }
    use_ccw = angle_on_ccw_arc(angles["start"], angles["end"], angles["mid"])

    points = [start, mid, end]
    for candidate in (0.0, math.pi / 2.0, math.pi, math.pi * 3.0 / 2.0):
        if use_ccw:
            on_arc = angle_on_ccw_arc(angles["start"], angles["end"], candidate)
        else:
            on_arc = angle_on_ccw_arc(angles["end"], angles["start"], candidate)

        if on_arc:
            points.append(
                (
                    center[0] + radius * math.cos(candidate),
                    center[1] + radius * math.sin(candidate),
                )
            )

    return points, center, radius


def bbox_from_points(points: Iterable[tuple[float, float]]) -> dict[str, float]:
    point_list = list(points)
    if not point_list:
        raise ValueError("Cannot calculate a bounding box without points")

    xs = [point[0] for point in point_list]
    ys = [point[1] for point in point_list]
    return {
        "min_x": min(xs),
        "min_y": min(ys),
        "max_x": max(xs),
        "max_y": max(ys),
    }


def transform_point(
    x: float, y: float, native_outline_bbox: dict[str, float]
) -> tuple[float, float]:
    return (
        round_mm(x - native_outline_bbox["min_x"]),
        round_mm(native_outline_bbox["max_y"] - y),
    )


def corner_name(
    point: tuple[float, float] | None,
    native_outline_bbox: dict[str, float],
) -> str | None:
    if point is None:
        return None

    x, y = transform_point(point[0], point[1], native_outline_bbox)
    width = native_outline_bbox["max_x"] - native_outline_bbox["min_x"]
    height = native_outline_bbox["max_y"] - native_outline_bbox["min_y"]
    horizontal = "left" if x < width / 2.0 else "right"
    vertical = "bottom" if y < height / 2.0 else "top"
    return f"{vertical}_{horizontal}"


def nearest_edge(
    x: float,
    y: float,
    width: float,
    height: float,
) -> str:
    distances = {
        "front": y,
        "back": height - y,
        "left": x,
        "right": width - x,
    }
    return min(distances, key=distances.get)


def ref_sort_key(item: dict[str, Any]) -> tuple[str, int, str]:
    ref = item.get("ref", "")
    prefix = "".join(char for char in ref if not char.isdigit())
    digits = "".join(char for char in ref if char.isdigit())
    return prefix, int(digits or 0), ref


def maybe_call(value: Any) -> Any:
    return value() if callable(value) else value


def object_attr(obj: Any, *names: str) -> Any:
    for name in names:
        if hasattr(obj, name):
            return maybe_call(getattr(obj, name))
    raise AttributeError(f"{obj!r} has none of {names!r}")


def import_pcbnew() -> tuple[Any | None, str | None]:
    try:
        import pcbnew  # type: ignore[import-not-found]

        return pcbnew, None
    except Exception as first_error:
        sys.modules.pop("pcbnew", None)
        first_error_message = str(first_error)

    if KICAD_APP_SITE_PACKAGES.exists():
        sys.path.insert(0, str(KICAD_APP_SITE_PACKAGES))
        try:
            import pcbnew  # type: ignore[import-not-found]

            return pcbnew, None
        except Exception as second_error:
            sys.modules.pop("pcbnew", None)
            return None, str(second_error)

    return None, first_error_message


def pcbnew_to_mm(pcbnew: Any, value: Any) -> float:
    return float(pcbnew.ToMM(value))


def pcbnew_point_to_mm(pcbnew: Any, point: Any) -> tuple[float, float]:
    x = object_attr(point, "x", "GetX")
    y = object_attr(point, "y", "GetY")
    return pcbnew_to_mm(pcbnew, x), pcbnew_to_mm(pcbnew, y)


def pcbnew_angle_deg(footprint: Any) -> float:
    if hasattr(footprint, "GetOrientationDegrees"):
        return float(footprint.GetOrientationDegrees())

    orientation = footprint.GetOrientation()
    if hasattr(orientation, "AsDegrees"):
        return float(orientation.AsDegrees())

    return float(orientation) / 10.0


def pcbnew_footprint_name(footprint: Any) -> str:
    fpid = footprint.GetFPID()

    for method_name in ("GetFootprintName", "GetLibItemName", "Format"):
        if hasattr(fpid, method_name):
            try:
                value = getattr(fpid, method_name)()
            except TypeError:
                continue
            if value:
                return str(value)

    return str(fpid)


def pcbnew_pads(footprint: Any) -> Iterable[Any]:
    if hasattr(footprint, "Pads"):
        return footprint.Pads()

    return footprint.GetPads()


def pcbnew_drill_diameter_mm(pcbnew: Any, footprint: Any) -> float | None:
    drill_diameters: list[float] = []
    for pad in pcbnew_pads(footprint):
        if hasattr(pad, "GetDrillSize"):
            drill = pad.GetDrillSize()
            drill_x = pcbnew_to_mm(pcbnew, object_attr(drill, "x", "GetX"))
            drill_y = pcbnew_to_mm(pcbnew, object_attr(drill, "y", "GetY"))
            drill_diameters.append(max(drill_x, drill_y))
        elif hasattr(pad, "GetDrillSizeX"):
            drill_diameters.append(float(pcbnew.ToMM(pad.GetDrillSizeX())))

    return max(drill_diameters) if drill_diameters else None


def pcbnew_shape_kind(pcbnew: Any, drawing: Any) -> str:
    shape = drawing.GetShape() if hasattr(drawing, "GetShape") else None

    if hasattr(pcbnew, "SHAPE_T_ARC") and shape == pcbnew.SHAPE_T_ARC:
        return "arc"
    if hasattr(pcbnew, "SHAPE_T_SEGMENT") and shape == pcbnew.SHAPE_T_SEGMENT:
        return "line"

    shape_text = str(shape).upper()
    if "ARC" in shape_text:
        return "arc"
    if "SEGMENT" in shape_text or "LINE" in shape_text:
        return "line"

    return shape_text.lower()


def pcbnew_extract_edges(
    pcbnew: Any, board: Any
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    edge_layer = (
        pcbnew.Edge_Cuts if hasattr(pcbnew, "Edge_Cuts") else board.GetLayerID("Edge.Cuts")
    )
    points: list[tuple[float, float]] = []
    arcs: list[dict[str, Any]] = []

    for drawing in board.GetDrawings():
        if drawing.GetLayer() != edge_layer:
            continue

        kind = pcbnew_shape_kind(pcbnew, drawing)
        if kind == "line":
            points.extend(
                (
                    pcbnew_point_to_mm(pcbnew, drawing.GetStart()),
                    pcbnew_point_to_mm(pcbnew, drawing.GetEnd()),
                )
            )
        elif kind == "arc":
            start = pcbnew_point_to_mm(pcbnew, drawing.GetStart())
            end = pcbnew_point_to_mm(pcbnew, drawing.GetEnd())
            if hasattr(drawing, "GetArcMid"):
                mid = pcbnew_point_to_mm(pcbnew, drawing.GetArcMid())
            else:
                mid = pcbnew_point_to_mm(pcbnew, drawing.GetCenter())

            arc_bbox_points, center, radius = arc_points_for_bbox(start, mid, end)
            points.extend(arc_bbox_points)
            arcs.append({"center": center, "radius": radius})

    native_bbox = bbox_from_points(points)
    rounded_corner_arcs = [
        {
            "corner": corner_name(arc["center"], native_bbox),
            "radius": round_mm(arc["radius"]),
            "center_x": transform_point(arc["center"][0], arc["center"][1], native_bbox)[0],
            "center_y": transform_point(arc["center"][0], arc["center"][1], native_bbox)[1],
        }
        for arc in arcs
        if arc["center"] is not None and arc["radius"] is not None
    ]
    rounded_corner_arcs.sort(key=lambda arc: arc["corner"] or "")

    return native_bbox, rounded_corner_arcs


def extract_with_pcbnew(board_path: Path) -> dict[str, Any]:
    pcbnew, import_error = import_pcbnew()
    if pcbnew is None:
        raise RuntimeError(f"pcbnew unavailable: {import_error}")

    board = pcbnew.LoadBoard(str(board_path))
    native_bbox, rounded_corner_arcs = pcbnew_extract_edges(pcbnew, board)
    width = round_mm(native_bbox["max_x"] - native_bbox["min_x"])
    height = round_mm(native_bbox["max_y"] - native_bbox["min_y"])

    mounting_holes: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []

    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        value = footprint.GetValue()
        footprint_name = pcbnew_footprint_name(footprint)
        native_x, native_y = pcbnew_point_to_mm(pcbnew, footprint.GetPosition())
        x, y = transform_point(native_x, native_y, native_bbox)
        rotation_deg = round_mm(pcbnew_angle_deg(footprint))
        layer_name = board.GetLayerName(footprint.GetLayer())
        layer = "B" if layer_name.startswith("B.") else "F"
        bbox = footprint.GetBoundingBox()
        bbox_width = round_mm(pcbnew_to_mm(pcbnew, bbox.GetWidth()))
        bbox_height = round_mm(pcbnew_to_mm(pcbnew, bbox.GetHeight()))

        component = {
            "ref": ref,
            "value": value,
            "footprint_name": footprint_name,
            "x": x,
            "y": y,
            "rotation_deg": rotation_deg,
            "layer": layer,
            "bbox_width": bbox_width,
            "bbox_height": bbox_height,
            "nearest_edge": nearest_edge(x, y, width, height),
        }
        components.append(component)

        if ref.startswith("MH") or "MountingHole" in footprint_name:
            mounting_holes.append(
                {
                    "ref": ref,
                    "x": x,
                    "y": y,
                    "drill_diameter": round_mm(
                        pcbnew_drill_diameter_mm(pcbnew, footprint) or 0.0
                    ),
                }
            )

    components.sort(key=ref_sort_key)
    mounting_holes.sort(key=ref_sort_key)

    return build_output(
        source_board=board_path,
        board_outline=board_outline(width, height, rounded_corner_arcs),
        mounting_holes=mounting_holes,
        components=components,
        extraction_backend="pcbnew",
    )


def tokenize_sexpr(text: str) -> list[Any]:
    tokens: list[Any] = []
    index = 0

    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
        elif char in "()":
            tokens.append(char)
            index += 1
        elif char == '"':
            index += 1
            value_chars: list[str] = []
            while index < len(text):
                char = text[index]
                if char == "\\" and index + 1 < len(text):
                    value_chars.append(text[index + 1])
                    index += 2
                elif char == '"':
                    index += 1
                    break
                else:
                    value_chars.append(char)
                    index += 1
            tokens.append("".join(value_chars))
        else:
            start = index
            while index < len(text) and not text[index].isspace() and text[index] not in "()":
                index += 1
            atom = text[start:index]
            try:
                tokens.append(float(atom) if "." in atom else int(atom))
            except ValueError:
                tokens.append(atom)

    return tokens


def parse_sexpr_tokens(tokens: list[Any]) -> Any:
    def parse_at(index: int) -> tuple[Any, int]:
        if tokens[index] != "(":
            return tokens[index], index + 1

        values: list[Any] = []
        index += 1
        while index < len(tokens) and tokens[index] != ")":
            value, index = parse_at(index)
            values.append(value)

        if index >= len(tokens):
            raise ValueError("Unclosed S-expression")

        return values, index + 1

    parsed, end_index = parse_at(0)
    if end_index != len(tokens):
        raise ValueError("Unexpected trailing S-expression data")
    return parsed


def is_node(value: Any, name: str | None = None) -> bool:
    if not isinstance(value, list) or not value:
        return False
    return name is None or value[0] == name


def child(node: list[Any], name: str) -> list[Any] | None:
    for value in node:
        if is_node(value, name):
            return value
    return None


def children(node: list[Any], name: str) -> list[list[Any]]:
    return [value for value in node if is_node(value, name)]


def number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def at_xy_rotation(node: list[Any]) -> tuple[float, float, float]:
    at = child(node, "at")
    if at is None or len(at) < 3:
        return 0.0, 0.0, 0.0
    rotation = number(at[3]) if len(at) > 3 else 0.0
    return number(at[1]), number(at[2]), rotation


def property_value(node: list[Any], name: str) -> str:
    for property_node in children(node, "property"):
        if len(property_node) >= 3 and property_node[1] == name:
            return str(property_node[2])
    return ""


def point_node(node: list[Any], name: str) -> tuple[float, float] | None:
    item = child(node, name)
    if item is None or len(item) < 3:
        return None
    return number(item[1]), number(item[2])


def add_rect_points(
    points: list[tuple[float, float]],
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    rotation_deg: float = 0.0,
) -> None:
    radians = math.radians(rotation_deg)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    for dx in (-width / 2.0, width / 2.0):
        for dy in (-height / 2.0, height / 2.0):
            points.append(
                (
                    center_x + dx * cos_a - dy * sin_a,
                    center_y + dx * sin_a + dy * cos_a,
                )
            )


def local_shape_points(shape: list[Any]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    kind = str(shape[0])

    if kind in {"fp_line", "gr_line"}:
        for name in ("start", "end"):
            point = point_node(shape, name)
            if point is not None:
                points.append(point)
    elif kind == "fp_rect":
        start = point_node(shape, "start")
        end = point_node(shape, "end")
        if start is not None and end is not None:
            points.extend(
                [
                    start,
                    (start[0], end[1]),
                    end,
                    (end[0], start[1]),
                ]
            )
    elif kind in {"fp_circle", "gr_circle"}:
        center = point_node(shape, "center")
        end = point_node(shape, "end")
        if center is not None and end is not None:
            radius = distance(center, end)
            points.extend(
                [
                    (center[0] - radius, center[1]),
                    (center[0] + radius, center[1]),
                    (center[0], center[1] - radius),
                    (center[0], center[1] + radius),
                ]
            )
    elif kind in {"fp_arc", "gr_arc"}:
        start = point_node(shape, "start")
        mid = point_node(shape, "mid")
        end = point_node(shape, "end")
        if start is not None and mid is not None and end is not None:
            arc_points, _, _ = arc_points_for_bbox(start, mid, end)
            points.extend(arc_points)
    elif kind in {"fp_poly", "gr_poly"}:
        pts = child(shape, "pts")
        if pts is not None:
            for xy in children(pts, "xy"):
                if len(xy) >= 3:
                    points.append((number(xy[1]), number(xy[2])))

    return points


def pad_points(pad: list[Any]) -> list[tuple[float, float]]:
    at = child(pad, "at")
    size = child(pad, "size")
    if at is None or size is None or len(size) < 3:
        return []

    x = number(at[1]) if len(at) > 1 else 0.0
    y = number(at[2]) if len(at) > 2 else 0.0
    rotation = number(at[3]) if len(at) > 3 else 0.0
    width = number(size[1])
    height = number(size[2])
    points: list[tuple[float, float]] = []
    add_rect_points(points, x, y, width, height, rotation)
    return points


def pad_drill_diameter(pad: list[Any]) -> float | None:
    drill = child(pad, "drill")
    if drill is None or len(drill) < 2:
        return None

    drill_values = [number(value) for value in drill[1:] if isinstance(value, (int, float))]
    return max(drill_values) if drill_values else None


def rotate_point(x: float, y: float, rotation_deg: float) -> tuple[float, float]:
    radians = math.radians(rotation_deg)
    return (
        x * math.cos(radians) - y * math.sin(radians),
        x * math.sin(radians) + y * math.cos(radians),
    )


def fallback_footprint_bbox(footprint: list[Any], x: float, y: float, rotation: float) -> tuple[float, float]:
    local_points: list[tuple[float, float]] = []
    for item in footprint:
        if not is_node(item):
            continue
        if str(item[0]).startswith("fp_") and item[0] != "fp_text":
            local_points.extend(local_shape_points(item))
        elif item[0] == "pad":
            local_points.extend(pad_points(item))

    if not local_points:
        return 0.0, 0.0

    global_points: list[tuple[float, float]] = []
    for local_x, local_y in local_points:
        rotated_x, rotated_y = rotate_point(local_x, local_y, rotation)
        global_points.append((x + rotated_x, y + rotated_y))

    bbox = bbox_from_points(global_points)
    return (
        round_mm(bbox["max_x"] - bbox["min_x"]),
        round_mm(bbox["max_y"] - bbox["min_y"]),
    )


def extract_edge_data_from_sexpr(board: list[Any]) -> tuple[dict[str, float], list[dict[str, Any]]]:
    points: list[tuple[float, float]] = []
    arcs: list[dict[str, Any]] = []

    for item in board:
        if not is_node(item) or item[0] not in {"gr_line", "gr_arc"}:
            continue

        layer = child(item, "layer")
        if layer is None or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue

        if item[0] == "gr_line":
            start = point_node(item, "start")
            end = point_node(item, "end")
            if start is not None and end is not None:
                points.extend([start, end])
        elif item[0] == "gr_arc":
            start = point_node(item, "start")
            mid = point_node(item, "mid")
            end = point_node(item, "end")
            if start is not None and mid is not None and end is not None:
                arc_bbox_points, center, radius = arc_points_for_bbox(start, mid, end)
                points.extend(arc_bbox_points)
                arcs.append({"center": center, "radius": radius})

    native_bbox = bbox_from_points(points)
    rounded_corner_arcs = [
        {
            "corner": corner_name(arc["center"], native_bbox),
            "radius": round_mm(arc["radius"]),
            "center_x": transform_point(arc["center"][0], arc["center"][1], native_bbox)[0],
            "center_y": transform_point(arc["center"][0], arc["center"][1], native_bbox)[1],
        }
        for arc in arcs
        if arc["center"] is not None and arc["radius"] is not None
    ]
    rounded_corner_arcs.sort(key=lambda arc: arc["corner"] or "")

    return native_bbox, rounded_corner_arcs


def extract_with_sexpr(board_path: Path, backend_note: str) -> dict[str, Any]:
    parsed = parse_sexpr_tokens(tokenize_sexpr(board_path.read_text(encoding="utf-8")))
    if not is_node(parsed, "kicad_pcb"):
        raise ValueError(f"{board_path} is not a KiCad PCB file")

    native_bbox, rounded_corner_arcs = extract_edge_data_from_sexpr(parsed)
    width = round_mm(native_bbox["max_x"] - native_bbox["min_x"])
    height = round_mm(native_bbox["max_y"] - native_bbox["min_y"])
    components: list[dict[str, Any]] = []
    mounting_holes: list[dict[str, Any]] = []

    for footprint in children(parsed, "footprint"):
        footprint_name = str(footprint[1]) if len(footprint) > 1 else ""
        native_x, native_y, rotation = at_xy_rotation(footprint)
        x, y = transform_point(native_x, native_y, native_bbox)
        ref = property_value(footprint, "Reference")
        value = property_value(footprint, "Value")
        layer_node = child(footprint, "layer")
        layer_name = str(layer_node[1]) if layer_node is not None and len(layer_node) > 1 else "F.Cu"
        layer = "B" if layer_name.startswith("B.") else "F"
        bbox_width, bbox_height = fallback_footprint_bbox(
            footprint, native_x, native_y, rotation
        )

        component = {
            "ref": ref,
            "value": value,
            "footprint_name": footprint_name,
            "x": x,
            "y": y,
            "rotation_deg": round_mm(rotation),
            "layer": layer,
            "bbox_width": bbox_width,
            "bbox_height": bbox_height,
            "nearest_edge": nearest_edge(x, y, width, height),
        }
        components.append(component)

        if ref.startswith("MH") or "MountingHole" in footprint_name:
            drill_diameters = [
                diameter
                for diameter in (pad_drill_diameter(pad) for pad in children(footprint, "pad"))
                if diameter is not None
            ]
            mounting_holes.append(
                {
                    "ref": ref,
                    "x": x,
                    "y": y,
                    "drill_diameter": round_mm(max(drill_diameters) if drill_diameters else 0.0),
                }
            )

    components.sort(key=ref_sort_key)
    mounting_holes.sort(key=ref_sort_key)

    return build_output(
        source_board=board_path,
        board_outline=board_outline(width, height, rounded_corner_arcs),
        mounting_holes=mounting_holes,
        components=components,
        extraction_backend=backend_note,
    )


def board_outline(
    width: float,
    height: float,
    rounded_corner_arcs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "min_x": 0.0,
        "min_y": 0.0,
        "max_x": width,
        "max_y": height,
        "width": width,
        "height": height,
        "rounded_corner_arcs": rounded_corner_arcs,
    }


def build_output(
    source_board: Path,
    board_outline: dict[str, Any],
    mounting_holes: list[dict[str, Any]],
    components: list[dict[str, Any]],
    extraction_backend: str,
) -> dict[str, Any]:
    return {
        "source_board": str(source_board),
        "units": "mm",
        "coordinate_origin": (
            "bottom-left of Edge.Cuts bounding box; KiCad native Y is top-down"
        ),
        "extraction_backend": extraction_backend,
        "board_outline": board_outline,
        "mounting_holes": mounting_holes,
        "components": components,
    }


def extract_geometry(board_path: Path) -> dict[str, Any]:
    try:
        return extract_with_pcbnew(board_path)
    except Exception as error:
        print(
            f"Warning: pcbnew extraction failed ({error}); using KiCad S-expression fallback.",
            file=sys.stderr,
        )
        return extract_with_sexpr(board_path, "sexpr_fallback")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract normalized board geometry from a KiCad PCB file."
    )
    parser.add_argument(
        "board",
        nargs="?",
        default=DEFAULT_BOARD,
        type=Path,
        help=f"KiCad PCB file to read (default: {DEFAULT_BOARD})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        type=Path,
        help=f"JSON file to write (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    data = extract_geometry(args.board)
    text = json.dumps(data, indent=2)
    args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
