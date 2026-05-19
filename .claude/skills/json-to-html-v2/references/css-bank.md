# CSS Bank

This is the class library for email HTML. The `json-to-html` skill pulls classes from this bank as needed for each email. Only the classes actually used get included in the email's `<style>` block — no unused CSS ships.

**If a class doesn't exist in this bank, the skill creates it** following the naming conventions and patterns documented here. Any new class created for an email should be added back to this bank for future reuse.

All classes are mobile-only — they live inside the `@media` block and override inline desktop styles on small screens.

---

## How to use this bank

1. While rendering the HTML, collect every utility class referenced on any element.
2. After rendering is complete, assemble the `<style>` block using only the classes that were actually used.
3. If a class was needed but didn't exist in this bank, create it following the naming conventions below and include it in the `<style>` block.
4. Always include the **base resets** section — those are required on every email regardless.

---

## Base resets (always include)

These are not utility classes — they're global resets required for cross-client rendering. Include all of them in every email.

```css
body {
  height: 100% !important;
  margin: 0 auto !important;
  padding: 0 !important;
  width: 100% !important;
  -webkit-text-size-adjust: 100%;
  -ms-text-size-adjust: 100%;
  -webkit-font-smoothing: antialiased;
  mso-hyphenate: none;
}
* {
  -ms-text-size-adjust: 100%;
  -webkit-text-size-adjust: 100%;
  -webkit-font-smoothing: antialiased;
  -moz-text-size-adjust: none;
  -ms-text-size-adjust: none;
  text-size-adjust: none;
}
table, td {
  mso-table-lspace: 0pt !important;
  mso-table-rspace: 0pt !important;
  border-collapse: collapse !important;
}
img {
  -ms-interpolation-mode: bicubic;
}
a {
  color: #5b5b5b;
}
a:visited {
  color: inherit;
}
a[x-apple-data-detectors] {
  color: inherit !important;
  text-decoration: none !important;
  font-size: inherit !important;
  font-family: inherit !important;
  font-weight: inherit !important;
  line-height: inherit !important;
}
.x-gmail-data-detectors, .x-gmail-data-detectors *, .aBn {
  border-bottom: 0 !important;
  cursor: default !important;
  color: inherit !important;
  text-decoration: none !important;
  font-size: inherit !important;
  font-family: inherit !important;
  font-weight: inherit !important;
  line-height: inherit !important;
}
```

---

## MSO block (always include after closing `</style>`)

```html
<!--[if gte mso 9]><xml>
<o:OfficeDocumentSettings>
<o:AllowPNG/>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml><![endif]-->
<!--[if (gte mso 9)|(IE)]>
<style>
sup {font-size:100% !important;}
</style>
<![endif]-->
```

---

## Mobile utility classes

Everything below lives inside:
```css
@media screen and (max-width: 480px), only screen and (max-device-width: 480px) {
  /* classes here */
}
```

**Exception: `.hideOnMob` and `.showOnMob` need desktop defaults OUTSIDE the @media block.** These classes use a show/hide swap pattern that requires both a desktop rule and a mobile rule to work correctly. Place these in the `<style>` block before the `@media` block:

```css
/* Desktop defaults — place BEFORE the @media block */
.hideOnMob { display: inline; }
.showOnMob { display: none; mso-hide: all; max-height: 0; overflow: hidden; }
```

Without the desktop defaults, the mobile `<span>` has no inline hiding and will show on both breakpoints in clients that respect `<style>` but don't support `@media`.

---

### Layout & stacking

| Class | CSS | Notes |
|---|---|---|
| `.block-cell` | `display: block !important; max-width: 100% !important; width: 100% !important;` | Applied to `<th>` elements for responsive column stacking. Preferred over `.drop` on `<td>` because `display: block` works on `<th>` in Outlook iOS quirks mode where it fails on `<td>`. |
| `.drop` | `display: block !important;` | Stacks inline-block `<table>` elements on mobile. Use on inner `<table>` columns. |
| `.boxSizing` | `max-width: 100% !important; box-sizing: border-box !important;` | |

### Show / hide

| Class | CSS | Notes |
|---|---|---|
| `.showMob` | `display: block !important; font-size: 100% !important; max-height: none !important; height: auto !important; width: 100% !important; margin: 0 !important;` | Reveals mobile-only content. Must pair with inline `display: none; font-size: 0; max-height: 0; overflow: hidden;` on desktop. |
| `.hide` | `visibility: hidden !important; display: none !important; width: 0px !important; font-size: 0px !important; line-height: 0px !important; max-height: 0px !important; overflow: hidden !important;` | Hides desktop-only content on mobile. |
| `.hideOnMob` | `display: none !important; mso-hide: all !important; max-height: 0 !important; overflow: hidden !important;` | Hides INLINE content on mobile (use on `<span>` wrapping desktop-only inline elements, e.g. the desktop variant of a responsive line-break pair). Pair with inline `display: inline;` on desktop. |
| `.showOnMob` | `display: inline !important; mso-hide: none !important; max-height: none !important;` | Reveals INLINE content on mobile (use on `<span>` wrapping mobile-only inline elements). Pair with inline `display: none; mso-hide: all; max-height: 0; overflow: hidden;` on desktop. |

Use `.hideOnMob` / `.showOnMob` for inline content (spans inside a sentence — e.g., the responsive line-break pattern in `.claude/skills/json-to-html-v2/references/rendering-patterns.md`). Use `.hide` / `.showMob` for block content (entire rows, images, tables). Don't mix them — block classes use `display: block` which corrupts inline flow.

### Width

| Class | CSS |
|---|---|
| `.widthfull` | `width: 100% !important;` |
| `.widthhalf` | `width: 50% !important;` |
| `.width25` | `width: 25% !important;` |
| `.width40` | `width: 40% !important;` |
| `.width80` | `width: 80% !important;` |
| `.width64` | `width: 64px !important;` |
| `.width76` | `width: 76px !important;` |
| `.width112` | `width: 112px !important;` |
| `.width320` | `width: 320px !important;` |
| `.width360` | `width: 360px !important;` |
| `.maxwidth75` | `max-width: 75% !important;` |
| `.maxwidth100` | `max-width: 100% !important;` |
| `.bgwidthfull` | `width: 100% !important; background-size: 100% 100% !important;` |

**Naming convention for new width classes:** `.width{N}` for pixel values, `.width{N}pct` for non-standard percentages. Examples: `.width200` → `width: 200px !important;`, `.width33pct` → `width: 33% !important;`

### Padding — Top

| Class | CSS |
|---|---|
| `.padT0` | `padding-top: 0px !important;` |
| `.padT2` | `padding-top: 2px !important;` |
| `.padT4` | `padding-top: 4px !important;` |
| `.padT5` | `padding-top: 5px !important;` |
| `.padT8` | `padding-top: 8px !important;` |
| `.padT10` | `padding-top: 10px !important;` |
| `.padT12` | `padding-top: 12px !important;` |
| `.padT14` | `padding-top: 14px !important;` |
| `.padT15` | `padding-top: 15px !important;` |
| `.padT16` | `padding-top: 16px !important;` |
| `.padT20` | `padding-top: 20px !important;` |
| `.padT24` | `padding-top: 24px !important;` |
| `.padT30` | `padding-top: 30px !important;` |
| `.padT40` | `padding-top: 40px !important;` |
| `.padT50` | `padding-top: 50px !important;` |

### Padding — Bottom

| Class | CSS |
|---|---|
| `.padB0` | `padding-bottom: 0px !important;` |
| `.padB2` | `padding-bottom: 2px !important;` |
| `.padB4` | `padding-bottom: 4px !important;` |
| `.padB5` | `padding-bottom: 5px !important;` |
| `.padB8` | `padding-bottom: 8px !important;` |
| `.padB10` | `padding-bottom: 10px !important;` |
| `.padB12` | `padding-bottom: 12px !important;` |
| `.padB14` | `padding-bottom: 14px !important;` |
| `.padB15` | `padding-bottom: 15px !important;` |
| `.padB16` | `padding-bottom: 16px !important;` |
| `.padB20` | `padding-bottom: 20px !important;` |
| `.padB24` | `padding-bottom: 24px !important;` |
| `.padB30` | `padding-bottom: 30px !important;` |
| `.padB40` | `padding-bottom: 40px !important;` |
| `.padB50` | `padding-bottom: 50px !important;` |

### Padding — Left

| Class | CSS |
|---|---|
| `.padL0` | `padding-left: 0px !important;` |
| `.padL2` | `padding-left: 2px !important;` |
| `.padL4` | `padding-left: 4px !important;` |
| `.padL5` | `padding-left: 5px !important;` |
| `.padL8` | `padding-left: 8px !important;` |
| `.padL10` | `padding-left: 10px !important;` |
| `.padL12` | `padding-left: 12px !important;` |
| `.padL14` | `padding-left: 14px !important;` |
| `.padL15` | `padding-left: 15px !important;` |
| `.padL16` | `padding-left: 16px !important;` |
| `.padL20` | `padding-left: 20px !important;` |
| `.padL24` | `padding-left: 24px !important;` |
| `.padL30` | `padding-left: 30px !important;` |
| `.padL40` | `padding-left: 40px !important;` |
| `.padL50` | `padding-left: 50px !important;` |

### Padding — Right

| Class | CSS |
|---|---|
| `.padR0` | `padding-right: 0px !important;` |
| `.padR2` | `padding-right: 2px !important;` |
| `.padR4` | `padding-right: 4px !important;` |
| `.padR5` | `padding-right: 5px !important;` |
| `.padR8` | `padding-right: 8px !important;` |
| `.padR10` | `padding-right: 10px !important;` |
| `.padR12` | `padding-right: 12px !important;` |
| `.padR14` | `padding-right: 14px !important;` |
| `.padR15` | `padding-right: 15px !important;` |
| `.padR16` | `padding-right: 16px !important;` |
| `.padR20` | `padding-right: 20px !important;` |
| `.padR24` | `padding-right: 24px !important;` |
| `.padR30` | `padding-right: 30px !important;` |
| `.padR40` | `padding-right: 40px !important;` |
| `.padR50` | `padding-right: 50px !important;` |

**Naming convention for new padding classes:** `.pad{T|B|L|R}{N}` where N is the pixel value. Example: `.padT36` → `padding-top: 36px !important;`

### Font size

| Class | CSS |
|---|---|
| `.font10` | `font-size: 10px !important; line-height: 14px !important;` |
| `.font11` | `font-size: 11px !important; line-height: 15px !important;` |
| `.font12` | `font-size: 12px !important; line-height: 16px !important;` |
| `.font13` | `font-size: 13px !important; line-height: 17px !important;` |
| `.font14` | `font-size: 14px !important; line-height: 18px !important;` |
| `.font15` | `font-size: 15px !important; line-height: 19px !important;` |
| `.font16` | `font-size: 16px !important; line-height: 20px !important;` |
| `.font18` | `font-size: 18px !important; line-height: 22px !important;` |
| `.font20` | `font-size: 20px !important; line-height: 24px !important;` |
| `.font22` | `font-size: 22px !important; line-height: 26px !important;` |
| `.font24` | `font-size: 24px !important; line-height: 28px !important;` |
| `.font26` | `font-size: 26px !important; line-height: 30px !important;` |
| `.font28` | `font-size: 28px !important; line-height: 32px !important;` |
| `.font30` | `font-size: 30px !important; line-height: 34px !important;` |

**Naming convention:** `.font{N}` — font-size is N, line-height is N+4.

### Text alignment

| Class | CSS |
|---|---|
| `.alignCenter` | `text-align: center !important; align-content: center !important; align-items: center !important;` |
| `.alignLeft` | `text-align: left !important;` |
| `.alignRight` | `text-align: right !important;` |

### Block-element centering / alignment

| Class | CSS | Notes |
|---|---|---|
| `.tblCenterMob` | `margin: 0 auto !important;` | Centers a fixed-width `<table>` inside a full-width parent on mobile. Use on the inner `<table>` wrapping an image in a stacked multiColumn. Do NOT use `alignCenter` for this — `text-align: center` doesn't work on `display: block` images. See the "Icon + text columns" example in `rendering-patterns.md`. |
| `.tblLeftMob` | `margin-right: auto !important; margin-left: 0 !important;` | Left-aligns a fixed-width `<table>` inside a full-width parent on mobile. Use when the image column should stay left-aligned after stacking (e.g. a small logo above a text block). |
| `.tblRightMob` | `margin-left: auto !important; margin-right: 0 !important;` | Right-aligns a fixed-width `<table>` inside a full-width parent on mobile. |

**`alignCenter`/`alignLeft`/`alignRight` vs `tblCenterMob`/`tblLeftMob`/`tblRightMob` — when to use which:**
- `align*` → positions **text** (inline content) inside a `<td>` or `<th>`. Works because `text-align` affects inline elements.
- `tbl*Mob` → positions a **block element** (a `<table>` wrapping an image) inside its parent. Works because `margin` auto/0 controls block-level positioning. Use this whenever a stacked multiColumn has an image column that needs specific alignment on mobile.

### Border

| Class | CSS | Notes |
|---|---|---|
| `.border-none` | `border: none !important;` | Removes a `border-left`, `border-right`, etc. that was set inline for desktop. Used to hide vertical dividers when columns stack on mobile. |
| `.border-top-none` | `border-top: none !important;` | |
| `.border-bottom-none` | `border-bottom: none !important;` | |
| `.border-left-none` | `border-left: none !important;` | |
| `.border-right-none` | `border-right: none !important;` | |

### Height

| Class | CSS |
|---|---|
| `.heightAuto` | `height: auto !important;` |
| `.height0` | `height: 0px !important; font-size: 0px !important; line-height: 0px !important;` |

**Naming convention:** `.height{N}` → `height: Npx !important;`

### Display

| Class | CSS |
|---|---|
| `.displayNone` | `display: none !important;` |
| `.displayBlock` | `display: block !important;` |
| `.displayInline` | `display: inline !important;` |
| `.displayInlineBlock` | `display: inline-block !important;` |

### Special

| Class | CSS | Notes |
|---|---|---|
| `.mobilePhoneISI` | `display: inline !important; font-family: Arial, Helvetica, sans-serif !important; font-weight: normal !important; visibility: visible !important;` | For phone numbers in safety information sections that should be clickable on mobile. |
| `.footerPhoneMobile` | `display: inline !important; font-family: Arial, Helvetica, sans-serif !important; white-space: nowrap !important; font-weight: normal !important; visibility: visible !important;` | For footer phone numbers on mobile. |

---

## Creating new classes

When the JSON spec requires a mobile override that doesn't match any existing class, create one following these conventions:

**Padding:** `.pad{T|B|L|R}{value}` → `padding-{side}: {value}px !important;`
**Width pixel:** `.width{value}` → `width: {value}px !important;`
**Width percent:** `.width{value}pct` → `width: {value}% !important;`
**Font size:** `.font{value}` → `font-size: {value}px !important; line-height: {value+4}px !important;`
**Height:** `.height{value}` → `height: {value}px !important;`
**Max-width pixel:** `.maxwidth{value}` → `max-width: {value}px !important;`
**Max-width percent:** `.maxwidth{value}pct` → `max-width: {value}% !important;`

For anything outside these patterns, use a descriptive camelCase name that clearly states what it does. Example: `.imgFluid` → `width: 100% !important; height: auto !important;`

**Every custom class must use `!important`** — mobile overrides must beat inline desktop styles.
