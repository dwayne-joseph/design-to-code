# PLAN — tzield-now-approved-day1-crm

## Email
- Figma file: uVU9ZnWB6iZO0kgY4bztS9
- Frames: desktop 40000030:420 (620×4202, 600px content) / mobile 40000030:440 (360×5787)
- 14 sections, paired 1:1 by DOM order
- Subject (from section 1): "Explore a[n] [new] indication for a T1D treatment option."
- Preview text (from section 2): "Learn about this treatment option for your patients."

### Sections (desktop / mobile / working name)
1. 40000030:421 / 40000030:441 — Email Envelope Metadata (SKIP - editorial)
2. 40000030:422 / 40000030:442 — Preheader Label (SKIP - editorial, captured in meta.previewText)
3. 40000030:423 / 40000030:443 — Top Nav Links (View in browser | Contact a Rep | Unsubscribe)
4. 40000030:424 / 40000030:444 — Header (Sanofi + Tzield logos, PI links, INDICATIONS, bullet list)
5. 40000030:425 / 40000030:445 — NEW INDICATION Banner (dark teal)
6. 40000030:426 / 40000030:446 — Approval Announcement (blue background)
7. 40000030:427 / 40000030:447 — Hero Image (girl in park)
8. 40000030:428 / 40000030:448 — Stages Continuum Headline + 2 Checkmark Rows
9. 40000030:429 / 40000030:449 — Abbreviation Footnote (T1D=type 1 diabetes.)
10. 40000030:430 / 40000030:450 — Learn More + Discover More Button (light blue bg)
11. 40000030:431 / 40000030:451 — ISI Module (WARNINGS, AR, USE IN SPECIFIC POPULATIONS, links)
12. 40000030:432 / 40000030:452 — References (numbered list)
13. 40000030:433 / 40000030:453 — Survey/CXQ (7-point rating scale)
14. 40000030:434 / 40000030:457 — Footer (Sanofi address, legal, MAT code)

### Canvas-level siblings
- **40000030:438 / 40000030:458** — `RIGHT Decorative Lines` (coral 8px + blue 16px bars) overlaying hero section's right edge. APPLY OVERLAY RULE → bake into hero image asset before launch (blocking).
- **40000030:435 / 40000030:454** — `[ ]` bracket frame overlaying survey section (section 13) left+right edges. APPLY OVERLAY RULE → bake into survey rendering or treat as decorative (blocking).

### Repeated assets
- Sanofi corporate logo: section 4 (60×16, top right of header) and section 14 (88×24, in footer). Different sizes; different asset URLs.
- TZIELD brand logo: section 4 only (214×90).
- Orange checkmark icon: section 8 (110×110, used twice).

### Scaffolding colors
- `#FF00B7` (Variable token) — main scaffolding marker, used throughout for placeholder brackets, dynamic content markers, and the MAT job code.
- `#FF25DB` (Static/text-dynamic-annotate token) — declared but not used in this design.

### Annotations
- `stripBrackets: true` — all `[ ]` characters are scaffolding markers around dynamic content. Strip them globally.
- `stripColors: ["#FF00B7"]` — drop scaffolding color, inherit parent block color.
- `recolorMap: {}` — empty (color drop handles all cases).

### Email-level open questions (blocking before launch)
1. **hero-overlay-bake**: Bake coral 8px + cyan/blue 16px decorative bars into hero image asset (right edge). Email HTML cannot render absolute overlays.
2. **section-13-bracket-overlay**: Decorative `[ ]` bracket frame overlays the survey section's left and right edges. Decide whether to bake into the survey design or omit.
3. **sanofi-logo-alt**: Provide alt text "Sanofi" for the corporate logo (sections 4 and 14).
4. **tzield-logo-alt**: Provide alt text for TZIELD® brand logo with subtext "(teplizumab-mzwv) Injection | 2mg/2mL" (section 4).
5. **hero-alt**: Provide alt text for the hero image (decorative? or descriptive — young girl in park).

---

## Sections

### section-1 — Email Envelope Metadata (skip)
Nodes: 40000030:421 / 40000030:441 (600×104 / 360×144)
- Entire block in scaffolding pink #FF00B7 — From/To/Date/Subject editorial display.
- Decision: `skipInProduction: true`. Subject content captured in `meta.subjectLine`.

### section-2 — Preheader Label (skip)
Nodes: 40000030:422 / 40000030:442 (600×44 / 360×64)
- "Preheader: [Learn about this treatment option for your patients.]" — editorial display.
- Decision: `skipInProduction: true`. Content captured in `meta.previewText`.

### section-3 — Top Nav Links
Nodes: 40000030:423 / 40000030:443 (600×64 / 360×64)
- Background: #E4EEF7. Padding 12px top/bottom, 24px left/right.
- Single textBlock: "View in browser | Contact a Rep | Unsubscribe" — three blue underlined links separated by gray "|" dividers.
- Color #0023C8 base, "|" runs in #414042.
- Mobile: same layout, may wrap differently.

### section-4 — Header
Nodes: 40000030:424 / 40000030:444 (600×469 / 360×729)
- Structural pattern: single-layer (root has padding only, no bg). Padding: top 14px, bottom 12px, 0 horizontal.
- Sub-sequence:
  1. **Sanofi logo** (image, 60×16) — right-aligned, with pb-14, pr-10
  2. **Coral separator bar** (full width, 4px, #FF5000) — spacer with bg
  3. **Two-column row** (24px padding container, then 50px gap inner):
     - Left: Tzield logo image (214×90)
     - Right: vertical blue line (rotated stroke) + link text block (201px wide)
     - Mobile stacks (flex-col, 50px gap)
  4. **INDICATIONS** heading (#0023C8 bold 19px, line-height 23, with pb-24)
  5. **Indication body** — text block + bullet list
- Decisions:
  - Sanofi top logo and tzield logo each become `image` primitives (or sit inside multiColumn).
  - The coral bar is a `spacer` with background.
  - Two-column header row → `multiColumn` with `borderLeft` on text column (the rotated stroke), `hideOnMobile: true` for the border.
  - Bullet list → `list` primitive.

### section-5 — NEW INDICATION Banner
Nodes: 40000030:425 / 40000030:445 (600×92 / 360×126)
- Background: #06537B (Text_SubHeader). Padding 12px/24px.
- Single bold textBlock (30px, line-height normal): "[NEW INDICATION] FOR APPROPRIATE PATIENTS¹"
- Base color #E4EEF7 (light blue, on dark bg). Brackets `[` and `]` in scaffolding pink (#FF00B7).
- Superscript "1" at 19.35px.
- After stripping: "NEW INDICATION FOR APPROPRIATE PATIENTS¹"

### section-6 — Approval Announcement
Nodes: 40000030:426 / 40000030:446 (600×139 / 360×208)
- Background: #0023C8. Padding 12px/24px.
- Single regular textBlock (19px, line-height 23, color white).
- Text: "Due to the significant unmet need in T1D and years of clinical research, TZIELD has been approved for patients with Stage 3 T1D within [6-12 weeks] of diagnosis as the first therapy under the FDA's Commissioner National Priority Voucher (CNPV) program.²"
- "[" and "]" around "6-12 weeks" in scaffolding pink. Superscript "2" at 12.255px.

### section-7 — Hero Image
Nodes: 40000030:427 / 40000030:447 (600×324 / 360×312)
- Padding 12px top/bottom only.
- Single `image`: 600×300 desktop. Mobile uses different asset URL, 360×288. mobile.preserveWidth=false (fluid hero).
- **Open question** (blocking): bake decorative bars (coral 8px + blue 16px) from canvas sibling 40000030:438/458 into the hero image asset.

### section-8 — Stages Continuum + Checkmarks
Nodes: 40000030:428 / 40000030:448 (600×490 / 360×718)
- Padding 12px top/bottom (no horizontal padding on the section).
- Inner gap 24px between elements.
- Sub-sequence:
  1. Heading textBlock (#0023C8 bold 30px, line-height 34): "TZIELD has expanded across the following stages of the T1D disease continuum¹" with superscript 1
     - Wrapped in container with 24px horizontal padding
  2. Row 1 (multiColumn, container 24px padding): orange checkmark (110×110) + 24px gap + "APPROVED in Stage 2 T1D" (bold 20px, line-height 28, body color #414042)
  3. Row 2 (multiColumn, container 24px padding): orange checkmark (110×110) + 24px gap + "[NOW] APPROVED in Stage 3 T1D within [6-12 weeks] of diagnosis"
- Mobile: checkmark rows stack (image above text)

### section-9 — Abbreviation Footnote
Nodes: 40000030:429 / 40000030:449 (600×47 / 360×47)
- Padding 12px/24px. White bg (default).
- Single textBlock: "T1D=type 1 diabetes." (regular 19px, line-height 23, body color #414042)

### section-10 — Learn More + Discover Button
Nodes: 40000030:430 / 40000030:450 (600×159 / 360×192)
- Background #E4EEF7. Padding 12px/24px. Inner gap 24px.
- Sub-sequence:
  1. textBlock centered: "Learn more about the [new] indication" (regular 19px, line-height 23, black)
     - "[new]" in scaffolding pink
  2. button "Discover More":
     - Desktop: 444×88, blue #0023C8 bg, border 4px #80CBFF
     - Mobile: 204×98 (different height) — set mobile.width=204, mobile.height=98
     - Bold 20px white, line-height 24

### section-11 — ISI Module
Nodes: 40000030:431 / 40000030:451 (600×1295 / 360×2042)
- Padding 12px/24px. Default white bg. Inner gap 24px between blocks.
- Sub-sequence (each item is a block, separated by 24px gap):
  1. "IMPORTANT SAFETY INFORMATION" heading (#0023C8 bold 19px, line-height 23)
  2. "WARNINGS AND PRECAUTIONS" subheading (bold 16px, line-height 20, body color)
  3. Bulleted list with 6 items (Cytokine Release Syndrome (CRS), Serious Infections, Lymphopenia, Hypersensitivity Reactions, Vaccinations, Glucose Monitoring in Patients...) — each item starts with a bold label term. Vaccinations item has multi-line content with inline line breaks.
  4. "ADVERSE REACTIONS" subheading (bold 16px)
  5. Body paragraph: "Most common adverse reactions (>10%) were lymphopenia, rash, leukopenia, neutropenia, increased liver transaminase, and headache."
  6. "USE IN SPECIFIC POPULATIONS" subheading (bold 16px)
  7. Bulleted list (Pregnancy, Lactation)
  8. textBlock: "Please see full [Prescribing Information](#), including patient selection criteria."
  9. textBlock: "[Click here](#) to learn more about Sanofi's commitment to fighting counterfeit drugs."
- Mobile delta: same content; on desktop the last two paragraphs are joined in one block, on mobile they're split. I'll keep them as two separate blocks to match mobile (also matches the section count).

### section-12 — References
Nodes: 40000030:432 / 40000030:452 (600×120 / 360×140)
- Padding 12px/24px. Inner gap 24px.
- Sub-sequence:
  1. "References:" heading (bold 16px)
  2. Numbered list (2 items):
     - "TZIELD Prescribing Information. Provention Bio, Inc; [2025.]" (item spacing 12px after)
     - "[Press release pending]" (entirely scaffolding)

### section-13 — Survey (CXQ)
Nodes: 40000030:433 / 40000030:453 (600×234 / 360×288)
- Structural pattern: intermediate container. Section frame has 12px top/bottom padding. Inner container has #F2F2F2 bg + 24px padding.
- `outerPadding: {top: 12, right: 0, bottom: 12, left: 0}`, `padding: {24 on all sides}`, `background: #F2F2F2`.
- Inner gap 10px between rows.
- Sub-sequence:
  1. Intro textBlock (regular 16px center, body color): "Your feedback is important to us. To help us improve our offering, you are invited to respond to the question below and complete a short survey."
  2. Question textBlock (bold 19px center, line-height 22, black): "How relevant is the content of this email to you?"
  3. multiColumn (justify-between): "Not relevant" / "Very relevant" labels (bold 19px black). Two columns.
  4. multiColumn with 7 rating boxes (justify-between, mobileLayout=preserve since they must stay horizontal on mobile)
     - Desktop: each box 72×48, #FFFFFF bg with 1px #707070 border
     - Mobile: each box 40×40 (mobile.width=40, mobile.height=40)
     - Box #2 is highlighted: bg #979797, text white #FFFFFF, border #979797
     - Each box has a link (alias cxq-rating-1 through cxq-rating-7, href "#")
     - line-height equal to height for vertical centering
- Mobile delta: question text has explicit line break in mobile ("How relevant is the content of this / email to you?"). I'll keep desktop single-line and let mobile wrap naturally.
- **Open question** (blocking): decorative `[ ]` bracket frame canvas sibling overlays this section's left and right edges.

### section-14 — Footer
Nodes: 40000030:434 / 40000030:457 (600×471 / 360×573)
- Padding 12px/24px. White bg.
- Sub-sequence (no explicit gap between, each block has own padding):
  1. textBlock: "Prescribers and other Healthcare Professionals may [click here](#) for State Price Disclosure Information."
  2. textBlock (pt-16): bold "Please do not reply to this message." + " Sanofi US will not receive a message if you reply."
  3. Sanofi logo (image, 88×24, pt-16 pb-14)
  4. textBlock (pb-16): "Sanofi US / 100 Morris Street, / Morristown, NJ 07960" (3 lines)
  5. textBlock: "© 2026 Sanofi. All rights reserved." + blank line + "[Legal Disclaimer](#) and [Privacy Policy](#)" + blank + "Questions and Comments? [Click here](#) to contact us." + blank + "This email is intended for use by US residents only." + blank + "You may unsubscribe from Sanofi by [clicking here](#) or calling 1-800-633-1610."
  6. textBlock (pt-16, scaffolding pink, body color after strip): "MAT-US-2510989-v1.0-10/2025"

---

## Link aliases (must be unique)
- section-3: nav-view-in-browser, nav-contact-a-rep, nav-unsubscribe
- section-4: header-read-indication, header-read-pi, header-pi-link, header-warning-link
- section-10: cta-discover-more
- section-11: isi-prescribing-info, isi-counterfeit
- section-13: cxq-rating-1 through cxq-rating-7
- section-14: footer-state-price, footer-legal-disclaimer, footer-privacy-policy, footer-questions-comments, footer-unsubscribe
