# JSON Format — Email Spec

This file documents the JSON shape produced by `figma-to-json` and consumed by `json-to-html`. It's designed to describe any email faithfully, without assuming a specific industry, brand, or layout pattern.

The core idea: **describe what's there, not what category it belongs to.** Every email is a sequence of sections; every section is a sequence of primitive visual elements. The extraction skill captures whatever Figma shows; the coding skill renders it following coding standards.

---

## Top-level structure

```json
{
  "specVersion": "2.0.0",
  "meta": { ... },
  "annotations": { ... },
  "sections": [ ... ]
}
```

- `specVersion` — semver of the format. Both skills check compatibility on entry.
- `meta` — email-level metadata (name, subject line, preview text, container widths).
- `annotations` — email-wide transforms applied before rendering (scaffolding strip rules).
- `sections` — array of sections in DOM order (top to bottom).

---

## meta

```json
"meta": {
  "emailName": "Q4 Newsletter — December",
  "figmaFile": "abc123XYZ",
  "subjectLine": "Your December update is here",
  "previewText": "Inside: product launches, year-end tips, and more.",
  "desktopWidth": 600,
  "mobileWidth": 360,
  "openQuestions": [
    {"id": "hero-overlay-bake", "question": "Bake decorative bars into hero asset before launch — email HTML cannot render absolute overlays.", "blocking": true}
  ]
}
```

- `emailName` (required) — human-readable identifier.
- `figmaFile` — Figma file key, for traceability.
- `subjectLine` — used in `<title>` AMPScript binding.
- `previewText` — inbox preview text.
- `desktopWidth` (default 600) and `mobileWidth` (default 360) — container widths. Standard for most emails.
- `openQuestions` — items the extraction skill couldn't resolve confidently and that production must address before launch (overlays to bake into assets, missing alt text on non-decorative images, ambiguous mobile widths, unresolved Tailwind classes). **Do NOT use `openQuestions` for placeholder values that are expected to be swapped at production time** — placeholder image URLs (Figma-hosted), placeholder hrefs (`"#"`), and placeholder aliases are normal and require no flagging.

---

## annotations

Email-wide stripping/recoloring rules. Both skills apply these to text content before rendering.

```json
"annotations": {
  "stripBrackets": true,
  "stripColors": ["#FF00B7", "#FF25DB"],
  "recolorMap": { "#FF00B7": "#414042" }
}
```

- `stripBrackets` (default false) — when true, square brackets `[ ]` used as editorial scaffolding around content are removed; the content inside is kept.
- `stripColors` — colors used as scaffolding markers in the source design. Any text run with a color in this list has its color dropped (falls back to parent block color). These values are **per-email** — the extraction skill detects what the design team uses for scaffolding in this specific file. Common examples include neon magenta, hot pink, or any unusually-saturated marker color used to flag dynamic content.
- `recolorMap` — source-to-target color replacements. Used when text is colored a scaffolding color in Figma but should render in body color. Common case: regulatory identifier strings shown in scaffolding color in the source but rendered in the email's body text color.

If a design has no scaffolding markers, leave `stripColors` as an empty array and `recolorMap` empty.

---

## sections

Each section is a labeled container with optional background, padding, and a sequence of primitive nodes.

```json
{
  "id": "section-3",
  "name": "Hero",
  "figmaNodeId": "1:42",
  "background": "#E4EEF7",
  "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
  "outerPadding": null,
  "skipInProduction": false,
  "nodes": [
    { primitive },
    { primitive }
  ]
}
```

- `id` (required) — stable identifier (`section-1`, `section-2`, ... in DOM order). Used by link aliases and for cross-reference.
- `name` (required) — human-readable label taken directly from the Figma layer name. Not interpreted as a type; just descriptive. Examples: "Header", "Hero", "Product Grid", "Footer", "CTA Block", whatever the Figma file calls it.
- `figmaNodeId` — source Figma node, for traceability.
- `background` — optional section background color (hex). When the section has an intermediate container in Figma, this is the container's background, not the section frame's.
- `padding` — content padding inside the background area (4-side object).
- `outerPadding` — optional. Spacing OUTSIDE the background area (4-side object). Used when the Figma section has an intermediate container pattern: the section frame has spacing (outer) and the inner container has background + padding (inner). When present, the HTML renderer produces nested wrappers: an outer `<td>` with `outerPadding` (no bgcolor) wrapping an inner `<td>` with `background` + `padding`. When absent or null, the renderer produces a single wrapper with `background` + `padding` as before.
- `skipInProduction` (default false) — if true, this section is editorial-only and won't be rendered as HTML body.
- `nodes` (required) — array of primitive elements in DOM order. Any combination of the primitives below.

Sections are flat. They don't nest. If a Figma file has nested groupings, flatten them into one section per visual row — that matches how email HTML actually renders (one `<tr>` per row).

---

## Primitives

These are the visual building blocks. Each one renders to a known HTML pattern (documented in the coding skill's `.claude/skills/json-to-html-v2/references/rendering-patterns.md`).

Every primitive node has a `type` field that names which primitive it is.

### image

```json
{
  "type": "image",
  "src": "https://cdn.example.com/hero.png",
  "alt": "Descriptive alt text",
  "width": 600,
  "height": 300,
  "decorative": false,
  "fluid": false,
  "alignment": "center",
  "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0},
  "link": {"href": "https://example.com", "alias": "hero-image"},
  "mobile": {
    "src": "https://cdn.example.com/hero-mobile.png",
    "width": 360,
    "height": 200,
    "preserveWidth": true,
    "alignment": "center",
    "hide": false,
    "padding": {"top": 0, "right": 0, "bottom": 0, "left": 0}
  }
}
```

- `src`, `alt`, `width`, `height` — required. `src` may be a placeholder URL (Figma-hosted asset URLs are fine — they get swapped to production CDN URLs downstream). Capture whatever URL Figma returned.
- `decorative` (default false) — if true, `alt` may be empty.
- `fluid` (default false) — if true, renders with `max-width:Npx; width:100%; height:auto;` so the image scales with the container.
- `alignment` (default "left") — `left`, `center`, or `right`.
- `link` — optional. Wraps the image in an `<a>` for clickable images. Requires `alias` for tracking.
- `mobile.src` — use a different image asset on mobile (e.g., a mobile-cropped variant).
- `mobile.preserveWidth` (default true) — keep the desktop pixel width on mobile (image stays left-anchored with whitespace to the right). Set false to make the image fluid on mobile only.
- `mobile.hide` (default false) — for desktop-only decorative elements.

### textBlock

A block of text. Block-level properties (font size, line height, color, alignment) apply to the whole block. The `content` array contains text runs that can override individual properties or add links.

```json
{
  "type": "textBlock",
  "content": [
    {"text": "Welcome to our "},
    {"text": "December update",
     "bold": true,
     "link": {"href": "#", "alias": "header-link"}},
    {"text": ". Inside you'll find..."}
  ],
  "fontFamily": "Arial, Helvetica, sans-serif",
  "fontSize": 16,
  "lineHeight": 20,
  "fontWeight": "normal",
  "color": "#414042",
  "alignment": "left",
  "padding": {"top": 0, "right": 24, "bottom": 12, "left": 24},
  "mobile": {
    "fontSize": 16,
    "lineHeight": 20,
    "padding": {"top": 0, "right": 24, "bottom": 12, "left": 24},
    "alignment": "left"
  }
}
```

Every text run is an inline object that can override styling for that segment:

```json
{
  "text": "the actual words",
  "bold": false,
  "italic": false,
  "underline": false,
  "color": "#0023C8",
  "fontSize": 12,
  "superscript": false,
  "link": { "href": "...", "alias": "..." }
}
```

**Verbatim rule (applies to ALL text):** the `text` value in every run MUST match Figma exactly. Word-for-word, including curly apostrophes, special punctuation, footnote markers, casing, and line breaks. The extraction skill never paraphrases, summarizes, or edits text. The coding skill renders it as-is. The only allowed text transformations are the annotation rules (`stripBrackets`, `stripColors`, `recolorMap`).

textBlocks handle every kind of text: headings (just set `fontWeight: "bold"` and a larger `fontSize`), body copy, hyperlinks, captions, footer disclaimers — all the same primitive.

`fontFamily` is optional — defaults to `"Arial, Helvetica, sans-serif"` when omitted. Only include it when the design uses a different web-safe font stack.

### button

```json
{
  "type": "button",
  "label": "Learn More",
  "link": {"href": "https://example.com/learn", "alias": "cta-learn-more"},
  "background": "#0023C8",
  "textColor": "#FFFFFF",
  "border": {"width": 4, "color": "#80CBFF"},
  "borderRadius": 0,
  "width": 444,
  "height": 88,
  "fontFamily": "Arial, Helvetica, sans-serif",
  "fontSize": 20,
  "lineHeight": 24,
  "fontWeight": "bold",
  "alignment": "center",
  "padding": {"top": 24, "right": 24, "bottom": 24, "left": 24},
  "mobile": {
    "width": 320,
    "height": 88,
    "fluid": false
  }
}
```

- `label`, `link`, `background`, `width`, `height` — required.
- `border` and `borderRadius` — optional styling.
- `alignment` (default "center") — alignment of the button within its container.
- `padding` — padding around the button (applied to the wrapping cell, not the button itself).
- `mobile.fluid` (default false) — if true, becomes `width:100% max-width:Npx` on mobile.

### list

A bulleted or numbered list.

```json
{
  "type": "list",
  "style": "bullet",
  "indent": 24,
  "bulletColor": "#414042",
  "fontFamily": "Arial, Helvetica, sans-serif",
  "fontSize": 16,
  "lineHeight": 20,
  "color": "#414042",
  "itemSpacing": 8,
  "padding": {"top": 0, "right": 24, "bottom": 12, "left": 24},
  "items": [
    {"content": [{"text": "First item"}]},
    {"content": [
      {"text": "Second item with a "},
      {"text": "link", "link": {"href": "#", "alias": "list-link"}, "underline": true}
    ]}
  ]
}
```

- `style` — `"bullet"` or `"numbered"`.
- `bulletColor` — color of the bullet character or number, independent from text color.
- `indent` (default 24) — left padding in pixels.
- `itemSpacing` (default 0) — spacing between items in pixels.
- Each item's `content` is an array of textRuns (same shape as textBlock content).

### multiColumn

A row of columns side-by-side on desktop. By default, stacks vertically on mobile. Vertical dividers between columns are expressed as `borderLeft` on the column, not as standalone primitives. Horizontal colored bars between sections are expressed as a section's `<td bgcolor>` — not a standalone primitive.

```json
{
  "type": "multiColumn",
  "background": "#FFFFFF",
  "alignment": "left",
  "verticalAlignment": "top",
  "mobileLayout": "stack",
  "columns": [
    {
      "id": "logo-col",
      "width": 232,
      "alignment": "left",
      "padding": {"top": 0, "right": 50, "bottom": 0, "left": 0},
      "content": { "type": "image", "src": "...", "alt": "Product logo", "width": 232, "height": 90 },
      "mobile": {
        "preserveWidth": true,
        "hide": false,
        "alignment": "left"
      }
    },
    {
      "id": "links-col",
      "width": 201,
      "borderLeft": {"width": 1, "color": "#0023C8", "hideOnMobile": true},
      "alignment": "left",
      "padding": {"top": 0, "right": 0, "bottom": 0, "left": 24},
      "content": { "type": "textBlock", "content": [{"text": "Column 2 text"}], "fontSize": 16, "lineHeight": 18, "color": "#414042" },
      "mobile": {
        "preserveWidth": true,
        "hide": false,
        "alignment": "left"
      }
    }
  ],
  "gaps": [
    {"between": ["logo-col", "links-col"], "desktop": 0, "mobile": 24, "direction": "auto"}
  ]
}
```

**Fixed-height interactive cell example** (rating boxes, badges, button-like cells with single-line text):

```json
{
  "id": "cxq-rating-1",
  "width": 72,
  "height": 48,
  "background": "#FFFFFF",
  "border": {"top": 1, "right": 1, "bottom": 1, "left": 1, "color": "#707070"},
  "link": {"href": "#", "alias": "cxq-rating-1"},
  "content": {
    "type": "textBlock",
    "content": [{"text": "1"}],
    "fontSize": 16,
    "lineHeight": 48,
    "color": "#000000",
    "fontWeight": "bold",
    "alignment": "center"
  },
  "mobile": {
    "width": 40,
    "height": 40,
    "preserveWidth": false
  }
}
```

**The line-height-equals-height technique:** when a column has a fixed `height` and contains a single-line `textBlock`, set the textBlock's `lineHeight` equal to the column's `height` (and `mobile.lineHeight` equal to `mobile.height`). This is how the HTML renderer vertically centers the text in a fixed-height cell — see "Fixed-height interactive cell" in the json-to-html rendering patterns. Padding-based centering does not adapt across breakpoints; line-height does.

- `columns` (required, min 2) — named array of columns. Each column has its own width, optional styling, and exactly one `content` primitive.
- `width` (required) — column width in pixels (or percentage string like `"14%"`).
- `height` (optional) — fixed pixel height. Required when the column has any of: `background`, `border`, or `link` AND contains a single-line text element. Without `height`, the rendered cell collapses to its content's natural height. With `height`, the renderer sets a fixed cell height and uses `line-height` for vertical centering of the content.
- `background` (on a column, optional) — column-level background color (hex). For cells where the visual fill belongs to the column itself (rating boxes, badges).
- `border` (on a column, optional) — per-side border widths and color: `{top, right, bottom, left, color}`. For columns that visually appear as bounded boxes.
- `link` (on a column, optional) — makes the entire column area clickable. The renderer wraps the column's content in an `<a>` accordingly.
- `borderLeft` (on a column, optional) — vertical divider rendered as CSS `border-left` on the `<th>`. The `hideOnMobile` flag tells the coding skill to add a `border-none` class for mobile removal.
- `gaps` — explicit named gaps between columns. Each gap references two column IDs and specifies pixel values for desktop and optionally mobile. `direction: "auto"` = horizontal on desktop, vertical on mobile.
- `alignment` (default "left") — horizontal alignment of the column group within its container. Maps from Figma's `items-*` value.
- `verticalAlignment` (default "top") — vertical alignment of columns relative to each other.
- `mobileLayout` (default "stack") — `stack` makes columns drop vertically on mobile; `preserve` keeps them horizontal (rarely needed; used for narrow inline rows like rating scales).

**Columns can use percentage widths** by passing strings like `"14%"` instead of integers. Useful for layouts that must scale predictably across breakpoints (rating scales, navigation bars, equal-width grids).

**Column width preservation on mobile:**
- Default: `mobile.preserveWidth: true` — column keeps its desktop pixel width when stacked.
- To expand the column to full width on mobile, set `mobile.preserveWidth: false`.
- To shrink to a specific mobile width (e.g., scale-rating boxes shrinking from desktop size to mobile size), set `mobile.width` to the target.
- To hide on mobile entirely, set `mobile.hide: true`.
- To set a different mobile height (for fixed-height cells that shrink on mobile), set `mobile.height` to the target.

### spacer

An empty vertical gap between elements. Use when padding on adjacent elements isn't enough.

```json
{
  "type": "spacer",
  "height": 24,
  "mobile": {
    "height": 16
  }
}
```

Renders as `<tr><td height="24" style="height:24px; font-size:0; line-height:0;">&nbsp;</td></tr>`.

---

## Shared types

### padding

Always a 4-side pixel object. Never a CSS string, never partial.

```json
{"top": 12, "right": 24, "bottom": 12, "left": 24}
```

### hexColor

6-digit hex with leading hash. 3-digit shortcuts not allowed.

```
"#0023C8"
```

### link

```json
{"href": "https://example.com", "alias": "tracking-name"}
```

- `href` — any URL string, including `"#"` or other placeholder values. Must be present and non-empty (the field must exist on every link so downstream tooling can find it). Actual URL gets swapped to production at production time; the extraction skill captures whatever Figma shows.
- `alias` — tracking name (ESP-specific; e.g., SFMC uses this for click reporting). Must be unique across the email and non-empty. Alias values themselves may be placeholders that get swapped to ESP-specific codes at production time — what matters is uniqueness within the spec so collisions are caught early.

---

## Validation rules

The extraction skill validates its output before handoff. The coding skill re-validates on entry (defense in depth).

**Required fields**
- Top-level: `specVersion`, `meta`, `annotations`, `sections`.
- Every section: `id`, `name`, `nodes`.
- Every primitive node: `type` field matching a known primitive name.
- Every image: `src`, `alt`, `width`, `height`.
- Every button: `label`, `link`, `background`, `width`, `height`.
- Every link: `href`, `alias`.

**Value constraints**
- All hex colors are 6-digit with `#`.
- All padding objects have all 4 sides as integers ≥ 0.
- `alt` is empty only when `decorative: true`.
- No color value matches an entry in `annotations.stripColors` (scaffolding leakage check).
- Every text run has a non-empty `text` value. Placeholder image URLs and `"#"` hrefs are allowed, but text content is never a placeholder — if Figma shows text, the spec captures the exact text.

**Coherence checks**
- Every section ID is unique.
- Every link alias is unique across the email.
- Every multi-column gap references column IDs that exist in the same multiColumn's `columns` array.
- For each multiColumn, sum of column widths (when expressed in pixels) + gap widths ≤ container width (the larger of desktop and mobile minus padding).

---

## Schema versioning

The current version is `2.0.0`. Versioning is semver:
- **Major** bump when the JSON shape changes in a breaking way (e.g., renaming a top-level field).
- **Minor** bump when new optional fields or primitives are added.
- **Patch** bump for documentation-only changes.

Both skills check `specVersion` on entry. If the major version doesn't match what the skill supports, the skill refuses the file.
