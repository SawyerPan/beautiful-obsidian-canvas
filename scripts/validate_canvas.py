#!/usr/bin/env python3
"""Validate JSON Canvas structure and conservative visual-quality heuristics."""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
SIDES = {"top", "right", "bottom", "left"}
ENDS = {"none", "arrow"}
NODE_TYPES = {"text", "file", "link", "group"}
BACKGROUND_STYLES = {"cover", "ratio", "repeat"}

Issue = Dict[str, Any]
Point = Tuple[float, float]


def issue(code: str, message: str, ids: Optional[Sequence[str]] = None) -> Issue:
    result: Issue = {"code": code, "message": message}
    if ids:
        result["ids"] = list(ids)
    return result


def valid_color(value: Any) -> bool:
    return isinstance(value, str) and (bool(HEX_COLOR.fullmatch(value)) or value in set("123456"))


def is_int(value: Any) -> bool:
    return type(value) is int


def rect(node: Dict[str, Any]) -> Tuple[float, float, float, float]:
    return (
        float(node["x"]),
        float(node["y"]),
        float(node["x"] + node["width"]),
        float(node["y"] + node["height"]),
    )


def rectangles_overlap(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    ax1, ay1, ax2, ay2 = rect(a)
    bx1, by1, bx2, by2 = rect(b)
    return min(ax2, bx2) > max(ax1, bx1) and min(ay2, by2) > max(ay1, by1)


def contains_node(group: Dict[str, Any], node: Dict[str, Any]) -> bool:
    gx1, gy1, gx2, gy2 = rect(group)
    nx1, ny1, nx2, ny2 = rect(node)
    return gx1 <= nx1 and gy1 <= ny1 and nx2 <= gx2 and ny2 <= gy2


def is_semantic_hub(node: Dict[str, Any]) -> bool:
    return (
        node.get("type") == "text"
        and "color" in node
        and 200 <= node.get("width", 0) <= 240
        and 90 <= node.get("height", 0) <= 120
        and isinstance(node.get("text"), str)
        and len(node["text"].splitlines()) <= 2
    )


def anchor(node: Dict[str, Any], side: Optional[str]) -> Point:
    x = float(node["x"])
    y = float(node["y"])
    width = float(node["width"])
    height = float(node["height"])
    if side == "top":
        return (x + width / 2, y)
    if side == "right":
        return (x + width, y + height / 2)
    if side == "bottom":
        return (x + width / 2, y + height)
    if side == "left":
        return (x, y + height / 2)
    return (x + width / 2, y + height / 2)


def point_in_rect(point: Point, bounds: Tuple[float, float, float, float]) -> bool:
    x, y = point
    x1, y1, x2, y2 = bounds
    return x1 <= x <= x2 and y1 <= y <= y2


def orientation(a: Point, b: Point, c: Point) -> int:
    value = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if abs(value) < 1e-9:
        return 0
    return 1 if value > 0 else -1


def on_segment(a: Point, b: Point, p: Point) -> bool:
    return (
        min(a[0], b[0]) - 1e-9 <= p[0] <= max(a[0], b[0]) + 1e-9
        and min(a[1], b[1]) - 1e-9 <= p[1] <= max(a[1], b[1]) + 1e-9
    )


def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    if o1 != o2 and o3 != o4:
        return True
    return any(
        (
            o1 == 0 and on_segment(a, b, c),
            o2 == 0 and on_segment(a, b, d),
            o3 == 0 and on_segment(c, d, a),
            o4 == 0 and on_segment(c, d, b),
        )
    )


def segment_intersects_rect(a: Point, b: Point, bounds: Tuple[float, float, float, float]) -> bool:
    if point_in_rect(a, bounds) or point_in_rect(b, bounds):
        return True
    x1, y1, x2, y2 = bounds
    corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    sides = list(zip(corners, corners[1:] + corners[:1]))
    return any(segments_intersect(a, b, c, d) for c, d in sides)


def estimated_text_rows(text: str, width: int) -> float:
    usable_width = max(80, width - 36)
    total_rows = 0.0
    for raw_line in text.splitlines() or [""]:
        heading = raw_line.startswith("#")
        clean = re.sub(r"^[#>*+\-\s]+", "", raw_line)
        clean = re.sub(r"[`*_~]", "", clean)
        pixels = 0
        for char in clean:
            pixels += 16 if ord(char) > 255 else 8
        wrapped = max(1, math.ceil(pixels / usable_width))
        total_rows += wrapped * (1.35 if heading else 1.0)
    return total_rows


def validate(path: Path) -> Dict[str, Any]:
    errors: List[Issue] = []
    warnings: List[Issue] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        errors.append(issue("file-not-found", f"File does not exist: {path}"))
        return result(path, 0, 0, errors, warnings)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(issue("json-parse", f"Cannot parse JSON: {exc}"))
        return result(path, 0, 0, errors, warnings)

    if not isinstance(data, dict):
        errors.append(issue("top-level-type", "Top level must be a JSON object"))
        return result(path, 0, 0, errors, warnings)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list):
        errors.append(issue("nodes-type", "nodes must be an array"))
        nodes = []
    if not isinstance(edges, list):
        errors.append(issue("edges-type", "edges must be an array"))
        edges = []

    seen_ids: Dict[str, str] = {}
    valid_nodes: List[Dict[str, Any]] = []
    nodes_by_id: Dict[str, Dict[str, Any]] = {}

    for index, node in enumerate(nodes):
        prefix = f"node[{index}]"
        if not isinstance(node, dict):
            errors.append(issue("node-type", f"{prefix} must be an object"))
            continue
        node_id = node.get("id")
        node_type = node.get("type")
        if not isinstance(node_id, str) or not node_id:
            errors.append(issue("node-id", f"{prefix}.id must be a non-empty string"))
        elif node_id in seen_ids:
            errors.append(issue("duplicate-id", f"ID {node_id!r} is already used by {seen_ids[node_id]}", [node_id]))
        else:
            seen_ids[node_id] = prefix

        if node_type not in NODE_TYPES:
            errors.append(issue("node-kind", f"{prefix}.type must be one of {sorted(NODE_TYPES)}", [node_id] if isinstance(node_id, str) else None))

        geometry_ok = True
        for field in ("x", "y", "width", "height"):
            if not is_int(node.get(field)):
                errors.append(issue("node-geometry", f"{prefix}.{field} must be an integer", [node_id] if isinstance(node_id, str) else None))
                geometry_ok = False
        if geometry_ok and (node["width"] <= 0 or node["height"] <= 0):
            errors.append(issue("node-size", f"{prefix} width and height must be positive", [node_id]))
            geometry_ok = False

        if "color" in node and not valid_color(node["color"]):
            errors.append(issue("node-color", f"{prefix}.color must be #RRGGBB or preset 1-6", [node_id] if isinstance(node_id, str) else None))

        required_field = {"text": "text", "file": "file", "link": "url"}.get(node_type)
        if required_field and not isinstance(node.get(required_field), str):
            errors.append(issue("node-content", f"{prefix}.{required_field} must be a string", [node_id] if isinstance(node_id, str) else None))
        if "subpath" in node and (not isinstance(node["subpath"], str) or not node["subpath"].startswith("#")):
            errors.append(issue("file-subpath", f"{prefix}.subpath must be a string starting with #", [node_id] if isinstance(node_id, str) else None))
        if "label" in node and not isinstance(node["label"], str):
            errors.append(issue("group-label", f"{prefix}.label must be a string", [node_id] if isinstance(node_id, str) else None))
        if "background" in node and not isinstance(node["background"], str):
            errors.append(issue("group-background", f"{prefix}.background must be a string", [node_id] if isinstance(node_id, str) else None))
        if "backgroundStyle" in node and node["backgroundStyle"] not in BACKGROUND_STYLES:
            errors.append(issue("group-background-style", f"{prefix}.backgroundStyle must be cover, ratio, or repeat", [node_id] if isinstance(node_id, str) else None))

        if isinstance(node_id, str) and node_id and geometry_ok:
            valid_nodes.append(node)
            nodes_by_id[node_id] = node

    valid_edges: List[Dict[str, Any]] = []
    for index, edge in enumerate(edges):
        prefix = f"edge[{index}]"
        if not isinstance(edge, dict):
            errors.append(issue("edge-type", f"{prefix} must be an object"))
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append(issue("edge-id", f"{prefix}.id must be a non-empty string"))
        elif edge_id in seen_ids:
            errors.append(issue("duplicate-id", f"ID {edge_id!r} is already used by {seen_ids[edge_id]}", [edge_id]))
        else:
            seen_ids[edge_id] = prefix

        edge_ok = True
        for field in ("fromNode", "toNode"):
            value = edge.get(field)
            if not isinstance(value, str) or not value:
                errors.append(issue("edge-reference", f"{prefix}.{field} must be a non-empty string", [edge_id] if isinstance(edge_id, str) else None))
                edge_ok = False
            elif value not in nodes_by_id:
                errors.append(issue("dangling-edge", f"{prefix}.{field} references missing node {value!r}", [edge_id, value] if isinstance(edge_id, str) else [value]))
                edge_ok = False
        for field in ("fromSide", "toSide"):
            if field in edge and edge[field] not in SIDES:
                errors.append(issue("edge-side", f"{prefix}.{field} must be one of {sorted(SIDES)}", [edge_id] if isinstance(edge_id, str) else None))
                edge_ok = False
        for field in ("fromEnd", "toEnd"):
            if field in edge and edge[field] not in ENDS:
                errors.append(issue("edge-end", f"{prefix}.{field} must be one of {sorted(ENDS)}", [edge_id] if isinstance(edge_id, str) else None))
                edge_ok = False
        if "color" in edge and not valid_color(edge["color"]):
            errors.append(issue("edge-color", f"{prefix}.color must be #RRGGBB or preset 1-6", [edge_id] if isinstance(edge_id, str) else None))
            edge_ok = False
        if "label" in edge and not isinstance(edge["label"], str):
            errors.append(issue("edge-label", f"{prefix}.label must be a string", [edge_id] if isinstance(edge_id, str) else None))
            edge_ok = False
        if edge_ok and isinstance(edge_id, str) and edge_id:
            valid_edges.append(edge)

    ordinary = [node for node in valid_nodes if node.get("type") != "group"]
    groups = [node for node in valid_nodes if node.get("type") == "group"]
    for index, left in enumerate(ordinary):
        for right in ordinary[index + 1 :]:
            if rectangles_overlap(left, right):
                warnings.append(issue("node-overlap", "Ordinary nodes overlap", [left["id"], right["id"]]))

    for node in ordinary:
        if node.get("type") == "text" and isinstance(node.get("text"), str):
            required = estimated_text_rows(node["text"], node["width"])
            available = max(1.0, (node["height"] - 28) / 22.0)
            if required > available:
                warnings.append(issue("text-capacity", f"Text may need {required:.1f} rows but node has room for about {available:.1f}", [node["id"]]))

    for group in groups:
        members = [node for node in ordinary if contains_node(group, node)]
        top_minimum = 70 if group.get("label") else 50
        for node in members:
            left_gap = node["x"] - group["x"]
            top_gap = node["y"] - group["y"]
            right_gap = group["x"] + group["width"] - node["x"] - node["width"]
            bottom_gap = group["y"] + group["height"] - node["y"] - node["height"]
            if left_gap < 50 or right_gap < 50 or bottom_gap < 50 or top_gap < top_minimum:
                warnings.append(
                    issue(
                        "group-padding",
                        f"Node padding inside group is L{left_gap}/T{top_gap}/R{right_gap}/B{bottom_gap}; expected at least 50 px and 70 px at a labeled top",
                        [group["id"], node["id"]],
                    )
                )

        peers: Dict[Tuple[str, Optional[str]], List[Dict[str, Any]]] = {}
        for node in members:
            peers.setdefault((node.get("type", ""), node.get("color")), []).append(node)
        for role_nodes in peers.values():
            if len(role_nodes) < 3:
                continue
            row_tolerance = max(24, int(sorted(node["height"] for node in role_nodes)[len(role_nodes) // 2] * 0.25))
            rows: List[List[Dict[str, Any]]] = []
            for node in sorted(role_nodes, key=lambda item: (item["y"], item["x"])):
                for row in rows:
                    baseline = sum(item["y"] for item in row) / len(row)
                    if abs(node["y"] - baseline) <= row_tolerance:
                        row.append(node)
                        break
                else:
                    rows.append([node])
            for row in rows:
                if len(row) < 3:
                    continue
                ids = [node["id"] for node in row]
                if max(node["y"] for node in row) - min(node["y"] for node in row) > 8:
                    warnings.append(issue("row-misalignment", "Peer nodes in one row do not share the same y coordinate", ids))
                if (
                    max(node["width"] for node in row) - min(node["width"] for node in row) > 8
                    or max(node["height"] for node in row) - min(node["height"] for node in row) > 8
                ):
                    warnings.append(issue("peer-size-mismatch", "Peer nodes in one row do not share the same dimensions", ids))
                ordered = sorted(row, key=lambda item: item["x"])
                gaps = [
                    right["x"] - left["x"] - left["width"]
                    for left, right in zip(ordered, ordered[1:])
                ]
                if len(gaps) >= 2 and max(gaps) - min(gaps) > 16:
                    warnings.append(issue("uneven-spacing", f"Peer gaps vary from {min(gaps)} to {max(gaps)} px", ids))

    degree: Dict[str, int] = {node_id: 0 for node_id in nodes_by_id}
    edge_segments: List[Tuple[Dict[str, Any], Point, Point]] = []
    horizontal = 0
    vertical = 0
    for edge in valid_edges:
        from_id = edge["fromNode"]
        to_id = edge["toNode"]
        degree[from_id] += 1
        degree[to_id] += 1
        start = anchor(nodes_by_id[from_id], edge.get("fromSide"))
        end = anchor(nodes_by_id[to_id], edge.get("toSide"))
        edge_segments.append((edge, start, end))
        from_side = edge.get("fromSide")
        to_side = edge.get("toSide")
        if from_side in {"top", "bottom"} and to_side in {"top", "bottom"}:
            vertical += 1
        elif from_side in {"left", "right"} and to_side in {"left", "right"}:
            horizontal += 1
        elif abs(end[0] - start[0]) >= abs(end[1] - start[1]):
            horizontal += 1
        else:
            vertical += 1

        for node in ordinary:
            if node["id"] in (from_id, to_id):
                continue
            if segment_intersects_rect(start, end, rect(node)):
                warnings.append(issue("edge-through-node", "Connector intersects an unrelated node", [edge["id"], node["id"]]))

    for node_id, count in degree.items():
        limit = 6 if is_semantic_hub(nodes_by_id[node_id]) else 4
        if count > limit:
            warnings.append(issue("high-degree", f"Node has degree {count}; limit is {limit} for this node role", [node_id]))

    for index, (left_edge, a, b) in enumerate(edge_segments):
        for right_edge, c, d in edge_segments[index + 1 :]:
            shared = {left_edge["fromNode"], left_edge["toNode"]} & {right_edge["fromNode"], right_edge["toNode"]}
            if not shared and segments_intersect(a, b, c, d):
                warnings.append(issue("edge-crossing", "Connectors cross", [left_edge["id"], right_edge["id"]]))

    total_oriented = horizontal + vertical
    if total_oriented >= 4 and max(horizontal, vertical) / total_oriented < 0.70:
        warnings.append(issue("mixed-direction", f"No dominant edge direction: {horizontal} horizontal, {vertical} vertical"))

    return result(path, len(nodes), len(edges), errors, warnings)


def result(path: Path, nodes: int, edges: int, errors: List[Issue], warnings: List[Issue]) -> Dict[str, Any]:
    return {
        "path": str(path),
        "valid": not errors,
        "strict_valid": not errors and not warnings,
        "counts": {"nodes": nodes, "edges": edges, "errors": len(errors), "warnings": len(warnings)},
        "errors": errors,
        "warnings": warnings,
    }


def print_human(report: Dict[str, Any]) -> None:
    counts = report["counts"]
    print(f"Canvas: {report['path']}")
    print(f"Nodes: {counts['nodes']}  Edges: {counts['edges']}  Errors: {counts['errors']}  Warnings: {counts['warnings']}")
    for label in ("errors", "warnings"):
        for item in report[label]:
            suffix = f" [{', '.join(item.get('ids', []))}]" if item.get("ids") else ""
            print(f"{label[:-1].upper()} {item['code']}: {item['message']}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canvas", type=Path)
    parser.add_argument("--strict", action="store_true", help="Return exit code 2 when warnings exist")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print a machine-readable report")
    args = parser.parse_args()

    report = validate(args.canvas.expanduser().resolve())
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    if report["errors"]:
        return 1
    if args.strict and report["warnings"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
