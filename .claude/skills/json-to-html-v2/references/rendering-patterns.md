# Rendering Patterns

This file has two sections:

1. **Rules** — absolute constraints that apply to every email, every element, every time. Never break these.
2. **Examples** — reference HTML showing how common situations are coded. These are guides — adapt the structure, classes, and values to fit the design, but never violate a rule from Section 1.

---

# Section 1: Rules

These are non-negotiable. If the design seems to require breaking one, the design needs to be solved a different way — the rule doesn't bend.

---

## Structure

- **Tables only for layout.** Never `<div>` for structural layout.
- **Every `<table>` must have:** `cellpadding="0" cellspacing="0" border="0" role="presentation"`. No exceptions.
- **All CSS inline** via `style=""`. Most email clients strip `<style>` blocks — inline styles are the only styles guaranteed to render.
- **Container width: 600px** with `class="width360"` for mobile sizing.

## Forbidden elements

- **No `<ul>`, `<ol>`, `<li>`.** Outlook renders these inconsistently. Build lists as table rows with a bullet cell and a content cell.
- **No `<p>` tags.** Clients add unpredictable default margins. Text goes directly in `<td>` or `<th>`.
- **No `<h1>` through `<h6>`.** Use `font-size` and `font-weight` on `<td>` inline.
- **No `<strong>` or `<em>`.** Use `<span style="font-weight: bold;">` and `<span style="font-style: italic;">`.
- **No `<div>` for layout.** Only allowed in the preview text scaffolding block.

## Forbidden patterns

- **No ghost tables.** Do not use MSO conditional tables (`<!--[if mso]><table>...<![endif]-->`) to create column layouts. MSO conditionals are only for surgical Outlook rendering fixes — never for layout structure.
- **No VML wrapping on click-tracked elements.** Never put an `<a>` inside `<v:rect>` or `<v:roundrect>` — it breaks SFMC click tracking.
- **No `margin` anywhere.** Use `<td>` or `<th>` padding for all spacing.
- **No individual padding sides as inline styles.** Always use 4-value shorthand: `padding: 0px 24px 20px 24px`. Never `padding-top: 20px` etc. inline. (CSS bank classes for mobile overrides may use individual sides — that's fine in the `<style>` block.)

## Required attributes

- **Every `<img>`:** must have `alt`, `width` (HTML attribute), `height` (HTML attribute), and `style="border: 0; display: block;"`.
- **Every `<a>`:** must have `href`, `alias` (unique SFMC tracking name), `target="_blank"`, and inline `color`, `text-decoration`, `font-family`, `font-size`.
- **Every text `<td>`:** must have inline `font-family`, `font-size`, `line-height`, `mso-line-height-rule: exactly`, and `color`.
- **Every `<th>` used as a column:** must have `font-weight: normal` and `align="left"` set explicitly to reset the `<th>` defaults (bold, centered).

## Dual-attribute rules

These exist because Outlook ignores certain CSS properties and only reads the HTML attribute, while other clients do the opposite.

- **Background color:** always set both `bgcolor="..."` attribute AND `background-color` in `style=""`.
- **Width and height on `<img>`:** always set the HTML attributes `width="N"` `height="N"` AND the CSS `width: Npx; height: Npx;` in style.
- **Width and height on fixed-dimension `<td>`:** set both the HTML attribute and inline CSS.
- **Height on spacer/divider `<td>`:** set `height="N"` attribute, `height: Npx` in style, `line-height: Npx` in style, and `font-size: 0` in style. Include `&nbsp;` as cell content.

## Multi-column layout

- **Use `<th>` for responsive columns** within a single `<tr>`. Apply a CSS bank class (e.g., `block-cell`) for mobile stacking behavior. The specific class depends on the design — `block-cell` makes columns go full-width, but columns that should stay at a fixed width or percentage on mobile need a different class or combination from the CSS bank.
- **Vertical dividers between columns:** use `border-left` (or `border-right`) on the `<th>`, paired with a `border-none` class from the CSS bank to remove it on mobile. Do not use dedicated divider tables.
- **Column widths + gap padding must equal the container width** (typically 600px).
- **Gaps between columns:** apply as padding on the `<th>` (padding-right on the first, or padding-left on the second). Use CSS bank classes to adjust or remove the padding on mobile.

## Text

- All text lives directly in `<td>` or `<th>`. Set all typography inline.
- Bold: `<span style="font-weight: bold;">`. Italic: `<span style="font-style: italic;">`.
- Web-safe fonts only: `Arial, Helvetica, sans-serif` / `Georgia, serif` / `Verdana, Geneva, sans-serif`.
- Superscript: `<span style="font-size: Npx; line-height: 0; vertical-align: super;">` — use 60–70% of the parent font-size.

## Buttons

- Buttons use a `<table>` containing a `<td bgcolor>` with an `<a style="display: block;">` inside.
- The `<a>` gets `line-height` equal to the button height for vertical centering.
- Width and height on the `<td>` must be both HTML attributes and inline CSS.
- Never use VML (`<v:rect>`, `<v:roundrect>`) for buttons.

## Lists

- Build each item as a table row with two cells: a narrow cell for the bullet character (`&#x2022;` or a number), and a wide cell for the content.
- The bullet `<span>` controls bullet color independently from text color.
- Indent is controlled by the outer `<td>` padding-left. Spacing between items is controlled by the outer `<td>` padding-top/bottom.

## Images

- `alt=""` only when the image is purely decorative. All meaningful images need descriptive alt text.
- Fluid images: add `max-width: Npx; width: 100%;` to style. Keep `width` and `height` HTML attributes at the natural dimensions.
- Image cells need `font-size: 0; line-height: 0;` to prevent Outlook's phantom gap below block images.

## Spacer rows

- Use `<tr><td>` with `height` attribute, CSS `height`, `font-size: 0`, `line-height: 0`, and `&nbsp;` content.

## Background images

- Requires VML for Outlook. Read `references/vml-background.html` for the full boilerplate.
- Image URL in 3 places: `background` attribute, `url()` in style, `<v:image>` src.
- Inner content in a `<table>` inside the VML block.

## MSO conditionals

- For surgical Outlook rendering fixes only — never for layout.
- Show in Outlook: `<!--[if true]>...<![endif]-->`
- Hide from Outlook: `<!--[if false]><!-->...<!--<![endif]-->`
- Versions: 9=2000, 10=2002, 11=2003, 12=2007, 14=2010, 15=2013, 16=2016+

## CSS utility classes

- All mobile overrides come from `references/css-bank.md`.
- Only include classes actually used in the email's `<style>` block.
- If a design needs a class that doesn't exist, create it following the CSS bank naming conventions.
- Never invent arbitrary class names — follow the bank's patterns.

## CSS property quick reference

| Property | Allowed on | Notes |
|---|---|---|
| `background-color` | `<table>`, `<td>`, `<th>` | 6-digit hex. Also set `bgcolor` attribute. |
| `border` | `<table>`, `<td>`, `<th>` | Shorthand or individual sides. Pair with `border-none` class for mobile removal. |
| `color` | `<td>`, `<th>`, `<span>`, `<a>` | 6-digit hex. Never inherit. |
| `font-family` | `<td>`, `<th>`, `<span>`, `<a>` | Web-safe + fallback. |
| `font-size` | `<td>`, `<th>`, `<span>`, `<a>` | Pixels only. |
| `font-weight` | `<td>`, `<th>`, `<span>`, `<a>` | `bold` or `normal` inline. Never `<strong>`. |
| `font-style` | `<td>`, `<th>`, `<span>`, `<a>` | `italic` inline. Never `<em>`. |
| `height` | `<td>`, `<th>`, `<img>` | Both HTML attribute and inline style. |
| `line-height` | `<td>`, `<th>`, `<span>`, `<a>` | Pair with `mso-line-height-rule: exactly` on `<td>`/`<th>`. |
| `mso-line-height-rule` | `<td>`, `<th>` | Always `exactly`. |
| `padding` | `<td>`, `<th>` only | 4-value shorthand inline. Never individual sides inline. |
| `text-decoration` | `<a>`, `<span>` | `underline` or `none`. |
| `text-transform` | `<td>`, `<th>`, `<span>`, `<a>` | `uppercase`, `lowercase`, `capitalize`. |
| `width` | `<table>`, `<td>`, `<th>`, `<img>` | Pixels. Both attribute and inline on `<img>`. |

---

# Section 2: Examples

These show how the rules are applied in common situations. **They are reference patterns, not exact templates.** The values, class names, column counts, padding, font sizes, and overall structure should be adapted to match the JSON spec and the design. What must NOT change is the rules from Section 1 — every example follows those rules, and so must your adapted version.

---

## Example: Standard content row

A single-column text row with body copy.

```html
<tr>
  <td align="left" valign="top" style="padding: 0px 24px 20px 24px; font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
    Text content goes directly here
  </td>
</tr>
```

**What adapts:** padding values, font-size, line-height, color, alignment — all come from the JSON.

---

## Example: Spacer row

Vertical space between elements.

```html
<tr>
  <td height="20" style="height: 20px; font-size: 0; line-height: 0;">&nbsp;</td>
</tr>
```

**What adapts:** the height value. The `font-size: 0`, `line-height: 0`, and `&nbsp;` are always required.

---

## Example: Fixed image

```html
<tr>
  <td align="left" valign="top" style="padding: 0px 0px 0px 0px; font-size: 0; line-height: 0;">
    <img src="https://cdn.example.com/logo.png" alt="Company logo" width="120" height="40" style="border: 0; display: block; width: 120px; height: 40px;" />
  </td>
</tr>
```

**What adapts:** src, alt, dimensions, padding, alignment. The `border: 0; display: block;` and `font-size: 0; line-height: 0;` on the cell are always required.

---

## Example: Fluid image

```html
<img src="https://cdn.example.com/hero.jpg" alt="Hero description" width="600" height="300" style="border: 0; display: block; max-width: 600px; width: 100%;" />
```

**What adapts:** src, alt, natural dimensions. The `max-width` + `width: 100%` pattern is what makes it fluid.

---

## Example: Clickable image

```html
<a href="https://example.com" alias="hero-link" target="_blank" style="display: block; font-size: 0; line-height: 0; text-decoration: none;">
  <img src="https://cdn.example.com/hero.jpg" alt="Hero description" width="600" height="300" style="border: 0; display: block; max-width: 600px; width: 100%;" />
</a>
```

**What adapts:** href, alias, image src/alt/dimensions. The wrapping `<a>` always needs `display: block` and full link attributes.

---

## Example: Desktop-only element

```html
<table class="hide" cellpadding="0" cellspacing="0" border="0" role="presentation" width="100%">
  <tr>
    <td style="font-size: 0; line-height: 0;">
      <img src="decorative.png" alt="" width="200" height="4" style="border: 0; display: block;" />
    </td>
  </tr>
</table>
```

**What adapts:** any content can go inside — this pattern is about the `class="hide"` wrapper, not the content.

---

## Example: Mobile-only element

```html
<td class="showMob" style="display: none; font-size: 0; max-height: 0; overflow: hidden;">
  Mobile-only content
</td>
```

**What adapts:** the content inside. The inline `display: none` + overflow hiding and `showMob` class are always required together.

---

## Example: Bold and italic text

```html
<!-- WRONG -->
<strong>Bold text</strong>
<em>Italic text</em>

<!-- RIGHT -->
<span style="font-weight: bold;">Bold text</span>
<span style="font-style: italic;">Italic text</span>
```

---

## Example: Responsive line break (different wrapping on desktop vs mobile)

Sometimes a text block (typically a header link or a tagline) needs to break at a specific point on desktop but flow on one line on mobile, or vice versa. Two techniques exist — only one survives clients that strip the `<style>` block.

**Required pattern — parallel desktop / mobile blocks:**

```html
<!-- Desktop version: shown by default, hidden on mobile -->
<span class="hideOnMob">
  <a href="https://example.com/indication" alias="header-read-indication-fpi-desktop" target="_blank" style="color: #0023C8; text-decoration: underline; font-family: Arial, Helvetica, sans-serif; font-size: 16px;">Read Indication and<br />Full Prescribing Information</a>
</span>
<!--[if !mso]><!-->
<span class="showOnMob" style="display: none; mso-hide: all; max-height: 0; overflow: hidden;">
  <a href="https://example.com/indication" alias="header-read-indication-fpi-mobile" target="_blank" style="color: #0023C8; text-decoration: underline; font-family: Arial, Helvetica, sans-serif; font-size: 16px;">Read Indication and Full Prescribing Information</a>
</span>
<!--<![endif]-->
```

With CSS bank classes:
```css
.hideOnMob { display: inline; }
.showOnMob { display: none; mso-hide: all; }

@media screen and (max-width: 480px) {
  .hideOnMob { display: none !important; mso-hide: all !important; max-height: 0 !important; overflow: hidden !important; }
  .showOnMob { display: inline !important; mso-hide: none !important; max-height: none !important; }
}
```

**Why this pattern:** the desktop version renders by inline default (no `<style>` block needed). The mobile version is hidden by inline `display: none` (no `<style>` needed). When the client respects `<style>`, the @media block flips both. When the client strips `<style>`, the safer fallback is "show desktop version" — the user sees the line break but no content is lost. This pattern works in ~98% of email clients including Outlook 2007–2019, Gmail mobile app, Yahoo, Apple Mail, Samsung Mail, and AOL.

**Forbidden pattern — single `<br>` with `display: none`:**

```html
<!-- WRONG: doesn't survive <style>-stripping clients -->
<a href="..." style="...">Read Indication and<br class="hideBR" />Full Prescribing Information</a>
```

This looks cleaner but it relies entirely on the `<style>` block being respected. When stripped, the `<br>` shows on BOTH desktop and mobile — the break can't be removed from a `<br>` without working CSS. Use the parallel-block pattern instead.

**Tracking note:** the two `<a>` elements must have **different** aliases (e.g., `-desktop` and `-mobile`) to pass the JSON spec's unique-alias validation. Both aliases should be registered in SFMC. Each user sees only one render, so click events deduplicate naturally per impression.

---

## Example: Mixed inline content

```html
<td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
  <span style="font-weight: bold;">Term:</span> definition text with a <a href="https://example.com" alias="inline-link" target="_blank" style="color: #0023C8; text-decoration: underline; font-family: Arial, Helvetica, sans-serif; font-size: 16px;">linked phrase</a>.
</td>
```

**What adapts:** the text content, colors, link targets, alias names. The inline link must always carry its own `font-family` and `font-size` because some clients reset link styles.

---

## Example: Bulleted list item

```html
<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
  <tr>
    <td align="left" valign="top" style="padding: 5px 24px 5px 40px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td width="10" align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
            <span style="color: #f48474;">&#x2022;</span>&nbsp;
          </td>
          <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
            List item text goes here
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
```

**What adapts:** bullet color (the `<span>` color), text content, padding/indent values, font size, number of items (repeat the outer table row for each item). For numbered lists, see the next example.

---

## Example: Numbered list item

```html
<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
  <tr>
    <td align="left" valign="top" style="padding: 0px 24px 12px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td width="18" align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
            1.&nbsp;
          </td>
          <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
            First item text goes here
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td align="left" valign="top" style="padding: 0px 24px 12px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td width="18" align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
            2.&nbsp;
          </td>
          <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
            Second item text goes here
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
```

**What adapts:** the number width cell (`width="18"` may need to be wider for double-digit numbers — use `width="24"` for 10+), text content, padding/indent values, font size, spacing between items (controlled by outer `<td>` padding-bottom).

---

## Example: Phone number (tap-to-call)

```html
<td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #000000;">
  You may unsubscribe by <a href="#" alias="footer-unsubscribe" target="_blank" style="color: #0023C8; text-decoration: underline; font-family: Arial, Helvetica, sans-serif; font-size: 16px;">clicking here</a> or calling <a href="tel:18006331610" style="color: #000000; text-decoration: none; font-family: Arial, Helvetica, sans-serif; font-size: 16px;">1-800-633-1610</a>.
</td>
```

**What adapts:** the phone number digits, the surrounding text, the color (match the parent text color so it looks like plain text on desktop). The `tel:` href always strips formatting — digits only with country code, no dashes or parentheses. On mobile, iOS and Android make `tel:` links tappable automatically. Use `.footerPhoneMobile` class for footer phone numbers or `.mobilePhoneISI` for safety section phone numbers (see CSS bank).

---

## Example: Button

```html
<tr>
  <td align="center" valign="top" style="padding: 24px 24px 24px 24px;">
    <table cellpadding="0" cellspacing="0" border="0" role="presentation">
      <tr>
        <td align="center" valign="middle" bgcolor="#0023C8" width="444" height="88" style="background-color: #0023C8; border: 4px solid #80CBFF; width: 444px; height: 88px;">
          <a href="https://example.com" alias="cta-primary" target="_blank" style="display: block; width: 100%; font-family: Arial, Helvetica, sans-serif; font-size: 20px; line-height: 88px; font-weight: bold; color: #FFFFFF; text-decoration: none; text-align: center;">Button Label</a>
        </td>
      </tr>
    </table>
  </td>
</tr>
```

**What adapts:** all colors, dimensions, border style (or no border), font-size, label text, alias, href, padding around the button. The `<a> line-height` always equals the button height. A fluid mobile button adds `class="widthfull"` on the inner table and `max-width` on the `<td>` style. A button without a border just omits the `border` property.

---

## Example: Fixed-height interactive cell (rating box, badge, small button-like link)

A fixed-height cell with a background or border and a single line of centered text. Common in rating scales (1–7 boxes), step indicators, and small action chips. The key technique is **`line-height` equal to the cell's height** for vertical centering — never use padding for this.

```html
<table cellpadding="0" cellspacing="0" border="0" role="presentation">
  <tr>
    <td bgcolor="#FFFFFF" align="center" valign="middle" width="72" height="48" style="background-color: #FFFFFF; border: 1px solid #707070; width: 72px; height: 48px;">
      <a href="#" alias="cxq-rating-1" target="_blank" style="display: block; width: 72px; font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 48px; font-weight: bold; color: #000000; text-decoration: none; text-align: center;">1</a>
    </td>
  </tr>
</table>
```

With CSS bank classes for mobile (smaller cell size):

```css
@media screen and (max-width: 480px) {
  .ratingCell { width: 40px !important; height: 40px !important; }
  .ratingCell a { width: 40px !important; line-height: 40px !important; }
}
```

**The vertical centering rule:** `<a>` `line-height` must equal the cell's `height` exactly. When the cell shrinks on mobile, BOTH the cell height AND the `<a>` line-height must shrink together — otherwise the text drifts toward the top or bottom of the cell.

**Why padding does NOT work for this:** if you use `padding: 10px 0px 10px 0px` to fake centering at desktop (48 − 20 line-height = 28px excess, split 10/10), the SAME padding on a 40px mobile cell gives 40 − 20 − 10 − 10 = 0px of remaining space — text gets pushed to the exact edges with no breathing room. `line-height: <height>` adapts correctly when the height changes; padding does not.

**What adapts:** cell width, cell height, background color, border style (or omit), text color, font size, label text, href, alias. For multiple cells in a row (like a 1-7 rating scale), wrap the whole row in a multiColumn — each cell is one column.

---

## Example: Section wrapper — standard (single-layer)

When a section has `background` and/or non-zero `padding` (but no `outerPadding`), one outer `<td>` owns the section's padding AND background. Inner content rows carry no section-level padding and no background.

**Required pattern:**

```html
<!-- Section with padding 12px 24px 12px 24px and background #E4EEF7 -->
<tr>
  <td bgcolor="#E4EEF7" align="left" valign="top" style="background-color: #E4EEF7; padding: 12px 24px 12px 24px;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
      <tr>
        <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
          First content row — no outer padding, no bgcolor.
        </td>
      </tr>
      <tr>
        <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
          Second content row — no outer padding, no bgcolor.
        </td>
      </tr>
    </table>
  </td>
</tr>
```

**Forbidden pattern (do NOT do this):**

```html
<!-- WRONG: section padding repeated on every inner row -->
<tr>
  <td bgcolor="#E4EEF7" align="left" valign="top" style="background-color: #E4EEF7; padding: 12px 24px 0px 24px; font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
    First content row — padding mixed with content cell.
  </td>
</tr>
<tr>
  <td bgcolor="#E4EEF7" align="left" valign="top" style="background-color: #E4EEF7; padding: 0px 24px 12px 24px; font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
    Second content row — padding mixed with content cell.
  </td>
</tr>
```

The forbidden pattern renders the same as required pattern but is harder to maintain (changing the section's padding requires editing every row) and easier to break (mis-typing one value makes the section uneven). The HTML validator catches this by flagging two or more consecutive content rows in a sibling group sharing identical `padding` left+right values combined with identical `bgcolor`.

**Inner content rows can still have their own vertical padding** (between-row spacing). What they must NOT carry is the section's left/right padding or the section's background color — those belong on the outer wrapper.

**What adapts:** the padding values (any 4-side combination), the bgcolor (or omit if the section has no background), the content rows. For sections with no background AND no padding, skip the wrapper entirely and emit rows directly.

---

## Example: Section wrapper — nested (for sections with `outerPadding`)

When the JSON spec has `outerPadding` on a section, render as two-level nested wrappers: an outer cell with `outerPadding` and NO bgcolor, containing an inner table whose cell has the section's `padding` AND `bgcolor`. This preserves the visual gap between the section edge and the start of the background (which gets lost if both paddings are merged into a single cell).

```html
<!-- Section with outerPadding 12px 0 12px 0 + background #F2F2F2 + padding 24px 24px 24px 24px -->
<tr>
  <td align="left" valign="top" style="padding: 12px 0px 12px 0px;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
      <tr>
        <td bgcolor="#F2F2F2" align="left" valign="top" style="background-color: #F2F2F2; padding: 24px 24px 24px 24px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
            <tr>
              <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
                First content row.
              </td>
            </tr>
            <tr>
              <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 20px; mso-line-height-rule: exactly; color: #414042;">
                Second content row.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </td>
</tr>
```

**When to use this pattern vs the standard single-wrapper:**
- If the section has `background` and `padding` but no `outerPadding` — use the standard single-wrapper pattern from the "Section-padding architecture" rule in SKILL.md Step 7.
- If the section has `outerPadding` (the Figma file used an intermediate container pattern) — use this nested pattern. The outer `<td>` carries the spacing OUTSIDE the colored area; the inner `<td>` carries the background + padding INSIDE.

**Why nesting is correct here:** the `outerPadding` represents whitespace BETWEEN the section edge and where the colored background starts. A flat single wrapper would extend the bgcolor through that whitespace, eliminating the visual gap. Nesting preserves the gap because the outer `<td>` has no bgcolor.

**What adapts:** the outer padding values (any 4-side combination), the bgcolor, the inner padding values, the content rows. All four padding sides on both wrappers come from the JSON (`section.outerPadding` and `section.padding`).

---

## Example: Two-column layout with vertical divider

```html
<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <th class="block-cell padR0 padB24" width="232" align="left" valign="top" style="padding: 0 50px 0 0; font-weight: normal;">
      <a href="" target="_blank" alias="product-logo">
        <img src="" width="232" height="auto" alt="Product logo" style="display: block;" border="0">
      </a>
    </th>
    <th class="block-cell border-none padL0" align="left" valign="middle" style="border-left: 1px solid #2a3c98; padding: 0 0 0 24px; font-weight: normal;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td align="left" valign="top" style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; line-height: 18px; mso-line-height-rule: exactly; color: #414042;">
            Column 2 text content
          </td>
        </tr>
      </table>
    </th>
  </tr>
</table>
```

**What adapts:** number of columns, column widths, content inside each column, whether there's a divider, the CSS bank classes used for mobile behavior. `block-cell` stacks columns full-width on mobile — if a column should stay at a fixed width or percentage on mobile, use a different class or combination from the CSS bank (e.g., `displayBlock` + `width320`). The `border-left` and `border-none` are only needed when the design has a vertical divider. Columns without a divider just use padding for the gap.

---

## Example: Icon + text columns (centering images on mobile stack)

A common pattern: a small image (icon, checkmark, badge) on the left with text on the right, side-by-side on desktop, stacked on mobile. When stacked, the image usually needs to center above the text.

### The problem

Images in email HTML always have `display: block` (to prevent the phantom-space gap Outlook adds below inline images). A block-level element ignores `text-align: center` on its parent — that property only affects inline content. So adding `alignCenter` to the parent `<th>` doesn't center the image on mobile. The image stays left-aligned.

### The fix

Apply `margin: 0 auto` on the **inner `<table>`** that wraps the image — not on the `<img>` itself. The image is the same width as its wrapping `<table>` and `<td>` (all, say, 110px), so centering the image inside a 110px container is invisible. The `<table>` (110px) sitting inside the stacked `<th>` (now 100% width on mobile) is the element with room to center.

```html
<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
  <tr>
    <th class="block-cell padR0 padB24" width="110" align="left" valign="middle" style="padding: 0px 0px 0px 0px; font-weight: normal; text-align: left;">
      <table class="tblCenterMob" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td align="left" valign="middle" style="font-size: 0; line-height: 0;">
            <img src="checkmark.png" alt="Orange checkmark" width="110" height="110" style="border: 0; display: block; width: 110px; height: 110px;" />
          </td>
        </tr>
      </table>
    </th>
    <th class="block-cell padL0Mob alignLeft" align="left" valign="middle" style="padding: 0px 0px 0px 24px; font-weight: normal; text-align: left;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation">
        <tr>
          <td align="left" valign="middle" style="font-family: Arial, Helvetica, sans-serif; font-size: 20px; line-height: 28px; mso-line-height-rule: exactly; font-weight: bold; color: #414042;">
            APPROVED in Stage 2 T1D
          </td>
        </tr>
      </table>
    </th>
  </tr>
</table>
```

With CSS bank class:
```css
@media screen and (max-width: 480px) {
  .tblCenterMob { margin: 0 auto !important; }
}
```

**How it works:**
- On desktop, `.tblCenterMob` does nothing — the `@media` rule only fires ≤480px. The inner `<table>` sits at the left of its 110px-wide `<th>`, which is correct.
- On mobile, `.block-cell` makes the `<th>` go 100% width. The inner `<table>` (still 110px) gets `margin: 0 auto` which centers it in the now-full-width container. The image inside is centered because it fills the table.

**What adapts:** the image src/alt/width/height, the text content, column widths, gap padding. The `tblCenterMob` class goes on any inner `<table>` wrapping an image that should center on mobile stack. Don't put `margin: 0 auto` on the `<img>` directly — it won't work because the image already fills its parent.

**When NOT to use this:** if the design wants the image to stay left-aligned on mobile (some layouts do), omit `tblCenterMob` and keep the default left alignment.

---

## Example: Horizontal colored bar

A thin full-width colored line (brand accent, section divider, etc.).

```html
<tr>
  <td bgcolor="#FF5000" height="4" style="background-color: #FF5000; height: 4px; line-height: 4px; font-size: 0;">&nbsp;</td>
</tr>
```

**What adapts:** the color, the height. The `bgcolor` attribute + CSS `background-color`, `height` attribute + CSS `height`, `line-height` matching the height, `font-size: 0`, and `&nbsp;` are all always required — each prevents a different client from adding unwanted space.

---

## Example: MSO conditional — Outlook-only fix

```html
<!--[if true]>
  <table width="600" cellpadding="0" cellspacing="0" border="0"><tr><td>
<![endif]-->
  Content that needs an Outlook-specific width wrapper
<!--[if true]>
  </td></tr></table>
<![endif]-->
```

**What adapts:** the specific fix inside. This is always a surgical fix for a specific rendering bug — never used for general column layout.

---

## Example: Background image with live text

Read `references/vml-background.html` for the full VML boilerplate. The key points:

- Image URL in 3 places: `background` attribute, `url()` in style, `<v:image>` src
- Height and width in multiple VML attributes
- Live text in a `<table>` inside the VML block with full inline typography

**What adapts:** everything — dimensions, image URL, text content, colors. The VML structure itself is the pattern; the content inside changes per design.
