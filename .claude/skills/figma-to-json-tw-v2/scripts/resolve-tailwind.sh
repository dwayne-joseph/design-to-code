#!/usr/bin/env bash
#
# resolve-tailwind.sh — Run the Tailwind CLI over every .jsx file in a directory,
# then rewrite each .jsx so className="..." becomes style={{...}}.
#
# Usage:
#   resolve-tailwind.sh <jsx-directory>
#
# Reads:
#   <jsx-directory>/*.jsx   — JSX files saved during Phase 3a
#
# Writes:
#   <jsx-directory>/decoded.css       — the Tailwind-resolved stylesheet
#   <jsx-directory>/*.inlined.jsx     — one inlined JSX file per input JSX
#
# Hard-codes the path to Tailwind v3.4 inside @mermaid-js/mermaid-cli's node_modules.
# This is intentional: the figma-to-json-tw skill assumes the Claude chat environment
# where this dependency is reliably present. If it disappears, this script fails
# loudly and the skill cannot proceed.

set -euo pipefail

# ----------------------------------------------------------------------------
# Locate Tailwind
# ----------------------------------------------------------------------------
TAILWIND_CLI="/home/claude/.npm-global/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/tailwindcss/lib/cli.js"

if [ ! -f "$TAILWIND_CLI" ]; then
  cat >&2 <<EOF

ERROR: Tailwind CLI not found at the expected path:
  $TAILWIND_CLI

The figma-to-json-tw skill depends on the Tailwind binary bundled with
@mermaid-js/mermaid-cli in this environment. If that dependency has been
removed or moved, this skill cannot run.

EOF
  exit 1
fi

# ----------------------------------------------------------------------------
# Locate this script's own directory (so we can find inline-styles.py next to it)
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INLINE_STYLES="$SCRIPT_DIR/inline-styles.py"

if [ ! -f "$INLINE_STYLES" ]; then
  echo "ERROR: inline-styles.py not found next to resolve-tailwind.sh" >&2
  exit 1
fi

# ----------------------------------------------------------------------------
# Parse args
# ----------------------------------------------------------------------------
if [ $# -ne 1 ]; then
  echo "usage: resolve-tailwind.sh <jsx-directory>" >&2
  exit 2
fi

JSX_DIR="$1"

if [ ! -d "$JSX_DIR" ]; then
  echo "ERROR: not a directory: $JSX_DIR" >&2
  exit 2
fi

# Use shopt or nullglob to handle the case where no .jsx files exist
shopt -s nullglob
JSX_FILES=("$JSX_DIR"/*.jsx)
# Exclude any existing .inlined.jsx files from a previous run
FILTERED=()
for f in "${JSX_FILES[@]}"; do
  case "$f" in
    *.inlined.jsx) ;;
    *) FILTERED+=("$f") ;;
  esac
done
JSX_FILES=("${FILTERED[@]}")

if [ ${#JSX_FILES[@]} -eq 0 ]; then
  echo "ERROR: no .jsx files found in $JSX_DIR" >&2
  exit 2
fi

# ----------------------------------------------------------------------------
# Step 1: Run Tailwind CLI once across all JSX files in the directory.
# ----------------------------------------------------------------------------
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

# Minimal Tailwind config: scan the JSX directory, no preflight (we don't want
# baseline resets — we only want class rules).
cat > "$TMPDIR/tailwind.config.js" <<EOF
module.exports = {
  content: ['$JSX_DIR/*.jsx'],
  corePlugins: { preflight: false },
}
EOF

# Minimal input CSS: just request utility class generation.
echo "@tailwind utilities;" > "$TMPDIR/input.css"

CSS_OUT="$JSX_DIR/decoded.css"

echo ">>> running Tailwind CLI over ${#JSX_FILES[@]} JSX file(s)..." >&2
node "$TAILWIND_CLI" \
  -c "$TMPDIR/tailwind.config.js" \
  -i "$TMPDIR/input.css" \
  -o "$CSS_OUT" \
  --no-autoprefixer 2>&1 | sed 's/^/  /' >&2

if [ ! -s "$CSS_OUT" ]; then
  echo "ERROR: Tailwind CLI produced no output" >&2
  exit 1
fi

RULE_COUNT=$(grep -c '^\.' "$CSS_OUT" || true)
echo ">>> $CSS_OUT contains $RULE_COUNT class rules" >&2

# ----------------------------------------------------------------------------
# Step 2: For each input JSX, run inline-styles.py to produce a .inlined.jsx
# ----------------------------------------------------------------------------
echo ">>> inlining styles into ${#JSX_FILES[@]} file(s)..." >&2

for jsx in "${JSX_FILES[@]}"; do
  base="$(basename "$jsx" .jsx)"
  out="$JSX_DIR/$base.inlined.jsx"
  python3 "$INLINE_STYLES" "$jsx" "$CSS_OUT" > "$out"
done

echo ">>> done. Inlined JSX files written next to each source JSX." >&2
