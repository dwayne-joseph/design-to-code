#!/usr/bin/env bash
#
# PostToolUse hook — auto-saves get_design_context JSX responses to disk.
#
# The skill writes an intent file to /tmp/figma-next-jsx.json before every
# get_design_context call. This hook reads it, saves the JSX, checks for
# truncation, appends to a manifest, and runs inline-styles.py if
# decoded.css already exists (speeds up re-runs of the same email).
#
# Intent file format:
#   {
#     "saveTo":       "/abs/path/to/{work}/jsx/frame-desktop.jsx",
#     "workDir":      "/abs/path/to/{work}",
#     "checkNodeIds": ["40000030:422", "40000030:430"]   // frame calls only
#   }
#
# Reports back to Claude via stdout (hookSpecificOutput):
#   savedTo, size, truncated, missingNodeIds, autoInlined

set -euo pipefail

INTENT_FILE="/tmp/figma-next-jsx.json"
INPUT=$(cat)

# No intent file → not a skill-managed call; exit silently.
if [ ! -f "$INTENT_FILE" ]; then
  exit 0
fi

# Read and immediately consume the intent file so a failed run can't reuse it.
SAVE_TO=$(jq -r '.saveTo' "$INTENT_FILE")
WORK_DIR=$(jq -r '.workDir // empty' "$INTENT_FILE")
CHECK_IDS=$(jq -c '.checkNodeIds // []' "$INTENT_FILE")
rm -f "$INTENT_FILE"

if [ -z "$SAVE_TO" ] || [ "$SAVE_TO" = "null" ]; then
  exit 0
fi

# ── Extract JSX ──────────────────────────────────────────────────────────────
# get_design_context returns a JSON object; the JSX lives in .code.
# Fall back to .jsx, then stringify the whole response as a last resort.
mkdir -p "$(dirname "$SAVE_TO")"

echo "$INPUT" | jq -r '
  if (.tool_response | type) == "object" then
    .tool_response.code // .tool_response.jsx // (.tool_response | tostring)
  else
    .tool_response
  end
' > "$SAVE_TO"

SAVED_SIZE=$(wc -c < "$SAVE_TO" | tr -d ' ')

if [ "$SAVED_SIZE" -eq 0 ]; then
  jq -n '{"hookSpecificOutput": {"error": "tool_response was empty — JSX not saved", "savedTo": null}}'
  exit 0
fi

# ── Truncation check ─────────────────────────────────────────────────────────
# For frame-level calls the intent file includes checkNodeIds. grep for each
# expected data-node-id attribute and collect any that are absent.
MISSING_IDS="[]"
ID_COUNT=$(echo "$CHECK_IDS" | jq 'length')

if [ "$ID_COUNT" -gt 0 ]; then
  MISSING_IDS=$(
    echo "$CHECK_IDS" | jq -r '.[]' | while IFS= read -r node_id; do
      if ! grep -qF "data-node-id=\"${node_id}\"" "$SAVE_TO" 2>/dev/null; then
        printf '%s\n' "$node_id"
      fi
    done | jq -R . | jq -s .
  )
fi

TRUNCATED="false"
if [ "$(echo "$MISSING_IDS" | jq 'length')" -gt 0 ]; then
  TRUNCATED="true"
fi

# ── Manifest ─────────────────────────────────────────────────────────────────
if [ -n "$WORK_DIR" ] && [ "$WORK_DIR" != "null" ]; then
  MANIFEST_DIR="$WORK_DIR/jsx"
  mkdir -p "$MANIFEST_DIR"
  NODE_ID=$(echo "$INPUT" | jq -r '.tool_input.nodeId // empty')
  TS=$(date +%s)
  printf '{"nodeId":"%s","file":"%s","size":%s,"ts":%s}\n' \
    "$NODE_ID" "$SAVE_TO" "$SAVED_SIZE" "$TS" >> "$MANIFEST_DIR/manifest.jsonl"
fi

# ── Auto-inline if decoded.css already exists ─────────────────────────────────
# On re-runs of the same email decoded.css is already present. Running
# inline-styles.py here means Phase 3a only needs to regenerate CSS, not
# re-inline every file.
AUTO_INLINED="false"
if [ -n "$WORK_DIR" ] && [ "$WORK_DIR" != "null" ]; then
  DECODED_CSS="$WORK_DIR/jsx/decoded.css"
  HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  INLINE_STYLES="$HOOK_DIR/../skills/figma-to-json-tw-v2/scripts/inline-styles.py"

  if [ -f "$DECODED_CSS" ] && [ -f "$INLINE_STYLES" ]; then
    INLINED_PATH="${SAVE_TO%.jsx}.inlined.jsx"
    if python3 "$INLINE_STYLES" "$SAVE_TO" "$DECODED_CSS" > "$INLINED_PATH" 2>/dev/null; then
      AUTO_INLINED="true"
    fi
  fi
fi

# ── Report back to Claude ─────────────────────────────────────────────────────
jq -n \
  --arg     savedTo    "$SAVE_TO" \
  --argjson size       "$SAVED_SIZE" \
  --argjson truncated  "$TRUNCATED" \
  --argjson missingIds "$MISSING_IDS" \
  --argjson inlined    "$AUTO_INLINED" \
  '{
    hookSpecificOutput: {
      savedTo:        $savedTo,
      size:           $size,
      truncated:      $truncated,
      missingNodeIds: $missingIds,
      autoInlined:    $inlined
    }
  }'

exit 0
