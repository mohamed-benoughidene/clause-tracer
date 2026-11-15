# Clause Tracer — Design system

This file documents the visual system that the prototype uses today. It covers the tokens, the components, the patterns and the rules behind them. The source of truth is `prototype/styles.css`. The reasons for each choice are in `spec.md` (section 14.4), `design-direction.md`, ADRs 0001–0003 and the brand file. The words are in `ux-copy.md`.

Each section says what the system is, then what the prototype does differently. Section 8 lists those differences in one place, so they can be fixed before coding starts.

**Contents**

1. Principles
2. Brand and logo
3. Tokens: colour, type, space, shape, depth, motion
4. Icons
5. Components
6. Patterns
7. Accessibility
8. Audit: where the prototype drifts
9. Using the prototype

---

## 1. Principles

These are the rules everything else follows. The Source column names the decision behind each.

| # | Rule | Source |
| --- | --- | --- |
| 1 | **The careful friend.** The contract fills the screen, and the app speaks through notes in the margin, in plain words. It feels calm and personal, not like a dashboard. | Design direction, principle 1 |
| 2 | **Paper and ink.** The app chrome is cool grey. Warm paper appears only on the contract sheet. Text and the primary button are ink. | Principle 5 |
| 3 | **Red means one thing.** Oxblood `#A91207` means walk-away: "a line you won't cross". The logo's line also uses it. One brand use remains: on first launch the words “the exact words” carry an oxblood underline, the logo's line. Nothing else uses red, not even errors or warnings. | ADR 0003 and its amendment of 15 Nov 2026 |
| 4 | **Labels are stamps.** Labels have square corners, a solid colour block with an icon, and the word in small capitals. They never look like the rounded tags or the status gauges. | ADR 0002 |
| 5 | **Never colour alone.** Every label has a colour, an icon and a word, and every view must pass a greyscale check. | Spec 14.4 |
| 6 | **Inked or pencilled.** A label from a clear rule match is inked (solid). A label the app judged from the wording is pencilled (dashed). | Design direction, action 2 |
| 7 | **Two radii, one shadow.** The radii are 4 px and 8 px. Only the contract sheet casts a shadow in the page, and the first-launch card, which is a sheet of paper and uses the same shadow. Floating layers (dialogs, menus) are the exception. | Principle 6 |
| 8 | **Group by space, then tone, then border.** A group sits on a slightly darker warm tone, with no border. | Principle 7 |
| 9 | **Two voices.** IBM Plex Sans is used for the interface. IBM Plex Serif is used for headings, the friend's notes (in italic) and quotes from the contract. Typeset contract pages use Liberation Serif, the look of the document itself. | Principle 4 |
| 10 | **Real content in every state.** Empty, error and loading states use real words and real numbers. There are no spinners and no fake delays; the reading log shows the actual work. In the prototype the Load file bar and the running play-through only stand in for real progress. | Principle 8 |
| 11 | **Nothing machine-made.** Every element carries meaning. No effect is used for its own sake, and nothing borrows the look of other AI tools. Section 4.1 lists what is never used. | Owner, 14 Nov 2026; `ux-copy.md` section 1.1 |
| 12 | **One thing at a time.** The review shows the contract and one column. The column shows the list or one label's detail, never both, and nothing covers the contract. | Owner, 14 Nov 2026 |

## 2. Brand and logo

The full reference is `docs/clause-tracer-logo-guide.pdf` and `docs/clause-tracer-brand-philosophy.md`. This section covers only what the interface needs.

**The mark.** The mark is one drawn butterfly beside the name, set in IBM Plex Serif SemiBold. It is a single unbroken oxblood line with four eyespots, and only one of the eyespots is red. The butterfly on its own is the app icon and the favicon.

**Brand colours.**

| Name | Hex | Used for | App token |
| --- | --- | --- | --- |
| Oxblood | `#A91207` | The line and the eyespot that matters | `--red`, `--walk` |
| Ink | `#1F2328` | The name and the other eyespots | `--text`, `--action` |
| Paper | `#FBF8F2` | Light background | `--bg-paper` |
| Dark | `#1E1D1A` | Dark background | *(no exact token; see 8.2)* |
| Light | `#ECE8E1` | The name and eyespots on dark | *(no exact token; see 8.2)* |

**Construction.**

- The butterfly is 1.6 × the cap height, centred halfway up the capitals.
- The gap between the butterfly and the C is 0.45 × the cap height, measured from the ink.
- Keep one cap height of clear space on every side.
- Minimum sizes: the logo 120 px (30 mm) wide; the butterfly alone 16 px (5 mm).

**In the prototype.**

- The sidebar shows the logo at 140 px wide. First launch shows it at 190 px, on the paper card.
- `.logo .on-light` and `.logo .on-dark` swap between `logo.svg` and `logo-dark.svg` when the theme changes.
- The master files are in `assets/`.

**Don't:**

- recolour the name red;
- move the butterfly between the words or after the name;
- outline it, or give it a shadow;
- redraw the line or add a fifth eyespot;
- repeat the mark as a pattern.

**Imagery.** The only picture is the First launch hero (`prototype/hero-butterflies.webp`). It fills the whole first-launch window, and one paper card lies on it (section 6, “First launch”). It looks hand-made, has one red thing in it and no text. Dark mode dims it with `brightness(.82)`.

**The underline as the logo's line.** The logo is one unbroken oxblood line. On first launch the words “the exact words” are underlined in that oxblood (`.quoted`). This is a brand use of the logo's line, so it may be red (principle 3, ADR 0003). It is the only red outside the walk-away label and the logo.

## 3. Tokens

All tokens are CSS custom properties on `:root`. `:root[data-theme="dark"]` redefines each one. Light mode is required and dark mode is optional (Spec 14.4).

### 3.1 Colour: surfaces

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--bg-canvas` | `#ECEEF0` | `#16181B` | The app background (cool grey chrome) |
| `--bg-surface` | `#F8F8F7` | `#1D2024` | Sidebar, app bar, panels, dialogs, inputs, buttons |
| `--bg-sunken` | `#E4E6E9` | `#121417` | The document viewer well, segmented tracks, active nav item, disabled buttons |
| `--bg-tone` | `#F3EFE8` | `#24221F` | Groups: cards, tables, notices, options (warm, no border) |
| `--bg-paper` | `#FBF8F2` | `#1F1D1A` | The contract sheet only, plus First launch |
| `--bg-hover` | `#F1F2F3` | `#26292E` | The hover state on rows, ghost buttons and menu items |
| `--bg-scrim` | `#1F232866` | `#00000099` | The dialog backdrop |
| `--line` | `#DDD6CA` | `#33363B` | Hairlines: dividers, table rows, region edges |
| `--line-strong` | `#C2C6CC` | `#4A4E55` | Control borders: buttons, inputs, step rings |

### 3.2 Colour: text and action

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--text` | `#1F2328` | `#EEF0F2` | Body text, headings, the focus ring |
| `--text-2` | `#5C574F` | `#BDB7AD` | Secondary text (`.muted`), icons |
| `--text-3` | `#66615A` | `#9A958D` | Tertiary text (`.faint`), hints, keyboard shortcuts |
| `--text-inverse` | `#FFFFFF` | `#1F2328` | Text on ink |
| `--action` | `#1F2328` | `#EEF0F2` | The primary button, toggle on, toast |
| `--action-hover` | `#3D4148` | `#D5D8DC` | The primary button on hover |
| `--pencil` | `#565A61` | `#A3A7AD` | Graphite, for pencilled marks |
| `--ok` | `#1B6B3C` | `#86D8A6` | Success ticks ("Key works") |

### 3.3 Colour: labels

Each label has three tokens:

- **solid** (`--x`) for the stamp block, the border and the pin border;
- **fg** (`--x-fg`) for the word and for text on a tint;
- **bg** (`--x-bg`) for the clause wash and for warning notices.

| Label | Icon | Solid | fg | bg | Dark solid / fg / bg |
| --- | --- | --- | --- | --- | --- |
| Preferred | ✓ `i-check` | `#2E8B57` | `#1B6B3C` | `#E3F1E7` | `#4CB57A` / `#86D8A6` / `#16301F` |
| Acceptable | ≈ `i-approx` | `#3A72B8` | `#1D5594` | `#E3ECF8` | `#5C93D8` / `#93BCF2` / `#172437` |
| Walk-away | ✕ `i-x` | `#A91207` | `#8E0F06` | `#F8E3E1` | `#D23A2C` / `#FF9A8F` / `#3A1512` |
| Unsure | ? `i-help` | `#B7791F` | `#7A4E00` | `#FCEFD2` | `#D9A040` / `#F2C46B` / `#33270F` |
| Not covered | dashed ring `i-ring-dashed` | `#8A857C` | `#55524C` | `#ECEAE5` | `#6F6A62` / `#BDB8AF` / `#2A2825` |

`--red` and `--red-tint` are aliases for the walk-away solid and bg, for the logo and brand uses.

**Warnings borrow Unsure.** A warning that isn't a label (a bad key, a scanned PDF, no credit) uses `--unsure-bg` / `--unsure-fg`, with the icon in `--unsure`. This keeps red for walk-away only.

### 3.4 Colour: marks and banners

| Token | Light | Dark | Role |
| --- | --- | --- | --- |
| `--hidden-bg` / `--hidden-fg` | `#FFF07A` / `#5C4A00` | `#4A4000` / `#FFE866` | Hidden text (highlighter yellow with a dashed outline) |
| `--banner-bg` / `--banner-line` | `#FFF8DB` / `#E8CF6B` | `#2E2810` / `#6B5A1C` | Top banners |
| `--swap-bg` / `--swap-fg` *(page-local)* | `#F7D29A` / `#3B2A10` | `#5C3F12` / `#FBE3BE` | Replaced personal details (privacy check). These are defined only in `privacy-check.html`; see 8.2. |

Hidden text, replacements and labels each have their own colour family. Banners share hidden text's yellow family, but a banner is a full-width strip with an icon and words, never a mark on the contract's words.

### 3.5 Typography

There are four families:

| Token | Stack | Use |
| --- | --- | --- |
| `--sans` | IBM Plex Sans, system-ui | All interface text |
| `--serif` | IBM Plex Serif, Georgia | Display and H1, notes, quotes, clause text in boxes, the reading log |
| `--mono` | IBM Plex Mono, ui-monospace | Clause numbers, timestamps, placeholders (`Person 1`), shortcuts |
| `--contract` | Liberation Serif, Times New Roman | Typeset contract pages only. This is the contract's look, not the app's voice. |

The base is `14px/1.5 var(--sans)` on `body`.

| Class | Font | Use |
| --- | --- | --- |
| `.display` | Serif 600 30/1.2, −0.005em | First launch headline (fluid, 32–42 px, there) |
| `.h1` | Serif 600 22/1.3 | Page titles |
| `.h2` | Sans 600 17/1.35 | Section titles |
| `.h3` | Sans 600 14/1.4 | Card and group titles |
| *(body)* | Sans 400 14/1.5 | Default text |
| `.small` | 12.5/1.45 | Secondary lines, table cells, hints |
| `.note` | Serif italic 15/1.5 | The friend's voice: margin notes |
| `.note-s` | Serif italic 13/1.5 | Short notes |
| `.quote` | Serif 15/1.6 | Quoted evidence; the exact words are bold and underlined in the label colour |
| `.mono`, `kbd` | Mono 500 12/1.4 | Numbers, codes, shortcuts |
| `.label`, `.field label` | Sans 500 12.5/1.45 | Form labels |
| Stamp word | Sans 700 11.5, +0.08em, uppercase | Label stamps only |
| Table head | Sans 600 12/1.3 | Column titles |

**Weights.** Use only 400, 500, 600 and 700. Use 700 only in stamps and contract headings.

### 3.6 Spacing

There are no spacing tokens. The prototype uses a 2 px step that settles on these values:

`2 · 4 · 6 · 8 · 10 · 12 · 14 · 16 · 20 · 24 · 32 · 40 · 48`

| Context | Value |
| --- | --- |
| Main content padding | 32 top, 40 sides, 48 bottom (16 below 860 px) |
| Card padding | 20 |
| Dialog body | 24, gap 14 |
| Gap between stacked cards | 16 |
| `.stack` / `.row` gap | 12 |
| Icon-to-text gap | 8 (buttons), 10 (nav, menus) |
| List rows | about 40 px tall (design direction, principle 9) |
| Contract sheet padding | 48 × 56 (review), 40 × 48 (other screens) |

Proposed tokens for the real build: `--s-1: 4px` up to `--s-8: 48px`, mapped to `4 8 12 16 20 24 32 48`. Fold 6, 10 and 14 into the nearest step except inside dense controls.

### 3.7 Shape

| Token | Value | Use |
| --- | --- | --- |
| `--r` | 4 px | Buttons, inputs, nav items, menu items, segment buttons |
| `--r-lg` | 8 px | Cards, tables, notices, dialogs, menus, segmented tracks, toasts |
| *(stamp)* | 3 px | Stamps and pins: deliberately square (ADR 0002) |
| *(circle)* | 50% | Step numbers, toggle knobs, trail knots, the `?` button |
| *(pill)* | 999 px | The toggle track only |

**Borders.**

- 1 px `--line` for hairlines between regions;
- 1 px `--line-strong` for controls;
- 1.5 px in the label colour for stamps and pins;
- 2 px for focus and selection outlines.

### 3.8 Depth

There are three levels, and only one of them is in-page.

| Level | Shadow | Use |
| --- | --- | --- |
| Sheet | `0 1px 2px rgba(27,26,23,.08), 0 6px 18px rgba(27,26,23,.10)` | The contract page, and the first-launch card: the lifted page |
| Menu | `0 8px 28px rgba(27,26,23,.2)` | Popover menus |
| Dialog | `0 12px 40px rgba(27,26,23,.25)` over `--bg-scrim` | Dialogs, side panels, the command palette |

Everything else is flat. Depth inside a page comes from tone (`--bg-tone`, `--bg-sunken`), never from a shadow.

### 3.9 Motion

Motion is small, short and tied to a change the user caused. This is the complete list. There are no spinners, nothing loops, nothing moves for decoration, and the reading log, not an animation, shows that work is going on. Every row stops under `prefers-reduced-motion: reduce`, and the finished look shows at once. Updated 15 Nov 2026 (owner).

| Motion | Time | Reduced motion |
| --- | --- | --- |
| The Private mode switch: the knob slides and the track changes colour | 150 ms ease | Stops |
| The sidebar folds to the icon rail (the width of the first column) | 150 ms ease | Stops |
| Icon movements on action icons (5.13): the arrow nudges, the plus turns, a press shrinks the icon | 150 ms ease, transform only | Stops |
| The logo: the butterfly folds its wings once when the logo is pointed at or reached with the keyboard (owner, 15 Nov 2026). The name stays still, and the logo files are unchanged | 110 ms ease-in, then 180 ms ease-out, transform only | No movement |
| The progress pie fills as positions are checked (the column, the title and the window tab, all at once) | 300 ms ease-out, no bounce | Jumps |
| A pin becomes filled when its label is decided | 300 ms ease-out | Stops |
| The full disc and its check appear when every position is checked | 150 ms ease-out, after the fill | Stops |
| The `?` on a group heading fades in on hover and keyboard focus | 150 ms ease-out | Stops |
| First launch, welcome: the logo, the headline, the line and the buttons arrive one after another, each rising 8 px as it fades in (owner, 15 Nov 2026) | 300 ms each, 140 ms apart | Stops, and everything shows at once. Also off on `?state=` pages |
| First launch, Welcome and Add your key: the old view fades and moves 16 px away, the new one comes in from the side it is on | 150 ms out, 150 ms in | Stops, and the view swaps at once |
| First launch, the key check: "Key works" rises 4 px as it fades in, and its check grows from half size | 250 ms ease-out | Stops, and the line shows at once |
| The flow stepper, on every load of a step page: the line into the current step draws from the left, then the ring appears. On step 1, which has no line, the ring and its inner dot grow in from the centre | 400 ms ease-out, then 150 ms. Step 1: 300 ms | Stops, and the finished look shows at once |
| The flow stepper, when the user presses the step's forward button: this dot becomes done (a check) and the next line starts to draw, then the page changes | 200 ms before the page changes | Stops, and there is no delay |
| The bar in the Load file dialog while a file is read | 400 ms linear, per page | Stops |
| The knob of the `.toggle` in Settings | 150 ms (`left`) | Not yet handled (8.3) |
| The arrow of the first-launch primary button moves 2 px on hover and focus | 150 ms ease-out | No movement |

**Never animated:** stamps and pins on the page (a pin only changes colour once), the reading log, and anything that repeats. The movements show a change that happened. They never invite a click.

For the real build, use 150 ms ease-out for state changes, and respect `prefers-reduced-motion` for every row.

### 3.10 Breakpoints

| Width | Change |
| --- | --- |
| ≤ 1100 px | Review: the Pages toggle and the thumbnails hide, and the contract and the column stack |
| ≤ 900 px | First launch: the picture is a 220 px band above a full-width card, with no shadow and square corners |
| ≤ 860 px | The sidebar goes above the content, and Collapse menu is hidden; two-column grids and flow side panels stack; tables scroll sideways |
| Text size 150% or 200% (`html[data-text]`, set by `app.js`) | Same as ≤ 860 px (the sidebar is never folded), and the app bar and button rows wrap. First launch is laid out as at ≤ 900 px. In the review the Pages toggle and the thumbnails hide, the contract and the column stack, and the group headings, the progress line and the detail head wrap. The window width is unchanged, so the media queries don't fire |

The design target is a laptop of about 1366 × 768 (Spec 14.4).

## 4. Icons

**The icon set** is in `prototype/icons.js`. It is [Remix Icon](https://remixicon.com) 4.9.1 in its line style: a 24 px grid, filled paths in `currentColor`, with no tiles. It replaced the drawn ink set (1.6 px strokes on a 16 px grid) on 14 Nov 2026, at the owner's request (design direction, principle 9, has the earlier choice). Icons are used as `<svg class="icon"><use href="#i-name"/></svg>`. `.icon` is 16 × 16, coloured `--text-2`, and inherits the colour inside buttons.

Four icons are still hand-drawn, on the old 16 px stroked grid, because Remix has no match: `approx` (≈), `ring-dashed` and `thread`, and `help`, whose Remix version is too small at 12 px inside the Unsure stamp.

There are 49 icons in the sprite, 45 from Remix and the 4 above. Three Remix icons were added on 15 Nov 2026: `home` (the Home window tab), `sidebar-fold` and `sidebar-unfold` (the Collapse menu and Expand menu button).

`approx arrow-left arrow-right book check chev-down chev-left chev-right clock cloud-off copy doc dots download drag eye-off filter gear help home info key link list lock mail merge minus paste pause pencil play plus refresh ring-dashed scissors search shield sidebar-fold sidebar-unfold textsize thread trash undo unlock upload users warn x`

**Licence.** The Remix icons are under the Remix Icon License v1.0 (January 2026), not the repository's licence. The text is in `prototype/LICENSE-remixicon.txt`. A plain reading, not legal advice: it allows the icons inside a product that is sold, as functional parts, and forbids selling or redistributing them as an icon pack, or using one as a logo. [ADR 0007](adr/0007-document-reading-stack.md) records it, and the third-party licences page lists it ([ux-copy 4.18](ux-copy.md#418-third-party-licences-licenceshtml-not-built-yet)).

**Rules.**

- An icon always sits next to a word, except in icon buttons, which need an `aria-label`.
- Never use a sparkle for AI. "AI judgment" is a pencilled stamp plus the plain words.
- The label icons are fixed: ✓ `check` preferred, ≈ `approx` acceptable, ✕ `x` walk-away, ? `help` unsure, and `ring-dashed` not covered (ADR 0002). Don't reuse them for other meanings next to labels.

### 4.1 Never

These make an app look machine-made, or look like every other AI tool. None is used, in the prototype or in the build.

| Never | Use instead |
| --- | --- |
| A sparkle, a wand or a robot to mean AI | The pencilled stamp and the plain words “AI judgment” |
| Gradients, glow and blur | Flat tone. The pencil hatch is the one pattern, and it means "pencilled" |
| Emoji | An icon from the set, next to a word |
| Illustration beyond the First launch picture | Real content |
| Skeleton loaders, shimmer and spinners | The reading log and the step gauges |
| Typing or streaming effects on text | The finished text, shown at once |
| Motion that loops, or moves for decoration | The short movements listed in 3.9, each tied to a change the user caused |
| Pill badges for status | The gauge (5.8) and the square stamp (5.2) |
| The names "assistant", "copilot" or "agent" for the AI | "the AI", or the plain action ("Ask AI") |
| A third corner radius, or a second in-page shadow | `--r` and `--r-lg`; the sheet shadow only |
| Meaning carried by colour alone | A colour, an icon and a word (rule 5) |

The signs of machine-made words are in `ux-copy.md` section 1.1.

## 5. Components

### 5.1 Button `.btn`

The default is 36 px tall, with a 0 14 px padding, `--r`, a `--line-strong` border on `--bg-surface`, and Sans 600 13.5.

| Variant | Class | Use |
| --- | --- | --- |
| Secondary | `.btn` | Most actions |
| Primary | `.btn-primary` | The one main action on a screen (ink fill). Home rows have one only: "Check 9 →". |
| Ghost | `.btn-ghost` | Low-weight actions in toolbars and footers |
| Small | `.btn-sm` | 28 px; inside rows, panels and banners |
| Block | `.btn-block` | Full width |
| Icon | `.icon-btn` | 32 × 32, transparent; needs an `aria-label` |
| Text link | `.link` | Inline actions and next steps (Continue, Resume, Retry) |

| State | Look |
| --- | --- |
| Hover | `--bg-hover` (primary: `--action-hover`) |
| Focus | 2 px `--text` outline, 2 px offset (global `:focus-visible`) |
| Disabled | `[disabled]` or `[aria-disabled="true"]`: `--bg-sunken`, no border, `--text-3`, not-allowed |
| Busy | The label changes to the action's progress ("Checking key…") with an icon. There is no spinner. |

- **Do:** name the outcome ("Send for review", "Copy to your playbooks").
- **Don't:** make a red button. A destructive action is never red. The button that opens it is secondary, and the confirm button in its dialog is the one dark primary button with an exact label ("Delete everything"). The dialog names what will go and says when it can't be undone (owner, 15 Nov 2026).

**Icon movements** (15 Nov 2026, owner). An action icon inside a button, link, nav item or menu item moves a little on hover and keyboard focus: an arrow or chevron nudges 2 px the way it points, a plus turns 90°, a gear turns 30°, download sinks 2 px, upload rises 2 px, copy lifts 1 px, search grows 6%, and a nav icon shifts 1 px. A press shrinks any of them to 94%. The movement is 150 ms, transform only, and it is off under reduced motion. It never touches stamps, pins or the logo, and nothing loops. The CSS finds the icon by its sprite name, so no page needs markup for it.

### 5.2 Label stamp `.stamp`

This is the main signal in the app (ADR 0002). It is 22 px tall, with a 1.5 px border in `currentColor` and a 3 px radius. It has two parts:

- `.mark`: a 20 px solid block with a 12 px icon, in surface colour;
- `.word`: Sans 700 11.5, uppercase, 0.08em, in the fg colour, on surface.

```html
<span class="stamp walk"><span class="mark"><svg><use href="#i-x"/></svg></span><span class="word">Walk-away</span></span>
```

| Modifier | Meaning |
| --- | --- |
| `.preferred` `.acceptable` `.walk` `.unsure` `.grey` | The level |
| `.pencilled` | The app judged it from the wording (AI judgment): a dashed graphite border (`--pencil`) and a hatched block. **Only pencilled stamps are dashed** (ADR 0002, amendment). |

The stamp is always followed by a `?` button (`.q`) that opens the definition, at least in the heading of each group in the Labels list and in the detail.

### 5.3 Pin `.pin`

An 18 × 18 square with a 1.5 px border in the label colour, a dark number (Sans 600 11) and a 3 px radius. A pin is **inked** (`.inked`) once the user has decided its label, and an outline until then. The fill is the label's fg shade, so the 11 px number keeps 4.5:1, and the number turns `--bg-surface`. A pencilled pin has a dashed `--pencil` outline, then a solid `--pencil` fill. This holds for the pin on the page and the pin on the list row. The pin's accessible name ends “, checked” or “, not checked”. It sits in the page margin beside a clause and opens that clause's detail in the right column. Pins are numbered down the page (1, 2, 3…), not by position: in the sample, position 10 has pin 7. The same number appears on the label's row in the Labels list.

### 5.4 Clause wash `.clause`

This is a typeset clause on the sheet. It is a grid of pin, number and text (`22px 40px 1fr`). At rest only walk-away and unsure clauses carry their wash (the label's bg colour on `.text`). A preferred or acceptable clause shows only its pin, and gets its wash only when it is selected (`.focus`). `.pencilled` adds a dashed graphite underline on any level, and `.focus` adds a 2 px ink outline. The review scrolls the contract to the clause of the open detail and gives it `.focus`. Not-covered clauses are not drawn on the page (ADR 0001).

### 5.5 Contract sheet `.sheet`

- **Look:** a paper background; Liberation Serif 14.5/1.65; padding 48 × 56; at most 720 px wide; and the only in-page shadow.
- **Headings:** contract headings are uppercase and bold.
- **Running head:** `.running-head` at the top of the page.
- **Text colour:** the text uses near-black `#1F1F1F` (dark mode `#E8E4DC`), not `--text`, so the page reads as a printed document.

### 5.6 Hidden-text mark `mark.hidden-text`

Highlighter yellow (`--hidden-bg`) with a 1 px dashed outline in `--hidden-fg`. It is never a label colour. In the contract check, hidden text also gets a chip with an eye-off icon and the words "Hidden text".

### 5.7 Replacement mark `.swap` (privacy check)

An amber tint with a 2 px radius. It shows the real value or the placeholder (`Person 1` in mono), depending on the viewer's mode, and `.off` shows a false alarm that was unticked.

### 5.8 Review status gauge `.gauge` (Home)

A 16 px circle gauge plus a next step. It is never a pill and never red (Spec 14.4).

| Status | Gauge | Next step |
| --- | --- | --- |
| Draft | Dashed ring | Continue (link) |
| Running | Fills by step, "Step 2 of 4 · about 40 s" | none |
| Interrupted | Pause | Resume (link) |
| Failed | "!" | Retry (link) |
| Ready to check | Solid ink disc; the row is in bold | "Check N →" (the only primary button) |
| Done | Quiet grey tick | Open message (link) |

### 5.9 Inputs

| Component | Class | Notes |
| --- | --- | --- |
| Field | `.field` > `label` + `.input` + `.hint` | 6 px gap; the label is Sans 500 12.5 |
| Text input | `.input` | 38 px tall, `--r`, a `--line-strong` border on surface |
| Textarea | `textarea.input` | At least 76 px, resizes vertically |
| Search | `.search` | An icon inside on the left, 36 px left padding |
| Flagged | `.input.is-flagged` | A `--unsure` border and a 1 px ring (a warning, never red) |
| Checkbox | `.check` | 16 px, `accent-color: --text` |
| Toggle | `.toggle` | 34 × 20, a `--line-strong` track that turns ink when on |
| Segmented | `.segmented` | A sunken track; the pressed item is raised on surface with weight 500 |
| Tabs | `.tabs` | The same look as segmented, with `role="tab"` and `aria-selected` |
| Option | `.option` | A tone row with a radio or checkbox; when checked it gets a 2 px ink outline |
| Command search | `.search-commands` | A 32 px toolbar box that opens the palette, with a Ctrl+K hint. The review has no such box: its first row in the More actions menu, “Search commands”, opens the palette. |

Validation messages sit below the field in Unsure colours, with an icon and words.

### 5.10 Groups

| Component | Class | Look |
| --- | --- | --- |
| Card | `.card` | `--bg-tone`, `--r-lg`, padding 20, no border, 16 px between stacked cards |
| Table | `.table` | A tone background, `--r-lg`, rows split by a `--line` hairline, a `.name` cell in 14 px with a `small` second line |
| Divider | `.divider` | 1 px `--line` |
| Toggle row | `.toggle-row` | A tone row: toggle, title and small explanation |

### 5.11 Feedback

There are two warning levels and three types of message.

| Component | Class | Use |
| --- | --- | --- |
| Banner | `.banner` | Top of the review only, and never more than one at a time: the practice review and the playbook-changed warning. It uses a banner colour, sits full width below the app bar, and holds an icon, the words and one or two small actions. The practice banner stays. The playbook-changed banner stays until the review is re-run. The hidden-text, unloaded-document and unedited-starter warnings are not banners: they are “Read first” rows (next row). |
| Read-first row | `.warn-row` | A row at the top of the Labels list, under a “Read first” heading. It holds an Unsure-colour icon, a short name (“1 piece of hidden text”, “Master Agreement not loaded”, “Example playbook, unedited”), a tick slot and a chevron. A click opens the hidden-text or starter warning in the column, with its full text, its actions and “All labels”, or opens the unloaded-document dialog. The row counts as read after its action (“Show me”, “Got it”): it turns faint and gets a tick, and it still opens. *Replaces the owner decision of 14 Nov 2026 that a read banner shrinks to a chip in the summary bar. Replaced 14 Nov 2026, the same day, when the summary bar went.* |
| Notice | `.notice` | An inline tone strip with an icon and text. It is used for information such as auto-delete. |
| Warning notice | `.notice.warn` | Unsure colours, for anything that blocks or needs a fix. *(Defined per page; see 8.1.)* |
| Toast | `.toast` | An ink bar (8 px corners) at the bottom centre with short past-tense words: "Copied", "Saved", "Replaced. Check the marked words." It is triggered by `data-toast`. |
| Reading log | `.log` (running) | Mono timestamp plus a Serif 15 line. A finished line is `--text` and upright. The line of the step still running is `--pencil` italic, with no dash, because only pencilled labels are dashed (`.running`, `aria-current="step"`; owner, 15 Nov 2026). A stopped line keeps Unsure fg. Nothing animates. |
| Progress bar | `.load-bar` (Load file dialog) | 4 px tall, ink. The review uses the progress pie (5.14), and the running screen has a status pie (next row). |
| Status pie | `.stage-head .pie` (running) | One ring, 28 px, with a wedge that grows as the review moves through its eight small steps (owner, 15 Nov 2026, after Linear’s status icon; a stage list was tried first and rejected). The step that is running counts as half done. It is ink while running, an Unsure ring and wedge when the review stops, and a full ink disc with a check when done. Beside it: the title (“Step 2 of 4 · Matching clauses”) and, under it, the name of the small step that is running. The wedge grows over 300 ms ease-out and jumps under reduced motion (same `.pie` as 5.14). |

### 5.12 Overlays

| Component | Class | Notes |
| --- | --- | --- |
| Dialog | `dialog` | A surface background, `--r-lg`, the dialog shadow, at most 560 px wide. It has a `.dialog-body` (24 px, gap 14) and a `.dialog-foot` (right-aligned, gap 8). |
| Wide dialog | `dialog.wide` | At most 860 px (rewrite, before and after) |
| Side panel | `dialog.panel` | Full height on the right, at most 480 px wide, square corners. Used for Suggestions. The label detail is not an overlay: it sits in the review's right column (5.14). |
| Load dialog | `dialog.load-dialog` | See “Load dialog” under 5.13. |
| Command palette | `dialog.palette` | 10vh from the top; a 48 px input, grouped results, and a shortcut on every row |
| Menu | `.menu` | A popover of at least 200 px, `--r-lg`, the menu shadow, 8 × 10 items |

### 5.13 Navigation

| Component | Class | Notes |
| --- | --- | --- |
| Sidebar | `.sidebar` | 232 px, sticky, on surface; ends in `.sidebar-foot` (Private mode, credit) and the Collapse menu button. See “Folding sidebar” below. |
| Nav item | `.nav a` | A 16 px icon and the label. When current: sunken, 500, and a 3 px ink marker on the right. **The marker is never red.** |
| App bar | `.appbar` | 56 px, for flow screens: back, the title with a small subtitle, steps, search, actions. In the review: back, the title and subtitle, a spacer, a “…” More actions menu (`.menu`) and Output. |
| Flow stepper | `ol.steps` | See “Flow stepper” below. |
| Window tabs | `.wintabs` | See “Window tabs” below. |
| Private mode switch | `.pm-switch` | See “Private mode switch” below. |
| Flow footer | `.flow-foot` | Sticky at the bottom with the primary action ("Looks right, continue", "Send for review") |
| Page head | `.page-head` | The title and a muted line on the left, actions on the right |

**Window tabs** (`.wintabs`, added 15 Nov 2026 at the owner's request). A 36 px strip at the top of every page except First launch and the prototype map, on `--bg-sunken`. `app.js` adds it, so a page carries no markup for it. It holds a Home icon button, one tab per open review, and a “+” that opens New review. A tab is the review's progress pie (14 px; a document icon for a new review that has no positions yet), the review's name (ellipsis after 200 px) and a close button (`Close tab, [name]` as its label). The current review tab is raised: `--bg-surface`, joined to the page below it. Home is not a document, so when current it is a pressed button with its own outline, which keeps it clear of the sidebar or the icon rail below it. Home is current on the sidebar pages. A closed tab that was open sends the user Home. The strip is sticky, and its height is the variable `--wintabs-h`, which the sidebar and the full-height screens subtract from their own height. On the empty Home and on the error page the strip shows Home only, because no review is open there. The tabs are prototype data in the `ct-tabs` store key. Several reviews open at once is a decision the build plan does not yet cover (Spec 13).

**Window tabs and the sidebar line.** The home button keeps its size in both states. Its left padding moves with the sidebar (16 px open, 12 px folded, eased over 150 ms) so its icon sits on the same centre line as the icons below it. The folded rail's logo is centred the same way (15 Nov 2026).

**Settings layout** (`.set-layout`, 15 Nov 2026). A 200 px list of five groups on the left (`.set-nav`, sticky) and one group at a time on the right (`.set-panel`, at most 640 px). Each group opens with a title and one line, then rows in a tone card (`.set-group`): a `.srow` has its name and one line on the left and its control on the right. Narrow windows stack the list above the group. Links such as `settings.html#ai-key` open the group that holds the anchor.

**Folding sidebar.** The Collapse menu button ends the sidebar. It folds the sidebar to a 56 px icon rail and shows “Expand menu”. Ctrl+B does the same, and the choice is kept (`ct-sidebar`). In the rail the labels are hidden but stay the accessible names, the logo becomes the symbol alone (`symbol.svg`, 28 px, a link Home), and each item shows its words as a small ink tooltip on hover and on keyboard focus. The width changes in 150 ms. A window of 860 px or less, and 150% or 200% text, ignore the fold and hide the button, because the sidebar is already above the content or the labels would not fit.

**Private mode switch** (`.pm-switch`, `role="switch"`, replaces the dropdown badge; 15 Nov 2026). A 32 px button with a 36 × 20 px track, a 16 px knob and the label “Private mode” (“Private mode for this review” in the Privacy check). **On** is the Preferred green (`--pref`) with an “I” on the knob. **Off** is neutral (`--line-strong`) with an “O”. It is never red: off is not a walk-away, and the oxblood stays with the walk-away label and the logo (ADR 0003). The “I” and “O” and `aria-checked` carry the state, so it reads without colour. Turning it on is one click. Turning it off opens a dialog once (“Turn private mode off for this review?”, Cancel and Turn off). One toast says “Private mode on” or “Private mode off”. The choice is kept (`ct-private`) and the switch is used on the Privacy check only. The Running screen says private mode in words in its footer, and keeps one button, “Turn private mode off…”, for the stop where no private-mode model is free (owner, 15 Nov 2026). It is not on the Review screen (owner, 15 Nov 2026): by then the AI calls are done, so a switch there would change nothing the user can see.

**Flow stepper** (`ol.steps`, `data-step="n"`; 15 Nov 2026). The four steps (Contract, Contract check, Privacy check, Review) are names in a row, 112 px each, over a 2 px line with one dot per step. A finished step is an ink dot with a check and is a link back to that step (except on Running, where nothing can be reopened). The current step is a dot with an ink ring and has `aria-current="step"`. A later step is a hollow grey dot. The line into a step is ink once that step is finished or current, and `--line-strong` before. Ink only, never red, and no number. A finished step's name carries a hidden “, done” for screen readers. Motion is in 3.9: it plays on every step page, and the forward button plays a short leave before the page changes.

**Load dialog** (`dialog.load-dialog`, New review; 15 Nov 2026). Opened by “Load file”, a small dialog (at most 480 px) that holds one pane at a time: a drop zone with “Choose a file”; “Reading page n of 5” with a file badge, a 4 px determinate bar (`role="progressbar"`) and Cancel; “Contract loaded” with a green tick, “Replace”, the first-page preview and “Done”. An error shows inside the dialog as a warning notice. The bar is determinate because the page count is known, so it is not a spinner. The file is read on this computer and the dialog says so.


### 5.14 Review-specific

| Component | Class | Notes |
| --- | --- | --- |
| Pages toggle | `.pages-toggle` | A ghost button at the left of the viewer bar, with `aria-pressed`. It shows or hides the thumbnails. It is hidden at ≤ 1100 px and at 150% and 200% text. |
| Thumbnails | `.thumbs` | A 96 px column of page thumbnails, with label dots. Hidden until the Pages toggle is pressed. The dots still use colour alone (8.3). |
| Progress block | `.progress-block` | One line: an 18 px **progress pie** (`.pie`, ink: a ring, and a disc that grows from the centre with the share of positions checked), the words “2 of 11 positions checked”, and “Next unchecked” with J on the right. When every position is checked the pie is a full disc with a check, and the words are “Every position is checked”. The pie only repeats the words, so it is `aria-hidden`. There is no 3 px bar any more (15 Nov 2026). The same pie, 24 px, sits before the review's title in the app bar, and 14 px in that review's window tab. All three follow a decision at once, also while a label's detail is open, and the wedge grows in 300 ms. The Home status gauge for “Ready to check” stays a solid disc (5.8): it is a status, and a share there would turn it into a second progress mark. |
| Group heading | `.group-head` | The stamp, the count of positions (faint) and the `?`, which shows on hover and keyboard focus only. The Labels list is grouped by level: Walk-away, Unsure, Acceptable, Preferred. “· 3 in Missing” sits next to Acceptable. “· 1 pencilled in” is hidden text for screen readers: the dashed pin already shows it. The Missing tab has one heading (Acceptable), not a stamp on every row. |
| Label list | `.label-list` | Quiet rows, with no rule between them and a hover tone: a pin, the position's title that truncates, and the clause number (“§ 5.4”, mono, at the right). A row has no stamp, because its group heading has it, and the position number is only in its accessible name (“Position 5 · Revision rounds”). A decided row's pin is filled and its title faint; the tick shows only on rows without a pin (Missing). The column truncates a long row with an ellipsis and never widens, so the tabs stay in view. |
| Governing-law line | `.law-line` | A small faint line at the bottom of the Labels list: an icon and one sentence. The two-law and no-law versions use the Unsure icon colour. |
| Detail | `.detail`, `.detail-head`, `.detail-card` | One label's detail, in the right column in place of the list. The tone sits on the evidence card and on “What to check” only, so a detail is not tinted twice. The head (`.detail-head`) is sticky: “All labels” (Escape does the same), “Next unchecked” and J, then the title. `.detail-card` is a tone card (`--bg-tone`, `--r-lg`, padding 16) holding the quote, its two links, the stamp and the lead sentence. |
| Not-covered tick | `.label-list li.grey-confirm` | The tone row at the top of Not covered: "I've read the 37 not-covered parts" |
| Evidence trail | `.trail` | A 12 px ring "knot" plus a step: the thread, shown as a list |
| Decide buttons | `.decide` | Full-width option buttons, each with a `kbd` key hint |
| Diff | `.diff` | `del` struck through in `--text-2` (never red, ADR 0003), `ins` on the preferred bg (rewrite, before and after) |
| Fold | `details.more` | Folds the source line, the level matched, the longer explanation and the evidence trail (decided 14 Nov 2026) |
| AI wording line | `p.small.faint` | “Every quote and number was checked against the contract; the wording was written by AI.” Sits under every block of AI-written text in a panel or dialog, and under no code-written block. |
| Contract link | `.contract-link` | A quiet underline that opens only after the link warning |

## 6. Patterns

**Flow screen.** New review, Contract check, Privacy check and Running use the same layout: an app bar with the flow stepper, then the work area on the left (`minmax(0,1fr)`), then a side margin of 340–400 px on surface with a left hairline, then a sticky flow footer.

**The margin.** The signature layout pattern is the margin beside the page (design direction, principle 3). The friend's notes, the reading log, the replacement list and the review's list and detail all sit in a right-hand surface column next to the paper. New screens should use it rather than inventing a new one.

**The review column** (principle 12). The review is the contract and one 400 px column. The column shows the Labels list (with Not covered and Missing as tabs), or one label's detail, or one “Read first” warning, and never two of them. Opening a label swaps the list for its detail. The contract stays visible and scrolls to the clause, which gets the focus outline. “All labels” or Escape brings the list back. Deciding on a label ticks its row and opens the next unchecked one. When none is left, a toast says “Every position is checked” and the list returns. Dialogs and the Suggestions side panel still open over the page. Nothing else covers the contract.

**First launch** (Spec 14.1, screen 1). The picture fills the window. One paper card, about 440 px wide (`--bg-paper`, `--r-lg`, the sheet shadow), lies on it at the left. Its running head reads like a contract page: “Clause Tracer” on the left, “Runs on this computer” on the right, in capitals. The card shows one view at a time. **Welcome** has the logo, the headline, one line under it, the primary button (“Open the free sample contract”), the secondary button (“Check your own contract”) and the legal line. **Key** has “Back”, the heading, a short paragraph, the key field, the primary button of that view (“Save key”), “Skip for now”, the key lines, the folded four steps and the legal line. `?state=key` and the checking, key-ok and key-error states open the key view. Below 900 px, and at 150% and 200% text, the picture is a 220 px band above a full-width card.

**Detail order** (Spec 14.1, screen 8). The head comes first: "All labels", "Next unchecked" with J, and the title. Then:

1. the quote, with the exact words highlighted, and "Show on the page" (scrolls the contract, the column stays as it is) and "Rewrite this clause";
2. the stamp and `?`;
3. the lead sentence (the why, in one or two sentences). Items 1 to 3 sit together in one tone card;
4. "why it could be the other level", the readings and the question to ask (unsure and AI judgment only), with the AI wording line under any AI-written block;
5. what to check;
6. the decision buttons ("Looks right", "Change it", or the three answers; keys 1, 2 and 3 act on the open detail only), then an "Add a note" link that reveals the note field;
7. "More": the source line, the level matched, the longer explanation and the evidence trail.

The source line moved into "More" on 14 Nov 2026 (owner decision 4). The detail moved from a dialog into the column the same day.

**Empty state.** Say what it is, why it's empty and how to start, with real words. For example: "Check a contract against your playbook. It takes about 3 minutes…". Use one primary button and links for the rest.

**Errors.** Say what happened and why, then give the fix as a button. Use Unsure colours and say "Your files are safe" where that is true.

**Confirm deletion.** The title names the thing ("Delete 3 reviews?"). The body lists what goes and says it can't be undone. The button repeats the verb.

**Command palette.** Ctrl+K, or the "Search commands" box (in the review, the first row of the More actions menu), opens it. It opens on the common commands, grouped, with a shortcut on each. Single keys (`data-key`, for example J for "Next unchecked") work only outside inputs.

**Links that leave the app** end with "(opens in your browser)".

## 7. Accessibility

**Contrast.** Measured light-mode ratios:

| Pair | Ratio | AA |
| --- | --- | --- |
| `--text` on canvas | 13.6 | ✅ |
| `--text-2` on canvas | 6.2 | ✅ |
| `--text-3` on sunken (the lowest-contrast use) | 4.9 | ✅ |
| Label fg on its bg (preferred to not covered) | 5.6 – 7.7 | ✅ |
| Hidden fg on hidden bg | 7.4 | ✅ |
| Stamp block vs surface (non-text, needs 3:1) | Unsure 3.4, Grey 3.5, Pref 4.0, Acc 4.6, Walk 7.1 | ✅ |
| Dark: surface icon on grey block | 3.05 | ✅ (just) |
| **`--line-strong` input border on surface** | **1.6** | ❌ see 8.3 |

**Keyboard.**

- Every control can be reached with Tab.
- Focus is a 2 px ink outline.
- Dialogs use the native `<dialog>`, so focus is trapped and Escape closes them.
- In the review, opening a detail moves focus to its title. Escape, or "All labels", returns to the list and puts focus back on the row it came from. Keys 1, 2 and 3 answer the open detail, and J opens the next unchecked label.
- Tabs use `role="tablist"` with `aria-controls`.
- Segmented buttons use `aria-pressed`.
- Nav uses `aria-current="page"`. The window tab of the page the user is on does too.
- The Private mode switch is a `role="switch"` with `aria-checked`. The Collapse menu button has `aria-expanded`.

**Screen readers.**

- Stamps carry their word as text.
- The `?` buttons have labels ("What Unsure means").
- Icon buttons have an `aria-label`.
- `.visually-hidden` is available for extra context.

**Text size.** In Settings, `data-text-set` scales the type to 100%, 125%, 150% or 200%.

## 8. Audit: where the prototype drifts

**Summary.** 17 screens, about 60 shared classes and 49 icons. 28 issues found, 11 fixed (counted 14 Nov 2026; 14 found and 4 fixed on 7 Nov 2026). The tokens are well used in shared CSS. Most drift sits in page-local `<style>` blocks and inline styles.

### 8.1 Naming and duplication

| Issue | Where | Fix |
| --- | --- | --- |
| ✅ **Fixed 15 Nov 2026.** `.notice.warn` is defined three times, identically | new-review, running, privacy-check | Moved to `styles.css`; the page copies are gone |
| The flow layout (`.flow`, `.work`, `.side`/`.margin`) is redefined on each page | contract-check, running, privacy-check | One `.flow` / `.flow-work` / `.flow-margin` in `styles.css` |
| `.cl` (privacy, running) duplicates `.clause` (review) | 3 pages | One clause component with a dense modifier |
| `.thumbs` is redefined in privacy-check with a different thumbnail (`.thumb-img` vs `.t` vs `.thumb`) | review, privacy, new-review | One thumbnail component |
| The margin column is called `.side` on some pages and `.margin` on others | running vs others | Pick `.margin`, the design-direction word |

### 8.2 Tokens

| Issue | Where | Fix |
| --- | --- | --- |
| `--swap-bg/fg` are page-local | privacy-check | Move them to `:root` with the other mark tokens |
| Hardcoded hex: `#55524C` (= `--grey-fg`), `#6B665D`, `#D8D0C0`, `#bbb` ×20 (contract table borders), `#555` | running, privacy-check, review, index | Map to tokens. Contract-page greys can become `--sheet-line` and `--sheet-faint`. |
| ✅ **Fixed 14 Nov 2026.** `.key-form` uses a 10 px radius | index | `--r-lg` (two radii only) |
| There are no exact tokens for the logo's dark (`#1E1D1A`) and light (`#ECE8E1`), and the app's dark text is the cooler `#EEF0F2` | brand vs app | Leave the app tokens; use the logo SVGs as they are. Note it here so nobody "fixes" one into the other. |
| There are no spacing or motion tokens | everywhere | Add them as proposed in 3.6 and 3.9 |
| There are 12 font sizes (11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 17, 22, 30) | everywhere | Keep 11.5 (stamps), 12, 12.5, 14, 15, 17, 22 and 30. Fold 11, 13 and 13.5. |

### 8.3 Spec and ADR gaps

| Issue | Source | Fix |
| --- | --- | --- |
| ✅ **Fixed.** **Dashed means two things.** `.pencilled` (AI judgment) and Not covered both draw a dashed border, so "Not covered" in the summary bar looks pencilled. | ADR 0002 says Not covered is dashed; design direction, action 2 says pencilled is dashed with a hatched block | Decide: keep dashed for pencilled and give Not covered a solid grey border, or add the hatched block so pencilled stays distinct |
| ✅ **Fixed.** **Acceptable and Not covered share an icon.** Both use `i-minus` in review.html, and help.html uses `i-dots` for Not covered. Without colour, the two can't be told apart. | ADR 0002 (≈ and a dashed ring); Spec 14.4 (never colour alone) | Add `i-approx` and `i-ring-dashed` to the sprite and use them everywhere |
| ✅ **Fixed.** The pencilled hatched colour block and the grey dashed clause underline are not built | Design direction, action 2 | Add a hatched `.mark` background and a `.clause.pencilled .text` underline |
| The thin label-colour underline on clauses is missing; there is only the wash | ADR 0002 | Add `text-decoration` in the solid colour to `.clause.<level> .text` |
| Pins use a surface background, but the ADR says a light tint | ADR 0002 | Use `--x-bg` on `.pin.<level>` |
| Input and button borders are 1.6:1 against surface, below the 3:1 needed for a control's edge (WCAG 1.4.11) | Spec 14.4 (AA) | Darken `--line-strong` to about `#8C9097` light / `#6A6E75` dark, or check that the fill difference carries the edge |
| ✅ **Fixed.** Icon stroke is 1.6 px, but the direction said 1.75 px | Design direction, principle 9 | 1.6 accepted; the direction now says 1.6 |
| ✅ **Fixed.** The direction said "Inter" in action 7, but principle 4 later dropped Inter for Plex | design-direction.md | Action 7 now points to Plex |
| ✅ **Fixed 15 Nov 2026.** The reading log isn't pencilled while running and inked when done | Design direction, principle 8 | Finished lines are `--text`, the running line is `--pencil` italic (the dashed underline was dropped on 15 Nov 2026) |
| ✅ **Fixed.** The rewrite diff showed deleted words in walk-away red, which is decoration | ADR 0003 | Struck through in `--text-2` |
| 106 inline `style=` attributes in review.html (mostly `gap` and contract-table cells; counted 14 Nov 2026) | review.html | Fine for a prototype; don't carry them into the build |
| Page-thumbnail label dots in the review use colour alone. The thumbnails are now hidden by default, behind the Pages toggle, but this is not fixed. | Rule 5, Spec 14.4 (found 14 Nov 2026) | Add the label's icon or a count beside each dot |
| ✅ **Fixed 14 Nov 2026.** At 200% text size, 11 of 15 pages scrolled sideways in a 1366 px window (measured by script) | Spec 14.4, section 7 "Text size" (found 14 Nov 2026) | Owner decided 14 Nov 2026: it must fit. At 150% and 200% `styles.css` stacks the sidebar and columns, lets rows wrap and scrolls tables inside their own box. No page or state scrolls sideways at 100%, 125%, 150% or 200% |
| ✅ **Fixed 14 Nov 2026.** The detail panel's order differed: the prototype showed the stamp first, section 6 and Spec 14.1 say the quote first | Section 6, Spec 14.1 screen 8 (found 14 Nov 2026) | Quote first in every panel of the prototype, then the stamp. The source line moved into "More" the same day. |
| ✅ **Fixed 14 Nov 2026.** The review's right column showed a summary bar, a stack of banners, a list and a detail dialog at once. The owner called it overwhelming. | Principle 12 (owner, 14 Nov 2026) | The contract and one column. The column shows the list or one label's detail. The summary bar and the read-banner chips are gone, the three read warnings are “Read first” rows, and the thumbnails are hidden by default. |
| The toggle knob moves for 150 ms and doesn't check `prefers-reduced-motion` | Section 3.9 (found 15 Nov 2026) | Wrap the transition in `@media (prefers-reduced-motion: no-preference)` |
| Four icons are hand-drawn strokes on a 16 px grid (`approx`, `ring-dashed`, `thread`, `help`) among 45 filled Remix icons on a 24 px grid, so their weight differs | Section 4 (found 14 Nov 2026) | Redraw them as filled 24 px paths, or find Remix matches that stay readable at 12 px in a stamp |

### 8.4 Component completeness

| Component | States | Variants | Docs | Score |
| --- | --- | --- | --- | --- |
| Button | ✅ | ✅ | ✅ | 10 |
| Stamp | ✅ | ✅ | ✅ | 8 |
| Pin | ✅ | ⚠️ tint missing | ✅ | 8 |
| Inputs | ⚠️ no error token, borders low | ✅ | ✅ | 7 |
| Notice / banner | ✅ | ⚠️ warn not shared | ✅ | 8 |
| Gauge | ✅ | ✅ | ⚠️ page-local CSS | 8 |
| Dialog / panel / palette | ✅ | ✅ | ✅ | 10 |
| Flow layout | ✅ | ⚠️ 3 copies | ✅ | 7 |

### 8.5 Priority actions

1. ~~Give each label its own icon, and settle "dashed means two things".~~ Fixed 7 Nov 2026.
2. Move the shared warning, flow, clause and thumbnail CSS into `styles.css`, and the swap tokens into `:root`.
3. Fix the control-border contrast, and finish the pencilled look (hatch and underline) and the pin tint.
4. Fix the thumbnail dots found on 14 Nov 2026. The panel order and the 200% text size are fixed.

## 9. Using the prototype

Serve it with the "prototype" launch config, or with:

```bash
python3 prototype/serve.py
```

There is no build and no framework. `app.js` wires the shared behaviour through attributes:

| Attribute | Does |
| --- | --- |
| `data-open="id"` / `data-close` | Opens or closes `<dialog id>` |
| `data-menu="id"` | Toggles a `.menu` |
| `data-key="J"` | Pressing that key clicks the element (Ctrl+K opens the palette) |
| `data-toast="text"` | Shows a toast |
| `data-theme-set` / `data-text-set` | Theme and text size, remembered across pages |
| `data-state="a b"` / `data-state-hide="a"` | Shown or hidden when the URL has `?state=a` |
| `#dialog-id` in the URL | Opens that dialog on load |

`window.CT` exposes `toast()` and `applyTheme()`. `states.html` links every state in Spec 14.2.

**Adding a component:**

1. Use existing tokens.
2. Put it in `styles.css`, not a page `<style>`.
3. Give it a colour, an icon and a word if it carries meaning.
4. Check it in greyscale and in dark mode.
5. Add a row to section 5.
