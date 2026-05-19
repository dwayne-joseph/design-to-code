#!/usr/bin/env python3
"""
inline-styles.py — Replace Tailwind className attributes with resolved style={{...}} blocks.

Reads:
  - A JSX file (path as argv[1]) containing one or more `className="..."` attributes
  - A Tailwind-generated stylesheet (path as argv[2]) covering every class used in the JSX

Writes:
  - Modified JSX to stdout, with each className replaced by an inline style={{...}} object
    whose properties are the resolved CSS for that class string

Usage:
    python3 inline-styles.py section-8.jsx decoded.css > section-8.inlined.jsx

The output is the source of truth for the figma-to-json-tw Phase 3 per-section authoring step.
Claude reads the inlined JSX directly — no Tailwind class lookup needed at JSON-authoring time.

The script does mechanical work only:
- Parse CSS selectors, un-escape Tailwind's CSS-class escaping
- Strip Tailwind v3 opacity-variable bloat (--tw-*-opacity, rgb(R G B / var(...)))
- For each className, merge per-class CSS in source order (later classes win on conflict)
- Emit JSX with className replaced by style={{...}}

The script does NOT:
- Decode any Tailwind class itself — that's the CLI's job
- Identify primitives, structures, or design intent — that's Claude's job
- Make per-side merging decisions (padding-top/right/bottom/left stay as separate keys)
"""

import json
import re
import sys
from typing import Any


# ============================================================================
# CSS SELECTOR UN-ESCAPING
# ============================================================================
#
# Tailwind escapes special characters in CSS selectors with backslashes:
#   className="text-[#0023c8]"  →  CSS selector ".text-\[\#0023c8\]"
#   className="size-[110px]"    →  CSS selector ".size-\[110px\]"
#
# We need to recover the original class name to match against className strings.

def unescape_selector(escaped: str) -> str:
    """Turn a Tailwind CSS-escaped selector body back into the source class name.

    Examples:
      'text-\\[\\#0023c8\\]'   → 'text-[#0023c8]'
      'font-\\[\\\'Arial\\:Bold\\\'\\2c sans-serif\\]'
                                   → "font-['Arial:Bold',sans-serif]"
    """
    # Handle CSS unicode escapes like \2c (comma) — \HHHH(space)
    def unicode_replace(m):
        return chr(int(m.group(1), 16))
    out = re.sub(r'\\([0-9a-fA-F]{1,6})\s?', unicode_replace, escaped)
    # Strip remaining single-char escapes (\[, \#, \', etc.)
    out = re.sub(r'\\(.)', r'\1', out)
    return out


# ============================================================================
# CSS PARSING
# ============================================================================

def parse_stylesheet(css: str) -> dict[str, list[tuple[str, str]]]:
    """Parse a Tailwind-generated stylesheet into {class_name: [(prop, value), ...]}.

    Properties are kept as an ordered list (not a dict) because a single class
    may legitimately repeat a property (e.g. a fallback declaration).
    """
    rules: dict[str, list[tuple[str, str]]] = {}

    # Match  .selector { body }  blocks. Selectors may contain escaped chars,
    # including CSS unicode escapes (\HH followed by a single space that's part
    # of the escape, not a selector terminator). So we accept either: a backslash
    # followed by any single character (possibly hex+space), or any non-whitespace
    # non-{-non-comma char.
    block_re = re.compile(
        r'\.((?:\\[0-9a-fA-F]{1,6}\s?|\\.|[^\s{,])+)\s*\{([^}]*)\}',
        re.DOTALL,
    )

    # Match individual  prop: value;  declarations inside a block body
    decl_re = re.compile(r'\s*([a-zA-Z-]+)\s*:\s*([^;]+?)\s*(?:;|$)')

    for block in block_re.finditer(css):
        selector_body = block.group(1)
        body = block.group(2)
        class_name = unescape_selector(selector_body)

        decls: list[tuple[str, str]] = []
        for decl in decl_re.finditer(body):
            prop = decl.group(1).strip()
            value = decl.group(2).strip()
            # Drop Tailwind v3 opacity-variable bloat
            if prop.startswith('--tw-') and prop.endswith('-opacity'):
                continue
            decls.append((prop, value))

        # Skip empty rule bodies (can happen after opacity-var stripping if a class only set the var)
        if decls:
            rules.setdefault(class_name, []).extend(decls)

    return rules


# ============================================================================
# VALUE CLEANUP
# ============================================================================

RGB_VAR_RE = re.compile(
    r'rgb\(\s*(\d+)\s+(\d+)\s+(\d+)\s*/\s*var\([^)]+\)\s*\)'
)

def clean_value(value: str) -> str:
    """Simplify Tailwind v3 color expressions to hex equivalents.

    rgb(0 35 200 / var(--tw-text-opacity, 1))  →  #0023C8
    """
    def to_hex(m):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"#{r:02X}{g:02X}{b:02X}"
    return RGB_VAR_RE.sub(to_hex, value)


# ============================================================================
# CSS PROPERTY → JSX STYLE KEY
# ============================================================================

def css_to_jsx_key(prop: str) -> str:
    """Convert a CSS property name to a JSX style key.

    font-family  →  fontFamily
    --tw-shadow  →  WebkitShadow  (vendor-prefix-style — but we drop these earlier)
    """
    # Vendor prefixes: -webkit-foo  →  WebkitFoo
    if prop.startswith('-webkit-'):
        return 'Webkit' + ''.join(p.capitalize() for p in prop[len('-webkit-'):].split('-'))
    if prop.startswith('-moz-'):
        return 'Moz' + ''.join(p.capitalize() for p in prop[len('-moz-'):].split('-'))
    # Custom properties: pass through verbatim (rare for our use case)
    if prop.startswith('--'):
        return prop
    # Standard property: dash-case → camelCase
    parts = prop.split('-')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


# ============================================================================
# CLASS-STRING → MERGED STYLE OBJECT
# ============================================================================

def resolve_classes(class_string: str, rules: dict[str, list[tuple[str, str]]]) -> dict[str, str]:
    """Walk classes in source order, merge their declarations into one style object.

    Later classes override earlier ones on the same property (CSS source-order rule —
    though in practice Tailwind ordering by class string position is approximate;
    real CSS specificity uses stylesheet order, but for our purposes className order
    is what designers intend).
    """
    style: dict[str, str] = {}
    unresolved: list[str] = []

    for cls in class_string.split():
        if cls not in rules:
            unresolved.append(cls)
            continue
        for prop, value in rules[cls]:
            jsx_key = css_to_jsx_key(prop)
            cleaned = clean_value(value)
            style[jsx_key] = cleaned

    return style, unresolved


# ============================================================================
# JSX REWRITING
# ============================================================================

# Match  className="..."  (single attribute, no curly-brace expressions for now;
# Figma's MCP output uses the static-string form exclusively, so this is safe).
CLASSNAME_RE = re.compile(r'className="([^"]+)"')


def format_style_object(style: dict[str, str]) -> str:
    """Format a style dict as a JSX style={{...}} attribute string.

    Numeric values stay quoted as strings — safer than guessing whether
    "30px" should be 30 (px) or "30px" (literal). React supports both,
    and our downstream consumer (the figma-to-json-tw Phase 3 author)
    reads strings either way.
    """
    if not style:
        return ''
    pairs = []
    for k, v in style.items():
        # Quote the key only if it isn't a valid JS identifier
        if re.match(r'^[A-Za-z_$][A-Za-z0-9_$]*$', k):
            key_repr = k
        else:
            key_repr = json.dumps(k)
        # Always quote the value as a string
        pairs.append(f'{key_repr}: {json.dumps(v)}')
    return 'style={{' + ', '.join(pairs) + '}}'


def rewrite_jsx(jsx: str, rules: dict[str, list[tuple[str, str]]]) -> tuple[str, list[str]]:
    """Replace each className="..." in the JSX with style={{...}}.

    Returns (rewritten_jsx, list_of_classes_that_had_no_rule).
    """
    all_unresolved: list[str] = []

    def replace(match):
        class_string = match.group(1)
        style, unresolved = resolve_classes(class_string, rules)
        all_unresolved.extend(unresolved)
        attr = format_style_object(style)
        if not attr:
            return ''  # className resolved to nothing — drop the attribute
        return attr

    return CLASSNAME_RE.sub(replace, jsx), all_unresolved


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: inline-styles.py <jsx-file> <css-file>\n")
        return 2

    jsx_path = sys.argv[1]
    css_path = sys.argv[2]

    try:
        jsx = open(jsx_path).read()
    except OSError as e:
        sys.stderr.write(f"error reading JSX file {jsx_path}: {e}\n")
        return 2

    try:
        css = open(css_path).read()
    except OSError as e:
        sys.stderr.write(f"error reading CSS file {css_path}: {e}\n")
        return 2

    rules = parse_stylesheet(css)
    rewritten, unresolved = rewrite_jsx(jsx, rules)

    sys.stdout.write(rewritten)

    # Diagnostic: stderr marker so callers can see whether anything went unresolved
    unique_unresolved = sorted(set(unresolved))
    sys.stderr.write(
        f">>> inline-styles: {jsx_path} — parsed {len(rules)} rules from stylesheet, "
        f"{len(unique_unresolved)} unresolved classes"
    )
    if unique_unresolved:
        sys.stderr.write(f": {', '.join(unique_unresolved)}")
    sys.stderr.write(" <<<\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
