#!/usr/bin/env python3
"""
HTML output validator for the json-to-html skill.

Usage:
    python3 validate-html.py path/to/output.html [path/to/spec.json]

Exit code 0 = valid. Non-zero = invalid; prints all issues found.

If the spec.json is provided, the validator reads `annotations.stripColors` from
it and checks that none of those colors appear in the rendered HTML. Without the
spec, scaffolding color leakage isn't checked (the validator has no way to know
what counts as scaffolding for this particular email).

This validator catches structural compliance failures from the Merkle/DEG Email
UI coding standards. It's a final pre-flight check before the HTML ships.

Checks include:
- Forbidden tags (<div> for layout, <p>, <strong>, <em>, <h1>-<h6>)
- Image attribute completeness (alt, width, height, border:0, display:block)
- Link attribute completeness (href, alias, target, color, text-decoration,
  font-family, font-size)
- Text cell typography completeness (font-family, font-size, line-height,
  mso-line-height-rule:exactly, color)
- Table presentation attributes (cellpadding, cellspacing, border, role)
- Padding shorthand discipline (4-value only, no individual sides inline)
- VML wrapping on click-tracked elements (forbidden — breaks ESP tracking)
- Scaffolding color leakage (read from spec.json's annotations.stripColors)
- AMPScript subject line binding present
"""
import json
import re
import sys
from html.parser import HTMLParser
from typing import List, Set


# Tags forbidden in email HTML per coding standards
FORBIDDEN_TAGS = {"p", "strong", "em", "h1", "h2", "h3", "h4", "h5", "h6"}

# VML elements that must not wrap click-tracked elements
VML_WRAPPING_ELEMENTS = {"v:rect", "v:roundrect", "w:anchorlock"}


class EmailHTMLValidator(HTMLParser):
    """Streaming validator that walks the HTML and accumulates issues."""

    def __init__(self, scaffolding_colors: Set[str]):
        super().__init__()
        self.issues: List[dict] = []
        # Track <a> open state for VML-wrap detection
        self.inside_vml = []  # stack of currently-open VML tags
        # Normalize scaffolding colors to lowercase for case-insensitive matching
        self.scaffolding_colors = {c.lower() for c in scaffolding_colors}

    def error(self, msg: str, severity: str = "ERROR"):
        self.issues.append({
            "severity": severity,
            "line": self.getpos()[0],
            "message": msg,
        })

    def warn(self, msg: str):
        self.error(msg, severity="WARN")

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)

        # Forbidden tags
        if tag in FORBIDDEN_TAGS:
            self.error(f"forbidden tag <{tag}> — use a <td> with appropriate font styling instead")

        # <div> is allowed only in specific places (preview text scaffolding, VML fallbacks)
        if tag == "div":
            style = attrs_d.get("style", "")
            normalized = style.replace(" ", "")
            if "display:none" not in normalized:
                self.warn(f"<div> found — divs should only be used for preview-text scaffolding, not layout")

        # Track VML element entries
        if tag in VML_WRAPPING_ELEMENTS:
            self.inside_vml.append(tag)

        # <a> inside VML is forbidden — breaks ESP click tracking
        if tag == "a" and self.inside_vml:
            self.error(
                f"<a> nested inside VML element <{self.inside_vml[-1]}> — "
                f"this breaks ESP click tracking. Use <td bgcolor> + <a display:block> instead."
            )

        # <table> attributes
        if tag == "table":
            for required in ("cellpadding", "cellspacing", "border"):
                if required not in attrs_d:
                    self.warn(f"<table> missing {required}=\"0\" attribute")
            if attrs_d.get("role") != "presentation":
                self.warn(f"<table> missing role=\"presentation\" attribute")

        # <img> attributes
        if tag == "img":
            for required in ("src", "alt", "width", "height"):
                if required not in attrs_d:
                    self.error(f"<img> missing {required} attribute")
            style = attrs_d.get("style", "")
            normalized = style.replace(" ", "")
            if "border:0" not in normalized:
                self.error(f"<img> missing border:0 in style attribute")
            if "display:block" not in normalized:
                self.error(f"<img> missing display:block in style attribute")

            # alt='' downstream rule: should be paired with decorative=true in JSON.
            # We can't enforce that from HTML alone; flag for human review.
            if attrs_d.get("alt") == "":
                self.warn(f"<img> with alt=\"\" — confirm this is decorative")

        # <a> attributes
        if tag == "a":
            href = attrs_d.get("href", "")
            if not href:
                self.error(f"<a> missing href attribute")
            if "alias" not in attrs_d:
                self.error(f"<a> missing alias attribute (ESP tracking)")
            if attrs_d.get("target") != "_blank":
                self.error(f"<a> missing target=\"_blank\"")
            style = attrs_d.get("style", "")
            normalized = style.replace(" ", "")
            for required in ("color:", "text-decoration:", "font-family:", "font-size:"):
                if required not in normalized:
                    self.error(f"<a> missing inline style property: {required.rstrip(':')}")

        # <td> with inline style — check padding shorthand and text typography
        if tag == "td":
            style = attrs_d.get("style", "")
            normalized = style.replace(" ", "")

            # Padding shorthand discipline: no individual sides inline
            for individual_side in ("padding-top:", "padding-right:", "padding-bottom:", "padding-left:"):
                if individual_side in normalized:
                    self.error(
                        f"<td> uses inline {individual_side.rstrip(':')} — "
                        f"use 4-value shorthand `padding: T R B L` instead"
                    )

            # If the <td> appears to contain text, it should have all five typography
            # properties. We use font-family as the trigger (not color) because:
            # - color: also matches inside background-color: and border-color:, which
            #   appear on bgcolor cells, button cells, and bordered boxes that hold
            #   <a> links or &nbsp; rather than loose text.
            # - font-family: is only used on real text cells, so it's a precise signal.
            # A genuine text cell will always have font-family set inline (it's the
            # first property a text-cell author writes); if font-family is absent,
            # the cell isn't text, regardless of what other color-adjacent properties
            # it may carry.
            looks_like_text_cell = "font-family:" in normalized

            if looks_like_text_cell:
                for required in ("font-family:", "font-size:", "line-height:", "color:"):
                    if required not in normalized:
                        self.warn(
                            f"<td> appears to contain text but missing inline style property: {required.rstrip(':')}"
                        )
                if "mso-line-height-rule:exactly" not in normalized:
                    self.warn(
                        f"<td> appears to contain text but missing mso-line-height-rule:exactly"
                    )

        # Scaffolding color leakage — only if we have a spec to read from
        if self.scaffolding_colors:
            all_attr_values = " ".join(f"{k}={v}" for k, v in attrs_d.items()).lower()
            for bad_color in self.scaffolding_colors:
                if bad_color in all_attr_values:
                    self.error(
                        f"<{tag}> contains scaffolding color {bad_color} — "
                        f"should be stripped per spec annotations.stripColors before rendering"
                    )

    def handle_endtag(self, tag):
        if tag in VML_WRAPPING_ELEMENTS:
            if self.inside_vml and self.inside_vml[-1] == tag:
                self.inside_vml.pop()

    def handle_data(self, data):
        # Check if a scaffolding color appears in text content
        if self.scaffolding_colors:
            data_lower = data.lower()
            for bad_color in self.scaffolding_colors:
                if bad_color in data_lower:
                    self.error(
                        f"text content contains scaffolding color {bad_color} — should be stripped"
                    )


def validate_html(html: str, scaffolding_colors: Set[str]) -> List[dict]:
    """Run all validation checks. Returns a list of issue dicts."""
    validator = EmailHTMLValidator(scaffolding_colors)
    validator.feed(html)

    # Top-level structural checks
    extra_issues = []

    # Mobile width class — base CSS provides .width360 as default
    if 'class="width360"' not in html and "class='width360'" not in html:
        extra_issues.append({
            "severity": "WARN",
            "line": 0,
            "message": (
                "No class=\"width360\" found — the desktop-width container should have a "
                "mobile-width class (typically .width360). If the email uses a non-standard "
                "mobile width, confirm the appropriate class is applied."
            )
        })

    # CSS bank assembled — look for @media block indicating mobile utility classes are present
    if "@media" not in html:
        extra_issues.append({
            "severity": "WARN",
            "line": 0,
            "message": (
                "No @media block found — CSS bank utility classes should be assembled "
                "into an @media block in the <style> tag"
            )
        })

    # AMPScript subject line binding
    if "%%=v(@subjectline)=%%" not in html:
        extra_issues.append({
            "severity": "WARN",
            "line": 0,
            "message": (
                "<title> doesn't contain AMPScript binding `%%=v(@subjectline)=%%` — "
                "SFMC won't bind subject line dynamically"
            )
        })

    # Section-padding architecture enforcement.
    #
    # A correctly-architected section has ONE outer <td> that owns the section's
    # padding and background, with content <tr> rows inside an inner <table>.
    #
    # The forbidden pattern is two or more consecutive sibling <tr> rows whose
    # top-level <td> elements all share the same bgcolor AND each carry a padding
    # with non-zero horizontal components.
    #
    # We track <table> nesting depth so we only check rows at the top content
    # level (depth ≤ 2: the outer wrapper table + the content table). Rows
    # deeper than that are inside lists, columns, or buttons and should be
    # skipped to avoid false positives.
    tr_block_re = re.compile(
        r"<tr[^>]*>\s*<td\b([^>]*)>",
        re.IGNORECASE,
    )
    table_open_re = re.compile(r"<table\b", re.IGNORECASE)
    table_close_re = re.compile(r"</table\b", re.IGNORECASE)
    bgcolor_re = re.compile(r"""bgcolor\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
    padding_re = re.compile(
        r"padding\s*:\s*(\d+)px\s+(\d+)px\s+(\d+)px\s+(\d+)px",
        re.IGNORECASE,
    )

    # Pre-compute the nesting depth at every character position by scanning
    # for <table> and </table> tags.
    depth_at = []  # list of (position, depth) sorted by position
    depth = 0
    events = []
    for m in table_open_re.finditer(html):
        events.append((m.start(), +1))
    for m in table_close_re.finditer(html):
        events.append((m.start(), -1))
    events.sort(key=lambda e: e[0])

    def get_depth_at(pos):
        """Return the <table> nesting depth at a given character position."""
        d = 0
        for epos, delta in events:
            if epos > pos:
                break
            d += delta
        return d

    # Build a list of (line_number, bgcolor, padding_lr_tuple) for every
    # <tr><td> at depth ≤ 2 (the outermost content table level).
    cells = []
    for m in tr_block_re.finditer(html):
        depth = get_depth_at(m.start())
        if depth > 2:
            continue  # Skip rows nested inside lists, columns, buttons
        td_attrs = m.group(1)
        line_no = html.count("\n", 0, m.start()) + 1
        bg_match = bgcolor_re.search(td_attrs)
        bgcolor = bg_match.group(1).lower() if bg_match else None
        pad_match = padding_re.search(td_attrs)
        if pad_match:
            _, r, _, l = pad_match.groups()
            padding_lr = (int(l), int(r))
        else:
            padding_lr = None
        cells.append((line_no, bgcolor, padding_lr))

    # Walk the cells looking for runs of 2+ consecutive matches with the same
    # bgcolor AND non-zero horizontal padding.
    run_start = None
    run_bgcolor = None
    for i, (line_no, bgcolor, padding_lr) in enumerate(cells):
        is_padded_bg_cell = (
            bgcolor is not None
            and padding_lr is not None
            and (padding_lr[0] > 0 or padding_lr[1] > 0)
        )
        if is_padded_bg_cell and bgcolor == run_bgcolor:
            # Continuing a run
            continue
        else:
            # End of any previous run — emit if it was 2+
            if run_start is not None and (i - run_start) >= 2:
                start_line = cells[run_start][0]
                end_line = cells[i - 1][0]
                extra_issues.append({
                    "severity": "ERROR",
                    "line": start_line,
                    "message": (
                        f"section-padding architecture violation: "
                        f"{i - run_start} consecutive <tr><td bgcolor=\"{run_bgcolor}\"> "
                        f"cells (lines {start_line}-{end_line}) each carry horizontal "
                        f"padding AND the same bgcolor. The section's padding and "
                        f"background must be hoisted to a single outer <td> wrapper "
                        f"with inner content rows that carry no section-level padding "
                        f"or bgcolor. See Step 7 of SKILL.md for the required pattern."
                    )
                })
            # Start a new run if this cell qualifies
            if is_padded_bg_cell:
                run_start = i
                run_bgcolor = bgcolor
            else:
                run_start = None
                run_bgcolor = None
    # Flush a run that extends to the end of the document
    if run_start is not None and (len(cells) - run_start) >= 2:
        start_line = cells[run_start][0]
        end_line = cells[-1][0]
        extra_issues.append({
            "severity": "ERROR",
            "line": start_line,
            "message": (
                f"section-padding architecture violation: "
                f"{len(cells) - run_start} consecutive <tr><td bgcolor=\"{run_bgcolor}\"> "
                f"cells (lines {start_line}-{end_line}) each carry horizontal "
                f"padding AND the same bgcolor. The section's padding and "
                f"background must be hoisted to a single outer <td> wrapper "
                f"with inner content rows that carry no section-level padding "
                f"or bgcolor. See Step 7 of SKILL.md for the required pattern."
            )
        })

    return validator.issues + extra_issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-html.py <output.html> [<spec.json>]", file=sys.stderr)
        sys.exit(2)

    try:
        with open(sys.argv[1]) as f:
            html = f.read()
    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(2)

    # Load scaffolding colors from spec if provided
    scaffolding_colors: Set[str] = set()
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2]) as f:
                spec = json.load(f)
            scaffolding_colors = set(spec.get("annotations", {}).get("stripColors", []))
            print(
                f"Reading scaffolding colors from {sys.argv[2]}: "
                f"{sorted(scaffolding_colors) if scaffolding_colors else 'none'}"
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: couldn't read spec at {sys.argv[2]} ({e}). "
                  f"Skipping scaffolding-color check.", file=sys.stderr)

    issues = validate_html(html, scaffolding_colors)
    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARN"]

    if errors:
        print(f"\n❌ {len(errors)} error(s):\n")
        for issue in errors:
            line = issue["line"]
            line_str = f"line {line}" if line else "(global)"
            print(f"  [ERROR] {line_str}")
            print(f"          {issue['message']}\n")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):\n")
        for issue in warnings:
            line = issue["line"]
            line_str = f"line {line}" if line else "(global)"
            print(f"  [WARN]  {line_str}")
            print(f"          {issue['message']}\n")

    if not errors and not warnings:
        print(f"✅ {sys.argv[1]} is valid")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
