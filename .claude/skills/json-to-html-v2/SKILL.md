---
name: json-to-html-v2
description: Render a structured JSON email spec into production HTML following Merkle/DEG Email UI coding standards. Use this skill whenever the user provides a JSON email spec (typically produced by the figma-to-json skill), asks to generate HTML from a JSON spec, wants to render an email from a structured design specification, or has a `.json` file describing email content. Works for any email type — the skill renders primitives following coding standards rather than fitting to a predefined template. Always use this skill when JSON describing email content needs to become deliverable HTML — this skill comes after figma-to-json in the email production workflow. The output is one HTML file ready for ESP upload.
---

# JSON → HTML Email Coding

## Core principle — Plan first, render mechanically

If `figma-to-json-tw` did its job, every visual decision is already encoded in the JSON spec. This skill should add **zero new visual interpretation** — its only job is mapping primitives to HTML patterns. To keep that boundary clean, classify and plan every section before writing any HTML. The plan tells you exactly which patterns and CSS classes to use; rendering then becomes execution.

The flow is therefore:

1. **Read** the spec and annotations
2. **Classify** every section before writing anything
3. **Plan** the HTML shape and CSS classes for each section (lookup-on-demand against references)
4. **Render** mechanically against the plan
5. **Validate** automatically before delivery

---

## Context management

This skill should run in a **separate conversation** from `figma-to-json-tw`. The JSON spec persists on disk — the user uploads it or points at it. Don't ask the user to paste the JSON into chat; read it from disk.

**Rule 1 — Lookup-on-demand for references.** Don't read `rendering-patterns.md` (33KB) or `css-bank.md` (15KB) in full upfront. Plan the email first (Step 3 below), then look up only the patterns and classes the plan calls out. By the time you start rendering, references are already cached and you're in pure execution mode.

**Rule 2 — Don't re-read reference files already in context.** If a reference was read earlier in this conversation, don't read it again.

**Rule 3 — Write the HTML in chunks.** For emails with 10+ sections, don't build the entire HTML in memory and write it in one giant call. Write the `<!DOCTYPE>` through `</style>` and `<body>` opener first, append 3-4 sections at a time, then close with `</table></body></html>`.

**Rule 4 — Keep prose minimal.** Don't narrate what you're about to code, then code it, then explain what you coded. Just code it. Save commentary for the delivery summary.

**Rule 5 — Write HTML directly, not a generator.** Do not write a Python or Node script that produces the HTML. Write the email HTML by hand using `str_replace` or `bash` append. A generator adds an abstraction layer that introduces its own bugs.

---

## Working directory

`{spec}` is the path the user provides — typically `/mnt/user-data/uploads/{email-name}-spec.json` (web) or `./emails/{email-name}/spec.json` (local). `{outputs}` is `/mnt/user-data/outputs/` (web) or `./emails/{email-name}/` (local). `{plan}` is `{outputs}/render-plan.md`.

---

# Step 1 — Read the inputs

1. The JSON spec at `{spec}`. Confirm `specVersion` starts with `2.` — if not, halt and tell the user the format is incompatible.
2. The JSON format reference — at `{figma-skill-path}/references/json-format.md` — so you know what every field means. Read this once; you'll need it.
3. **Do NOT read `rendering-patterns.md` or `css-bank.md` yet.** Those get looked up on demand during planning.

Expect placeholder values in the spec — Figma-hosted image URLs, `"#"` hrefs, and placeholder alias strings are normal. Render them as-is into their respective attributes; production swaps them downstream. Don't flag or warn about placeholders in the delivery summary.

---

# Step 2 — Classify every section

Walk the `sections` array. For each section, classify by primitive content and responsive behavior. This determines the coding strategy for every row.

| Section type                              | Strategy                                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Single column, no layout change on mobile | Standard 1-col `<table>`, all styles inline                                                              |
| 2+ columns that stack on mobile           | `<th class="block-cell">` columns within a single `<tr>`. Reset `font-weight: normal` and `align="left"` |
| Vertical divider between columns          | `border-left` on the `<th>`, paired with `border-none` class to remove on mobile                         |
| Element visible on desktop only           | `.hide` class on the wrapping element                                                                    |
| Element visible on mobile only            | `.showMob` with inline `display: none` on desktop                                                        |
| Background image with live text           | VML block from `references/vml-background.html`                                                          |

**No `<ul>`, `<ol>`, `<li>`.** Build lists as table rows with a bullet cell and a content cell.

**Column stacking order:** Columns stack in DOM source order on mobile. If the JSON specifies a different mobile order than desktop, reorder accordingly.

---

# Step 3 — Render plan (lock in every HTML decision)

Before writing any HTML, write `{plan}` covering every section. For each section, plan:

1. **Section ID and source structure** — from JSON: outerPadding? background? padding? Which primitives, in what order?
2. **HTML shape** — the outer wrapper choice (no wrapper / single-cell wrapper / nested outerPadding wrapper) and the primitive-by-primitive shape inside.
3. **CSS bank classes used** — every utility class this section needs (`block-cell`, `padR0`, `padB24`, `border-none`, `hide`, `showMob`, etc.). Look these up in `references/css-bank.md` *now* (first time you hit a class you don't know). If a class is missing, create it following the bank's naming conventions and note "NEW" in the plan.
4. **New classes needed** — any class the bank doesn't have. Defining these in the plan keeps the `<style>` assembly step honest.
5. **Annotation transforms** — does this section have `stripBrackets`, `stripColors`, or `recolorMap` matches? List the affected runs.
6. **Responsive line breaks** — text runs containing `\n` that exist because the desktop column is narrow. List each. Plan the parallel-block pattern (NOT `<br class="hideBR">`, which doesn't survive style-strip).
7. **Phone numbers** — list every phone-number run in this section. Plan the `tel:` link wrapper and which CSS class (`.footerPhoneMobile` for footer phones, `.mobilePhoneISI` for ISI phones).
8. **Open questions or approximations** — e.g., "JSON wants 50px top padding on mobile but bank's closest is `.padT48`". Surface in delivery summary.

Lookup discipline: open `references/rendering-patterns.md` for the specific primitive patterns the plan calls out — image, textBlock, button, list, multiColumn, spacer, VML background. Read only those sections, not the whole file.

After all sections are planned, audit the plan:

- Are all utility classes accounted for, including the ones marked NEW?
- Do any two sections share padding+bgcolor patterns that should have been merged at the spec level? (If yes, that's a spec bug — note it and continue.)
- Did annotation transforms catch every scaffolding-color match in the spec?

The render plan is the contract for Step 5. Once it's written, do not deviate.

---

# Step 4 — Setup base template and assemble CSS

1. Read `references/base-template.html` — copy as the starting point for `{outputs}/{email-name}.html`.
2. Replace `PREVIEW TEXT HERE` with `meta.previewText` from the spec.
3. Assemble the `<style>` block:
   - Always include the **base resets** from `references/css-bank.md` — required on every email.
   - Pull each utility class the render plan lists (and only those — no unused classes).
   - Add any NEW classes from the plan, following the bank's naming conventions.
   - Wrap utility classes inside the `@media` block.
   - Place the assembled `<style>` block in `<head>` where the comment marker indicates.
4. Always include the MSO block after `</style>` (see CSS bank for exact code).

**Template rules:**

- **DOCTYPE + namespaces** — HTML 4.01 Transitional with VML namespaces. Never change.
- **Title** — AMPScript `%%=v(@subjectline)=%%`. Do not replace with plain text.
- **Preview text** — replace placeholder text only; don't modify surrounding structure.
- **`class="width360"`** — always include on the 600px container.
- **`bgcolor` on `<body>`** — always both attribute and inline style.

---

# Step 5 — Render mechanically per plan

Walk the `sections` array in order. For each section, execute the plan entry — do not re-decide HTML shape or CSS classes.

**Ground rules** (Section 1 of `references/rendering-patterns.md`):

| Rule                                                  | Why                                                     |
| ----------------------------------------------------- | ------------------------------------------------------- |
| **Tables only — no `<div>` for layout**               | Outlook ignores `display` on divs                       |
| **All CSS inline**                                    | Most clients strip `<style>` blocks                     |
| **No `<p>`, `<strong>`, `<em>`, `<h1>`–`<h6>`**       | Unpredictable rendering — use `<td>` with inline styles |
| **No `<ul>`, `<ol>`, `<li>`**                         | Outlook inconsistency — table-based bullet pattern      |
| **`padding` as 4-value shorthand only**               | Never `padding-top` etc. inline                         |
| **`bgcolor` + `background-color` — always both**      | Outlook ignores CSS-only                                |
| **`width`/`height` as attribute + CSS — always both** | On `<img>` and fixed `<td>`/`<th>`                      |

**Apply annotation transforms inline as you render text:**

Render every text run's `text` value exactly as-is — no grammar edits, smart-quoting, casing changes, or word substitutions. The only allowed transformations are the three annotation rules below:

- **`stripBrackets: true`** — remove `[` and `]` from editorial placeholders; keep the content inside.
- **`stripColors`** — if a text run has a color in this list, drop the override; the run inherits the parent block's color.
- **`recolorMap`** — if a text run's color matches a key, render with the mapped value.

Never let a scaffolding color reach the rendered HTML.

**Section-padding architecture — REQUIRED PATTERN:**

When a section has non-zero padding or a background color, **one outer cell owns the entire section's padding and background.** Inner content rows carry no section-level padding and no background. When a section has `outerPadding`, use two nested wrappers — the outer for spacing, the inner for background + padding.

See `references/rendering-patterns.md`:

- "Section wrapper — standard (single-layer)" — background + padding on one cell
- "Section wrapper — nested" — the `outerPadding` case

The HTML validator flags the forbidden pattern: two or more consecutive content rows sharing identical `padding` left+right values combined with identical `bgcolor` — that's the signature of a section that should have been wrapped.

**Section-level routing:**

- If `skipInProduction: true` — skip entirely, emit nothing.
- If the section has `outerPadding` — render as nested wrappers per the plan.
- If the section has `background` or non-zero `padding` (no `outerPadding`) — wrap nodes in a `<tr><td bgcolor="...">` outer cell with inner `<table width="100%">`.
- If no background and no padding — emit nodes as `<tr>` rows directly in the outer content table.

**Per-primitive HTML** — read the matching section of `references/rendering-patterns.md` for each primitive type the plan uses. The patterns are guides for the correct structure, attributes, and rules — adapt them to the JSON values without breaking the rules (tables only, all CSS inline, no ghost tables, no `<li>`, `<th>` for responsive columns).

**Responsive line breaks** — use the parallel desktop/mobile block pattern from `references/rendering-patterns.md` for every `\n` the plan flagged. Duplicate the text into two `<span>` wrappers: one with the break (shown on desktop, hidden on mobile) and one without (hidden on desktop, shown on mobile). Do NOT use `<br class="hideBR">` — it doesn't survive style-strip.

**Phone numbers** — every phone number gets `<a href="tel:...">` with all formatting stripped from the `tel:` value (digits and country code only):

```
<a href="tel:18006331610" style="color: #000000; text-decoration: none;">1-800-633-1610</a>
```

Apply the planned class (`.footerPhoneMobile` or `.mobilePhoneISI`).

---

# Step 6 — Validate before delivering

Run the validator:

```
python3 scripts/validate-html.py {outputs}/{email-name}.html {spec}
```

Checks: forbidden tags, missing image attributes, missing link attributes, missing `mso-line-height-rule: exactly` on text cells, scaffolding color leakage, VML wrapping on click-tracked elements, individual padding sides used inline.

Fix every error before delivering. **If a validator error traces back to a wrong plan decision, update the plan first, then re-render — don't patch the HTML directly without updating the plan.** Warnings can be surfaced but don't block.

---

# Step 7 — Deliver

Write the final HTML to `{outputs}/{email-name}.html`. Tell the user:

- How many sections rendered and which were skipped
- Validation result
- Any mobile spacing approximations (e.g., JSON asked for 50px top padding but `.padT48` was closest)
- Open questions from `meta.openQuestions` that need resolution before launch (especially `blocking: true` ones)

---

## Checklist (run before delivering)

**Structure:**

- [ ] Render plan written before any HTML
- [ ] Base template from `references/base-template.html`
- [ ] `<style>` block: base resets + only the utility classes the plan listed
- [ ] MSO block included after `</style>`
- [ ] Zero `<div>` for layout
- [ ] Container: 600px with `class="width360"`
- [ ] Every `<table>`: `cellpadding="0" cellspacing="0" border="0" role="presentation"`
- [ ] No margin anywhere
- [ ] Padding only on `<td>` or `<th>`, inline as 4-value shorthand

**CSS:**

- [ ] All styles inline
- [ ] Colors: 6-digit hex with `#`
- [ ] Fonts: web-safe with fallback
- [ ] No unused classes in `<style>`
- [ ] Any NEW classes follow CSS bank naming conventions and are documented in the plan

**Text:**

- [ ] Zero `<p>`, `<h1>`–`<h6>`, `<strong>`, `<em>`
- [ ] Every text `<td>`: `font-family`, `font-size`, `line-height`, `mso-line-height-rule: exactly`, `color`
- [ ] All links: `target="_blank"`, `alias`, `color`, `text-decoration`, `font-family`, `font-size`

**Images:**

- [ ] Every `<img>`: `alt`, `width` attribute, `height` attribute, `style="border: 0; display: block;"`

**Multi-column:**

- [ ] `<th class="block-cell">` for responsive columns, with `font-weight` and `text-align` reset
- [ ] Vertical dividers use `border-left` with `border-none` class for mobile removal
- [ ] No ghost tables (`<!--[if mso]><table>`) for layout

**Lists:**

- [ ] Zero `<ul>`, `<ol>`, `<li>` — table-based bullet pattern only

**Annotations:**

- [ ] No scaffolding colors in rendered output
- [ ] Text rendered exactly as in the spec
- [ ] Placeholder values (`#` hrefs, Figma image URLs, placeholder aliases) rendered as-is
