#!/usr/bin/env python3
"""
Validator for email spec JSON.

Usage:
    python3 validate.py path/to/spec.json

Exit code 0 = valid. Non-zero = invalid; prints all issues found.

The validator runs at the end of figma-to-json, before output. If issues exist,
the skill iterates back to Figma to fill gaps before finalizing.

Validation has three tiers:
1. Required fields    — schema violations (missing src, alt, color, etc.)
2. Value constraints  — hex format, empty alt without decorative,
                        scaffolding colors (per spec.annotations.stripColors),
                        empty text runs (text is never placeholder)
3. Coherence          — multi-column overflow, gap references,
                        alias uniqueness
"""
import json
import re
import sys
from typing import Any, List


SUPPORTED_MAJOR_VERSION = 2


def is_hex_color(value: Any) -> bool:
    return isinstance(value, str) and bool(re.match(r"^#[0-9A-Fa-f]{6}$", value))


def has_all_padding_sides(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and all(k in value for k in ("top", "right", "bottom", "left"))
        and all(
            isinstance(value[k], int) and value[k] >= 0
            for k in ("top", "right", "bottom", "left")
        )
    )


def walk_text_runs(node: Any):
    """Recursively yield every text run in a node tree.

    A text run is a dict that has a `text` field (string) and is part of a
    `content` array somewhere in the tree.
    """
    if isinstance(node, dict):
        if "text" in node and isinstance(node["text"], str):
            yield node
        for v in node.values():
            yield from walk_text_runs(v)
    elif isinstance(node, list):
        for item in node:
            yield from walk_text_runs(item)


def walk_primitives_of_type(node: Any, type_name: str):
    """Recursively yield every primitive matching the given type."""
    if isinstance(node, dict):
        if node.get("type") == type_name:
            yield node
        for v in node.values():
            yield from walk_primitives_of_type(v, type_name)
    elif isinstance(node, list):
        for item in node:
            yield from walk_primitives_of_type(item, type_name)


def walk_links(node: Any):
    """Yield every link object — dicts with `href` and `alias` keys."""
    if isinstance(node, dict):
        if "href" in node and "alias" in node and isinstance(node.get("alias"), str):
            yield node
        for v in node.values():
            yield from walk_links(v)
    elif isinstance(node, list):
        for item in node:
            yield from walk_links(item)


def validate(spec: dict) -> List[dict]:
    """Return a list of issue dicts: {severity, path, message}."""
    issues = []

    def err(path: str, msg: str):
        issues.append({"severity": "ERROR", "path": path, "message": msg})

    def warn(path: str, msg: str):
        issues.append({"severity": "WARN", "path": path, "message": msg})

    # ----- Top-level required fields -----
    for field in ("specVersion", "meta", "annotations", "sections"):
        if field not in spec:
            err(f"$.{field}", f"required top-level field is missing")
            return issues  # Can't continue without these

    if not re.match(r"^\d+\.\d+\.\d+$", spec.get("specVersion", "")):
        err("$.specVersion", f"must be semver, got '{spec.get('specVersion')}'")
        return issues

    major = int(spec["specVersion"].split(".")[0])
    if major != SUPPORTED_MAJOR_VERSION:
        err(
            "$.specVersion",
            f"major version {major} not supported by this validator "
            f"(supports v{SUPPORTED_MAJOR_VERSION}.x.x)"
        )
        return issues

    # ----- meta -----
    meta = spec["meta"]
    if "emailName" not in meta:
        err("$.meta.emailName", "required")

    # ----- annotations -----
    annotations = spec["annotations"]
    # stripColors is per-email. Default to empty set if not provided.
    strip_colors = set(annotations.get("stripColors", []))
    # Also include lowercase variants for case-insensitive matching
    strip_colors_case_insensitive = {c.lower() for c in strip_colors}

    # ----- sections -----
    sections = spec["sections"]
    if not isinstance(sections, list) or not sections:
        err("$.sections", "must be a non-empty array")
        return issues

    seen_section_ids = set()
    seen_aliases = {}  # alias → first path where it was seen

    for i, section in enumerate(sections):
        spath = f"$.sections[{i}]"

        # Required section fields
        for field in ("id", "name", "nodes"):
            if field not in section:
                err(f"{spath}.{field}", "required")

        if "id" in section:
            if section["id"] in seen_section_ids:
                err(f"{spath}.id", f"duplicate section id '{section['id']}'")
            else:
                seen_section_ids.add(section["id"])

        if section.get("skipInProduction"):
            continue  # No further checks for editorial-only sections

        if "nodes" not in section or not isinstance(section["nodes"], list):
            continue

        # Walk every primitive in this section's nodes
        for j, node in enumerate(section["nodes"]):
            npath = f"{spath}.nodes[{j}]"
            validate_node(node, npath, err, warn)

        # Empty text run check: every text run in the spec must have non-empty
        # text content. Placeholder image URLs and "#" hrefs are allowed, but
        # text is never a placeholder — if a run has empty `text`, the skill
        # failed to transcribe something from Figma.
        for run in walk_text_runs(section["nodes"]):
            if not run.get("text"):
                err(
                    f"{spath}.nodes(textRun)",
                    f"section '{section.get('id', i)}' contains an empty text run"
                )

        # Collect all link aliases for uniqueness check
        for link in walk_links(section):
            alias = link.get("alias")
            if alias:
                if alias in seen_aliases:
                    err(
                        f"{spath}.nodes(link alias='{alias}')",
                        f"duplicate alias '{alias}' (first seen at {seen_aliases[alias]})"
                    )
                else:
                    seen_aliases[alias] = spath

        # Scaffolding color leakage check on every text run in this section
        for run in walk_text_runs(section["nodes"]):
            run_color = run.get("color")
            if run_color and run_color.lower() in strip_colors_case_insensitive:
                err(
                    f"{spath}.nodes(textRun text='{run['text'][:30]}...')",
                    f"scaffolding color {run_color} in rendered content. "
                    f"Should be stripped per annotations.stripColors, "
                    f"or recolored via annotations.recolorMap."
                )

        # Multi-column coherence checks
        desktop_width = meta.get("desktopWidth", 600)
        mobile_width = meta.get("mobileWidth", 360)
        for mc in walk_primitives_of_type(section["nodes"], "multiColumn"):
            validate_multicolumn(mc, npath, err, warn, desktop_width, mobile_width)

        # Hoist-shared-background check.
        # Two cases:
        #
        # Case A (hard): ALL immediate child nodes share the same `background`
        # but the section doesn't — hoist it to section level.
        #
        # Case B (soft): 2+ consecutive children share a background but other
        # children don't have one, and the section has no background. This
        # often means the extraction missed the background on some nodes.
        # Warn the operator to verify.
        nodes = section.get("nodes", [])
        if len(nodes) >= 2:
            section_bg = section.get("background")
            child_backgrounds = [
                n.get("background") for n in nodes if isinstance(n, dict)
            ]
            non_none = [bg for bg in child_backgrounds if bg is not None]

            if non_none:
                unique_colors = set(bg.lower() for bg in non_none)

                if (
                    len(non_none) == len(nodes)
                    and len(unique_colors) == 1
                    and (section_bg is None
                         or section_bg.lower() != non_none[0].lower())
                ):
                    # Case A: every child has the same bg, section doesn't
                    warn(
                        f"{spath}",
                        f"all {len(nodes)} child nodes share background "
                        f"'{non_none[0]}' but the section itself doesn't. "
                        f"Hoist the shared background to the section level "
                        f"per Phase 3c step 2."
                    )
                elif (
                    len(non_none) >= 2
                    and len(non_none) < len(nodes)
                    and len(unique_colors) == 1
                    and section_bg is None
                ):
                    # Case B: some children have the bg, some don't — the
                    # section-level background was likely missed during
                    # extraction. Phase 3c step 2 requires checking the
                    # section frame's fill before walking children.
                    err(
                        f"{spath}",
                        f"{len(non_none)} of {len(nodes)} child nodes have "
                        f"background '{non_none[0]}' but {len(nodes) - len(non_none)} "
                        f"don't, and the section has no background. The section "
                        f"frame likely has this background fill — re-check the "
                        f"section frame in Figma and set section.background per "
                        f"Phase 3c step 2."
                    )

    return issues


def validate_node(node: Any, path: str, err, warn) -> None:
    """Validate a single primitive node based on its type."""
    if not isinstance(node, dict):
        err(path, "node must be an object")
        return

    ntype = node.get("type")
    if not ntype:
        err(f"{path}.type", "required on every primitive node")
        return

    validators = {
        "image": validate_image,
        "textBlock": validate_text_block,
        "button": validate_button,
        "list": validate_list,
        "multiColumn": validate_multi_column_node,
        "spacer": validate_spacer,
    }

    handler = validators.get(ntype)
    if not handler:
        err(f"{path}.type", f"unknown primitive type '{ntype}'")
        return

    handler(node, path, err, warn)


def validate_image(node: dict, path: str, err, warn) -> None:
    for field in ("src", "alt", "width", "height"):
        if field not in node:
            err(f"{path}.{field}", "required on image")

    if "alt" in node and node["alt"] == "" and not node.get("decorative", False):
        err(
            f"{path}.alt",
            "empty alt requires decorative: true. Set decorative=true for purely "
            "visual elements; otherwise provide meaningful alt text."
        )

    for dim in ("width", "height"):
        if dim in node and (not isinstance(node[dim], int) or node[dim] < 1):
            err(f"{path}.{dim}", f"must be positive integer (got {node.get(dim)})")

    if "padding" in node and not has_all_padding_sides(node["padding"]):
        err(f"{path}.padding", "must be {top, right, bottom, left} with integer values >= 0")


def validate_text_block(node: dict, path: str, err, warn) -> None:
    if "content" not in node:
        err(f"{path}.content", "required on textBlock")
        return

    content = node["content"]
    if not isinstance(content, list) or not content:
        err(f"{path}.content", "must be a non-empty array of text runs")
        return

    for k, run in enumerate(content):
        if not isinstance(run, dict) or "text" not in run:
            err(f"{path}.content[{k}]", "text run must be {text: '...', ...}")
            continue
        if "color" in run and not is_hex_color(run["color"]):
            err(f"{path}.content[{k}].color", f"invalid hex: {run['color']}")
        if "link" in run:
            validate_link(run["link"], f"{path}.content[{k}].link", err)

    if "color" in node and not is_hex_color(node["color"]):
        err(f"{path}.color", f"invalid hex: {node['color']}")

    if "padding" in node and not has_all_padding_sides(node["padding"]):
        err(f"{path}.padding", "must be {top, right, bottom, left} with integer values >= 0")


def validate_button(node: dict, path: str, err, warn) -> None:
    for field in ("label", "link", "background", "width", "height"):
        if field not in node:
            err(f"{path}.{field}", "required on button")

    if "background" in node and not is_hex_color(node["background"]):
        err(f"{path}.background", f"invalid hex: {node['background']}")

    if "link" in node:
        validate_link(node["link"], f"{path}.link", err)


def validate_list(node: dict, path: str, err, warn) -> None:
    if node.get("style") not in ("bullet", "numbered"):
        err(f"{path}.style", "required, must be 'bullet' or 'numbered'")

    items = node.get("items")
    if not isinstance(items, list) or not items:
        err(f"{path}.items", "required, must be non-empty array")
        return

    for k, item in enumerate(items):
        if "content" not in item:
            err(f"{path}.items[{k}].content", "required")
            continue
        if not isinstance(item["content"], list):
            err(f"{path}.items[{k}].content", "must be array of text runs")


def validate_multi_column_node(node: dict, path: str, err, warn) -> None:
    """Per-node checks. Cross-column coherence is in validate_multicolumn (below)."""
    cols = node.get("columns")
    if not isinstance(cols, list) or len(cols) < 2:
        err(f"{path}.columns", "must have at least 2 columns")
        return

    seen_col_ids = set()
    for k, col in enumerate(cols):
        for field in ("id", "width", "content"):
            if field not in col:
                err(f"{path}.columns[{k}].{field}", "required")
        if "id" in col:
            if col["id"] in seen_col_ids:
                err(
                    f"{path}.columns[{k}].id",
                    f"duplicate column id '{col['id']}'"
                )
            else:
                seen_col_ids.add(col["id"])

        # Recurse into each column's content (which is itself a primitive)
        if "content" in col:
            validate_node(col["content"], f"{path}.columns[{k}].content", err, warn)


def validate_spacer(node: dict, path: str, err, warn) -> None:
    if "height" not in node:
        err(f"{path}.height", "required on spacer")
    elif not isinstance(node["height"], int) or node["height"] < 1:
        err(f"{path}.height", "must be positive integer")


def validate_link(link: dict, path: str, err) -> None:
    if not isinstance(link, dict):
        err(path, "link must be an object")
        return
    for field in ("href", "alias"):
        if field not in link:
            err(f"{path}.{field}", "required on link")
        elif not link[field]:
            err(f"{path}.{field}", "must be non-empty")


def validate_multicolumn(mc: dict, path: str, err, warn,
                          desktop_width: int, mobile_width: int) -> None:
    """Cross-column coherence: gap references and width overflow."""
    cols = mc.get("columns", [])
    col_ids = {c.get("id") for c in cols if isinstance(c, dict) and "id" in c}

    # Gap references must point to existing columns
    for k, gap in enumerate(mc.get("gaps", [])):
        between = gap.get("between", [])
        if not isinstance(between, list) or len(between) != 2:
            err(f"{path}.gaps[{k}].between", "must reference exactly 2 columns")
            continue
        for col_ref in between:
            if col_ref not in col_ids:
                err(
                    f"{path}.gaps[{k}].between",
                    f"column id '{col_ref}' not found. Available: {sorted(filter(None, col_ids))}"
                )

    # Width overflow check on mobile.
    # If columns DON'T stack on mobile (mobileLayout: "preserve") AND use pixel widths,
    # the sum of widths + gaps must fit in the mobile container.
    mobile_layout = mc.get("mobileLayout", "stack")
    if mobile_layout == "preserve":
        total_mobile_width = 0
        all_pixel_widths = True
        for col in cols:
            w = col.get("mobile", {}).get("width") or col.get("width")
            if isinstance(w, int):
                total_mobile_width += w
            else:
                # String like "14%" — percentage; skip pixel check
                all_pixel_widths = False
                break

        if all_pixel_widths:
            gap_total = sum(
                (g.get("mobile", g.get("desktop", 0)) or 0)
                for g in mc.get("gaps", [])
            )
            outer = mc.get("outerPadding", {}) or {}
            h_padding = (outer.get("left", 0) or 0) + (outer.get("right", 0) or 0)
            total = total_mobile_width + gap_total + h_padding

            if total > mobile_width:
                err(
                    path,
                    f"multiColumn with mobileLayout='preserve' has total width "
                    f"{total}px on mobile ({total_mobile_width} cols + {gap_total} gaps "
                    f"+ {h_padding} padding) — exceeds mobile container width {mobile_width}px. "
                    f"This will force horizontal scrolling and break the email's responsive layout."
                )

    # Width overflow on desktop (always relevant)
    total_desktop_width = 0
    all_pixel_widths_desktop = True
    for col in cols:
        w = col.get("width")
        if isinstance(w, int):
            total_desktop_width += w
        else:
            all_pixel_widths_desktop = False
            break

    if all_pixel_widths_desktop:
        gap_total_desktop = sum(
            (g.get("desktop", 0) or 0) for g in mc.get("gaps", [])
        )
        outer = mc.get("outerPadding", {}) or {}
        h_padding = (outer.get("left", 0) or 0) + (outer.get("right", 0) or 0)
        total = total_desktop_width + gap_total_desktop + h_padding

        if total > desktop_width:
            err(
                path,
                f"multiColumn total width on desktop is {total}px "
                f"({total_desktop_width} cols + {gap_total_desktop} gaps + {h_padding} padding) — "
                f"exceeds desktop container width {desktop_width}px."
            )


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <spec.json>", file=sys.stderr)
        sys.exit(2)

    try:
        with open(sys.argv[1]) as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(2)

    issues = validate(spec)
    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARN"]

    if errors:
        print(f"\n❌ {len(errors)} error(s):\n")
        for issue in errors:
            print(f"  [ERROR] {issue['path']}")
            print(f"          {issue['message']}\n")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):\n")
        for issue in warnings:
            print(f"  [WARN]  {issue['path']}")
            print(f"          {issue['message']}\n")

    if not errors and not warnings:
        print(f"✅ {sys.argv[1]} is valid")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
