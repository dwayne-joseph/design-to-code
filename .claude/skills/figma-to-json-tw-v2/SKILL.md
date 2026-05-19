---
name: figma-to-json-tw-v2
description: Extract any email design from Figma into a structured JSON specification ready for HTML rendering, using the real Tailwind CSS compiler to decode classes (more accurate than hand-decoding). Use this skill whenever the user shares a Figma URL for an email design, asks to "extract this Figma into JSON", wants to convert a Figma email design to a coded format, or needs a structured spec from a Figma file. This is the Tailwind-CLI variant of the figma-to-json family — prefer it when accurate decoding of unusual or arbitrary-value Tailwind classes matters. Works for any industry and any layout — the skill describes what's in the Figma file rather than fitting it to a predefined template. Always use this skill when a Figma email link is the input AND the goal is producing HTML, structured data, or anything downstream of the design — this skill comes first before any coding. The output is one JSON file that the `json-to-html` skill consumes.
---

# figma-to-json-tw

This skill extracts a Figma email design into a structured JSON specification consumed by the `json-to-html` skill. The JSON captures what Figma shows — no predefined module taxonomy. Every email is a sequence of sections made of primitives (image, text, button, list, multi-column, spacer), and the skill adapts to whatever structure the design uses.

## Core principle — Look first, then decode for precision

The hardest decisions in this skill are visual: is this an overlay or a column? does this row stack on mobile or shrink? is this scaffolding annotation or production content? Claude is a vision model — look first, then use the JSX and resolved CSS to fill in exact pixel values for what's already understood visually.

The flow:

1. **Discover** structure from metadata (cheap, XML-only) → enumerate sections + canvas-level siblings
2. **Look** at per-section screenshots → build visual understanding
3. **Decode** tokens and CSS → get exact values for what you understand
4. **Decide** all ambiguous calls in one pass → write a plan
5. **Author** JSON mechanically against the plan

## Two roles in this skill

- **`.claude/skills/figma-to-json-tw-v2/scripts/resolve-tailwind.sh`** does the mechanical Tailwind decoding: runs the real Tailwind CLI over every section's JSX once, then rewrites each `className="..."` as a fully-resolved `style={{...}}` block. Output: one `.inlined.jsx` file per input with every CSS property already computed.
- **Claude** does the visual interpretation and judgment: identifying structural patterns from screenshots, classifying overlays, transcribing text precisely, naming columns, deciding mobile behavior, locking in decisions in a written plan.

The skill assumes the Tailwind CLI is available at the path resolved by `resolve-tailwind.sh`. If that dependency disappears, the script fails loudly — there is no fallback to inline decoding. If the CLI isn't available, use the original `figma-to-json` skill instead.

## Working directory

Throughout this skill, `{work}` refers to a per-email working directory. On Claude Code locally, use `./emails/{email-name}/`. On the web sandbox, use `/home/claude/{email-name}/`. The final spec is written to `{outputs}/` — locally `./emails/{email-name}/`, on web `/mnt/user-data/outputs/`. Pick the paths once at the start and use them consistently.

---

## When to use this skill

- User provides a Figma file URL and wants to build an email from it
- User asks to "extract" or "analyze" a Figma email design
- User wants a JSON spec from a Figma file for any downstream use
- Any "figma → email" workflow — this skill comes first, before coding

If the user only wants to read a Figma file ("what does this design look like?") without producing structured output, this skill is overkill — use the Figma MCP tools directly instead.

---

## Workflow

Five phases. Don't skip them — each catches a class of errors the next can't detect. Visual phases (1 screenshots, 3c plan) feed Claude's judgment. Data phases (2, 3a, 3b) feed precision.

### Phase 1 — Discover (metadata-first, then per-section screenshots)

The goal of Phase 1 is to produce two things: a list of sections with paired node IDs at both breakpoints, and a per-section visual ground truth that the plan in Phase 3c can rely on. Do this metadata-first — `get_metadata` returns cheap XML and tells you everything about structure before any pixels are involved.

**Step 1 — Page metadata for both frames.**

```
Figma:get_metadata(nodeId=<desktop frame id>)
Figma:get_metadata(nodeId=<mobile frame id>)
```

Read each returned XML. For each frame, list:

- **Section children of the frame** in DOM order, with node ID, name, position, size. These are the email's sections.
- **Canvas-level siblings** — nodes living on the same page as the frame but parented OUTSIDE the frame (sibling to it in the page tree, not inside it). Bracket frames, registration marks, page-level annotations, decorative bars positioned above the canvas. Capture node ID and name for each. If the frame's metadata response doesn't show its siblings, call `get_metadata` with the page node ID (one level up) to list them.

If a frame's children come back collapsed, call `get_metadata` again with that frame's node ID to drill in. Don't proceed until every section is enumerated at both breakpoints.

**Step 2 — Pair sections across breakpoints.** Match section N at desktop to section N at mobile by DOM order. If counts disagree, note which breakpoint has extras — those are desktop-only or mobile-only sections that will get `mobile.hide: true` (or the desktop equivalent) in the JSON later.

**Step 3 — Design tokens.**

```
Figma:get_variable_defs(nodeId=<desktop frame id>)
Figma:get_variable_defs(nodeId=<mobile frame id>)
```

Brand and structural colors map to named tokens (`Brand/Primary: #0023C8`). Use these to recognize named colors in resolved CSS.

**Scaffolding markers.** Some design teams use saturated out-of-palette colors (neon magenta, hot pink) to flag dynamic content placeholders, MAT/regulatory codes, or editorial annotations. Giveaways:

- Token named `Variable`, `Annotation`, `Placeholder`, `Marker`, `Dynamic`
- Out-of-palette saturated value
- Square-bracket characters `[ ]` rendered in that color

If found, add to `annotations.stripColors` and (if appropriate) `annotations.recolorMap` later. If the design has none, leave those fields empty.

Create the working directories now (before fetching screenshots):

```
mkdir -p {work}/jsx
```

**Step 4 — Per-section screenshots.** For each section in the enumerated inventory:

```
Figma:get_screenshot(nodeId=<desktop section id>, maxDimension=1200) → {work}/jsx/section-{N}-desktop.png
Figma:get_screenshot(nodeId=<mobile section id>,  maxDimension=600)  → {work}/jsx/section-{N}-mobile.png
```

These are the visual ground truth for Phase 3c. No full-frame screenshot — section-resolution is what the plan needs, and per-section screenshots are what Claude actually opens during planning.

As you fetch each pair of screenshots, also open them and note one follow-up for Phase 3c:

- **Repeated assets** — same logo, icon, or image visible in multiple sections (header logo + footer logo is the canonical case). Note which sections share which asset.

**Why metadata-first.** The previous workflow took two full-frame screenshots, then narrated the inventory by eye, then called `get_metadata` to map names to IDs. Metadata gives you the inventory deterministically — node IDs, names, positions, sizes — without burning the screenshot budget on a thumbnail view that won't survive the plan phase anyway. Visual judgment moves to Phase 3c where it's needed at section resolution.

**Step 5 — Capture canvas-level siblings as open questions.** For each canvas-level sibling node from Step 1, decide:

- **Editorial scaffolding** (bracket frames, registration marks, page-level annotations) → skip in production, do not model in JSON.
- **Visual overlay on a section** (decorative bars over a hero, badge over an image) → apply the overlay rule: model only the base element, add a blocking `meta.openQuestions` entry instructing production to bake the overlay into the source asset before launch.

These decisions land in the plan in Phase 3c. There is no separate pre-scan file — the plan is the single judgment artifact.

### Phase 2 — Collect JSX (frame-first with per-section fallback)

JSX collection uses a hybrid strategy: try one call per breakpoint, fall back to per-section only when needed.

**Step 1 — Attempt frame-level JSX (two calls).** Always pass `excludeScreenshot: true` on every `get_design_context` call in this skill. The per-section screenshots from Phase 1 are already at the right resolution for Phase 3c; the embedded screenshot `get_design_context` returns by default is redundant and burns context.

```
Figma:get_design_context(nodeId=<desktop frame id>, excludeScreenshot=true) → {work}/jsx/frame-desktop.jsx
Figma:get_design_context(nodeId=<mobile frame id>,  excludeScreenshot=true) → {work}/jsx/frame-mobile.jsx
```

**Step 2 — Validate each frame response.** A frame call is successful only if ALL hold:

- Response contains JSX code (not just metadata). Figma returns metadata-only when the output is too large.
- File is not truncated mid-element (look for unclosed tags at EOF).
- Every section node ID from Phase 1 appears as a `data-node-id="{id}"` attribute somewhere in the JSX:

```
for id in <list of section nodeIds for this breakpoint>; do
  grep -q "data-node-id=\"$id\"" {work}/jsx/frame-{breakpoint}.jsx || echo "MISSING: $id"
done
```

If any section ID is missing from a frame's JSX, that breakpoint failed and needs per-section fallback. Breakpoints are checked independently — desktop may succeed while mobile fails.

**Step 3 — Per-section fallback for failed breakpoints.** For each breakpoint that failed validation, delete its `frame-{breakpoint}.jsx` and fetch per-section instead:

```
Figma:get_design_context(nodeId=<section id at this breakpoint>, excludeScreenshot=true)
  → {work}/jsx/section-{N}-{breakpoint}.jsx
```

If desktop succeeded but mobile failed (common — mobile frames are taller and hit the size limit first), only loop on mobile. Still cuts JSX calls roughly in half versus always going per-section.

**Step 4 — Record the strategy each breakpoint used:**

```
echo "desktop: frame" > {work}/jsx/.strategy   # or "desktop: per-section"
echo "mobile: frame" >> {work}/jsx/.strategy   # or "mobile: per-section"
```

**Why try frame-first.** Many emails return clean frame-level JSX with every section's node ID intact, especially short ones or designs without dense section content. Passing `excludeScreenshot: true` frees up response budget that would otherwise go to a thumbnail we don't need, which raises the size ceiling for the JSX itself. Cost of trying: two calls. Cost of being wrong: detected by Step 2 and recovered by Step 3 without losing any precision.

Do NOT run `.claude/skills/figma-to-json-tw-v2/scripts/resolve-tailwind.sh` during Phase 2. Do NOT author any JSON. The only goal is to land JSX on disk.

### Phase 3a — Resolve Tailwind (one shell command)

```
.claude/skills/figma-to-json-tw-v2/scripts/resolve-tailwind.sh {work}/jsx
```

The resolver picks up every `.jsx` file in the directory — `frame-desktop.jsx`, `frame-mobile.jsx`, and any `section-{N}-{breakpoint}.jsx` from Phase 2's fallback — and produces a matching `.inlined.jsx` for each. It doesn't care about the naming convention.

Produces:

- `{work}/jsx/decoded.css` — Tailwind-resolved stylesheet for every class used
- `{work}/jsx/frame-{breakpoint}.inlined.jsx` — for breakpoints that used frame-level
- `{work}/jsx/section-{N}-{breakpoint}.inlined.jsx` — for breakpoints that fell back to per-section

Watch stderr for an `unresolved classes` count. Zero is expected. Any non-zero: capture each unresolved class as a `meta.openQuestions` entry during planning.

If the script exits non-zero, the Tailwind CLI is unavailable — fall back to the original `figma-to-json` skill.

This is the only time the resolver runs. From here on, only `.inlined.jsx` files are read.

### Phase 3b — Judgment plan (all decisions in one pass)

**Before authoring any JSON, write a plan.** This phase locks in every interpretive decision in one place, surfaces ambiguity for review, and makes Phase 3c nearly mechanical.

**Read `.claude/skills/figma-to-json-tw-v2/references/json-format.md` once now** — it defines the exact shape of every primitive. You'll reference it as you plan.

Start the plan with an email-level header that captures what used to live in the pre-scan:

```
# PLAN — {email-name}

## Email
- Figma file: <fileKey>
- Frames: desktop <node id> ({W}×{H}) / mobile <node id> ({W}×{H})
- Sections (N, paired 1:1): list with node IDs at both breakpoints, plus working names
- Canvas-level siblings: classify each (scaffolding/skip OR overlay/bake-into-asset)
- Repeated assets (same logo/icon used in multiple sections): list with sizes
- Scaffolding colors: from Phase 1 design tokens, if any
- Email-level open questions: anything design must resolve before production (overlays to bake in, missing alt text, ambiguous mobile widths). Do NOT list placeholder Figma URLs, placeholder hrefs, or placeholder aliases — those are expected.
```

Then for each section in DOM order, write an entry covering:

1. **Section identity** — number, name, node IDs, dimensions at both breakpoints.
2. **Visual summary (from per-section screenshots)** — one or two sentences describing what the section looks like at each breakpoint. Open the screenshot. This is the visual anchor for every later decision.
3. **Structural pattern** — single-layer (root has bg + padding), intermediate container (outer padding wrapping inner bg + padding), or no-wrapper. Determined from the inlined JSX root carrying `data-node-id="{section id}"`:
   - **Single-layer:** root has both background AND padding. → `section.background` + `section.padding`. Walk root's children as content.
   - **Intermediate container:** root has padding, no background; single child has background and its own padding. → `section.outerPadding` = root's padding, `section.padding` = inner padding, `section.background` = inner background. Walk inner child's children as content.
   - **No wrapper:** root has neither. → leave `section.background` unset and `section.padding` zeroed. Walk root's children as content.
4. **Primitive sequence** — ordered list of primitives the section emits. Mapping from inlined JSX:
   - `<img>` → `image`. Width/height from the parent frame's style; the `<img>` itself usually `width:100%, height:100%`.
   - Text element → `textBlock` preserving text verbatim (special chars, bullets, whitespace).
   - `<a>` with a child whose style has both `background` and `padding` and a `color` → `button`.
   - Repeating bullet+text rows → `list`.
   - `<div>` with `display:flex` (no `flexDirection: column`) and multiple `<div>` children → `multiColumn`.
   - `<br>` or empty vertical gap → `spacer`.
   - Thin colored bar (1px width with bg, or `transform: rotate(90deg)`) between columns → `borderLeft`/`borderRight` on the adjacent column, NOT its own primitive.
5. **Judgment decisions** — explicit answer to every applicable judgment call from the catalog below. State the decision and the basis (screenshot, design token, canvas-sibling classification, etc.).
6. **Mobile deltas** — what's different at mobile (stacking, hidden elements, width changes). Compared from the inlined JSX for each breakpoint plus the two screenshots. To find a section's JSX at a given breakpoint:
   - If `{work}/jsx/.strategy` says that breakpoint used `frame`: open `{work}/jsx/frame-{breakpoint}.inlined.jsx` and locate the subtree whose root carries `data-node-id="{section id}"`.
   - If it used `per-section`: open `{work}/jsx/section-{N}-{breakpoint}.inlined.jsx` directly.
7. **Open questions raised by this section** — anything you can't resolve from the available inputs. These go into `meta.openQuestions` later.

Example section plan entry:

```
## section-2 — Hero
Nodes: desktop 40000030:422 / mobile 40000030:442 (600×420 / 360×252)

### Visual
Full-width photo, faces visible center-frame. Coral 8px + cyan 16px vertical
bars overlay right edge in Figma (canvas-level sibling, classified as overlay
in email-level header). Mobile has no bars visible.

### Structural pattern
Single-layer. Root has background-color #000 and padding 0.

### Primitives
1. image (full width, 600×420 desktop / 360×252 mobile)

### Judgment decisions
- Overlay bars → BAKE INTO IMAGE. Per overlay rule, do not model as multiColumn.
  Add blocking open question: "Bake coral+cyan decorative bars into hero asset
  before launch. Email HTML cannot render absolute overlays reliably."

### Mobile deltas
- Width: 600 → 360 (proportional). Image expands (fluid hero).
- mobile.preserveWidth: false (rare expansion case).

### Open questions
- Bake decorative bars into asset (blocking: true)
```

**The judgment catalog — answer each that applies, per section:**

Text content is always transcribed verbatim from Figma — special punctuation, footnote markers, casing, and line breaks preserved exactly. The skill never paraphrases, summarizes, or edits text. The only allowed transformations are the annotation rules (`stripBrackets`, `stripColors`, `recolorMap`). If a screenshot makes text hard to read, fetch a higher-resolution screenshot or fall back to the inlined JSX — don't approximate.

- **Scaffolding-color runs.** Identify every text run whose color appears in `annotations.stripColors`. Decide for each: (a) bracket character → emit plain, inherit color; (b) editorial label that won't render (e.g., `"Preheader: ["`) → drop the run; (c) real content miscolored in Figma → apply `recolorMap` and emit with the mapped color. Don't leave scaffolding colors to render-time.
- **Inherited colors and fonts.** When `<span>` styles lack `color`/`fontFamily`/`fontWeight`/`lineHeight`, walk the parent chain in the inlined JSX to find the inherited value. Note it in the plan so 3c doesn't re-discover it.
- **Mixed inline formatting.** Identify text blocks with multiple styled `<span>` children (bold, color, size, superscript). Plan a `textBlock` whose `content` array preserves each run in DOM order with its style.
- **fontFamily/fontWeight from Figma's `'Family:Weight'` convention.** Figma fonts resolve to e.g. `fontFamily: "'Arial:Bold',sans-serif"`. Split: `fontFamily: "Arial"`, and convert the weight (Regular/Normal → 400, Medium → 500, SemiBold → 600, Bold → 700, Black → 900). Default 400 if absent.
- **Multi-column naming.** Name every column (`logo-col`, `links-col`, etc.) from `data-name` or a meaningful slug.
- **Multi-gap rows.** A row with three children separated by two gaps has two distinct gap values. Each goes in `gaps[]` with explicit `between` references — never combined.
- **Mobile preservation vs expansion.** Default `mobile.preserveWidth: true`. Only set false for confirmed fluid elements (full-width hero, full-width CTA) — confirm against the mobile screenshot. When in doubt, preserve.
- **Scale-rating / fixed-pixel rows that must fit on mobile.** When a section has N elements of fixed pixel width that won't stack on mobile (1-7 scale, step indicator, nav), check `N × element_width ≤ mobile container width`. If desktop widths don't fit, extract mobile widths from the mobile inlined JSX. If you can't find them, halt and ask the user. Do not guess.
- **Overlay decorations on images.** Per the overlay rule below: model only the base element, add a blocking open question for production to bake the overlay in.
- **Identifier strings in scaffolding color.** Job codes, version stamps, MAT IDs colored as placeholders. Plan as body-color text; add the source color to `recolorMap` if in `stripColors`.

Note on placeholders: image `src` URLs from Figma, `"#"` hrefs, and placeholder alias strings are all expected — capture them as-is and don't flag them as open questions. Production swaps these downstream. `meta.openQuestions` is reserved for things production literally cannot fix without going back to design (bake-in-the-overlay items, ambiguous mobile widths, unresolved Tailwind classes, missing alt text on non-decorative images).

**Properties to ignore** (Figma artifacts, no rendering effect): `alignContent: stretch`, `minWidth: 1px`, `position: relative` without absolute children, `overflow: clip/hidden`, `whiteSpace: nowrap` on isolated blocks.

**The overlay rule (always applies):** When a screenshot shows a decorative element overlapping any other element, model only the base element at its full container dimensions and add a `meta.openQuestions` entry with `blocking: true` instructing production to bake the overlay into the source asset before launch. Never model an overlay as an adjacent multi-column sibling — that distorts the underlying image's width and crop. Example:

```
{
  "id": "hero-decorative-bars-overlay",
  "question": "The right edge of the hero has decorative vertical bars (coral 8px + cyan 16px) overlaying the photo in Figma. Email HTML cannot render this as an overlay. Bake the decorative bars into the exported hero image asset before launch so the photo+bars ship as one image.",
  "blocking": true
}
```

**Section background hygiene.** If a child has the same background as the section, omit it from the child's JSON — don't duplicate.

**Stop and review the plan before 3c.** Skim it end to end. Are all judgment calls answered? Are open questions clearly worded? Are mobile deltas captured? If the plan is incomplete, fix it before authoring JSON — Phase 3c is execution, not interpretation.

### Phase 3c — Author JSON (mechanical execution against the plan)

For each section in plan order:

1. Open the plan entry.
2. Locate the section's inlined JSX for each breakpoint per `{work}/jsx/.strategy`: either the relevant `data-node-id` subtree inside `frame-{breakpoint}.inlined.jsx`, or the standalone `section-{N}-{breakpoint}.inlined.jsx`. Every `style={{...}}` block is fully resolved CSS — read property values directly, do not re-decode Tailwind.
3. Emit the primitives the plan specifies, in the order it specifies, applying the judgment decisions already recorded. Pull exact values (colors, dimensions, padding, font sizes, line heights) from the inlined JSX.
4. **Per-side padding → JSON object.** Inlined JSX has `paddingTop/Right/Bottom/Left` keys; merge into a single `padding: {top, right, bottom, left}` object. Sides absent default to 0. Same for `border-*`.
5. Append the section to a scratch JSONL:

```
echo '{"id":"section-N","name":"...","nodes":[...]}' >> {work}/sections.jsonl
```

**Do NOT re-decode Tailwind from the source `.jsx` file.** If you find yourself looking at the source frame or section JSX (no `.inlined.` in the name) instead of the resolved version, the resolver missed a class — the plan should have already flagged it.

**Do NOT revisit judgment decisions in 3c.** If a decision feels wrong while authoring, stop, go back to 3b, update the plan, then resume. Don't drift mid-section.

### Phase 4 — Compose and validate

Assemble the final JSON from the JSONL scratch file:

```
python3 -c "
import json
sections = [json.loads(line) for line in open('{work}/sections.jsonl')]
spec = {
  'specVersion': '2.0.0',
  'meta': { ... },           # from plan email-level header + open questions
  'annotations': { ... },    # stripColors, stripBrackets, recolorMap from plan
  'sections': sections,
}
json.dump(spec, open('{outputs}/{email-name}-spec.json', 'w'), indent=2)
"
```

See `.claude/skills/figma-to-json-tw-v2/references/json-format.md` for the exact shape of every field. It is the contract between this skill and `json-to-html`.

Run the validator:

```
python3 .claude/skills/figma-to-json-tw-v2/scripts/validate.py {outputs}/{email-name}-spec.json
```

The validator catches:

- Missing required fields (colors, dimensions, alt text, link aliases)
- Empty `alt` without `decorative: true`
- Multi-column gap references to columns that don't exist
- Multi-column total width exceeding container width on either breakpoint
- Duplicate link aliases (tracking conflict)
- Scaffolding colors leaking into rendered content
- Empty text runs anywhere in the spec
- Section background inconsistency

**If validation fails, do NOT hand off.** Go back to the plan, identify which section's decisions were wrong, update the plan, re-author the affected sections, re-validate. Only output when the validator passes with zero errors.

Warnings can be addressed at the user's discretion — surface them but don't block.

---

## Do / Don't

| Do                                                                                      | Don't                                                              |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Discover structure from metadata before taking any screenshots                          | Take a full-frame screenshot just to count sections                |
| Use per-section screenshots as the visual anchor during planning                        | Try to make planning decisions from a 1200px-wide full-frame thumb |
| Write the plan to disk as the single judgment artifact                                  | Maintain a separate pre-scan file alongside the plan               |
| Lock in all interpretive decisions in Phase 3b                                          | Make judgment calls mid-authoring in 3c                            |
| Output JSON only                                                                        | Render HTML — that's the `json-to-html` skill's job                |
| Use the section's Figma name as-is                                                      | Categorize sections into predefined types ("header", "CTA module") |
| Transcribe all text word-for-word from Figma                                            | Paraphrase, summarize, or edit any text the spec captures          |
| Run `.claude/skills/figma-to-json-tw-v2/scripts/resolve-tailwind.sh` once after Phase 2 and read `.inlined.jsx` files for styling  | Read raw `.jsx` files for styling, or skip the resolver            |
| Flag any unresolved class in `meta.openQuestions`                                       | Drop unresolved classes silently                                   |
| Default to `mobile.preserveWidth: true`                                                 | Default to fluid expansion on mobile                               |
| Capture exactly what Figma shows                                                        | Make design decisions (changing colors, adjusting spacing)         |

---

## Output

The final deliverable is a single JSON file at `{outputs}/{email-name}-spec.json`.

After producing it, summarize for the user:

- Number of sections found (with their Figma names)
- Open questions captured (especially blocking ones)
- Validation result (errors blocked, warnings noted)

Then: **"Pass this JSON to the `json-to-html` skill in a NEW conversation to generate the HTML."** Running both skills in the same chat doubles context load — splitting them keeps each conversation efficient. The plan file in `{work}` is not needed by `json-to-html`; the spec is self-contained.
