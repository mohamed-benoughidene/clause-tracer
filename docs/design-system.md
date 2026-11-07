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

These are the ten rules everything else follows. Each one comes from a decision that has already been made.

| # | Rule | Source |
| --- | --- | --- |
| 1 | **The careful friend.** The contract fills the screen, and the app speaks through notes in the margin, in plain words. It feels calm and personal, not like a dashboard. | Design direction, principle 1 |
| 2 | **Paper and ink.** The app chrome is cool grey. Warm paper appears only on the contract sheet. Text and the primary button are ink. | Principle 5 |
| 3 | **Red means one thing.** Oxblood `#A91207` means walk-away: "a line you won't cross". The logo's thread also uses it. Nothing else uses red, not even errors or warnings. | ADR 0003 |
| 4 | **Labels are stamps.** Labels have square corners, a solid colour block with an icon, and the word in small capitals. They never look like the rounded tags or the status gauges. | ADR 0002 |
| 5 | **Never colour alone.** Every label has a colour, an icon and a word, and every view must pass a greyscale check. | Spec 14.4 |
| 6 | **Inked or pencilled.** A label from a clear rule match is inked (solid). A label the app judged from the wording is pencilled (dashed). | Design direction, action 2 |
| 7 | **Two radii, one shadow.** The radii are 4 px and 8 px. Only the contract sheet casts a shadow in the page. Floating layers (dialogs, menus) are the exception. | Principle 6 |
| 8 | **Group by space, then tone, then border.** A group sits on a slightly darker warm tone, with no border. | Principle 7 |
| 9 | **Two voices.** IBM Plex Sans is used for the interface. IBM Plex Serif is used for headings, the friend's notes (in italic) and quotes from the contract. Typeset contract pages use Liberation Serif, the look of the document itself. | Principle 4 |
| 10 | **Real content in every state.** Empty, error and loading states use real words and real numbers. There are no spinners and no fake delays; the reading log shows the actual work. | Principle 8 |

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

- The sidebar shows the logo at 140 px wide. First launch shows it at `clamp(200px, 17vw, 240px)`.
- `.logo .on-light` and `.logo .on-dark` swap between `logo.svg` and `logo-dark.svg` when the theme changes.
- The master files are in `assets/`.

**Don't:**

- recolour the name red;
- move the butterfly between the words or after the name;
- outline it, or give it a shadow;
- redraw the line or add a fifth eyespot;
- repeat the mark as a pattern.

**Imagery.** The only picture is the First launch hero (`prototype/hero-butterflies.webp`). It looks hand-made, has one red thing in it and no text.

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

**Borders.**

- 1 px `--line` for hairlines between regions;
- 1 px `--line-strong` for controls;
- 1.5 px in the label colour for stamps and pins;
- 2 px for focus and selection outlines.

### 3.8 Depth

There are three levels, and only one of them is in-page.

| Level | Shadow | Use |
| --- | --- | --- |
| Sheet | `0 1px 2px rgba(27,26,23,.08), 0 6px 18px rgba(27,26,23,.10)` | The contract page: the lifted page |
| Menu | `0 8px 28px rgba(27,26,23,.2)` | Popover menus |
| Dialog | `0 12px 40px rgba(27,26,23,.25)` over `--bg-scrim` | Dialogs, side panels, the command palette |

Everything else is flat. Depth inside a page comes from tone (`--bg-tone`, `--bg-sunken`), never from a shadow.

### 3.9 Motion

There is almost no motion: only the toggle knob (`left .15s`). There are no spinners, because progress is shown by the reading log and the step gauges.

For the real build:

- use 150 ms ease-out for state changes and 200 ms for panels sliding in;
- respect `prefers-reduced-motion`.

### 3.10 Breakpoints

| Width | Change |
| --- | --- |
| ≤ 1100 px | Review: the thumbnails hide, and the panes stack |
| ≤ 900 px | First launch: the picture moves above the form |
| ≤ 860 px | The sidebar goes above the content; two-column grids and flow side panels stack; tables scroll sideways |

The design target is a laptop of about 1366 × 768 (Spec 14.4).

## 4. Icons

**The drawn ink set** is in `prototype/icons.js`: a 16 px grid, stroked with `currentColor`, round caps and joins, and no fills or tiles. They are used as `<svg class="icon"><use href="#i-name"/></svg>`. `.icon` is 16 × 16, coloured `--text-2`, and inherits the colour inside buttons.

There are 46 icons in the sprite:

`approx arrow-left arrow-right book check chev-down chev-left chev-right clock cloud-off copy doc dots download drag eye-off filter gear help info key link list lock mail merge minus paste pause pencil play plus refresh ring-dashed scissors search shield textsize thread trash undo unlock upload users wand warn x`

**Rules.**

- An icon always sits next to a word, except in icon buttons, which need an `aria-label`.
- Never use a sparkle for AI. "AI judgment" is a pencilled stamp plus the plain words.
- The label icons are fixed: ✓ `check` preferred, ≈ `approx` acceptable, ✕ `x` walk-away, ? `help` unsure, and `ring-dashed` not covered (ADR 0002). Don't reuse them for other meanings next to labels.

## 5. Components

Each entry gives the class, the variants, the states and the main rule.

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
- **Don't:** make a red button. A destructive button is a secondary button with an exact label ("Delete everything"), and the confirm dialog names what will go.

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

The stamp is always followed by a `?` button (`.q`) that opens the definition, at least in the summary bar and the detail panel.

### 5.3 Pin `.pin`

An 18 × 18 square with a 1.5 px border in the label colour, a dark number (Sans 600 11) and a 3 px radius. It sits in the page margin beside a clause and opens that clause's detail panel. Pins are numbered down the page (1, 2, 3…), not by position: in the sample, position 10 has pin 7. The same number appears on the label's row in the Labels tab.

### 5.4 Clause wash `.clause`

This is a typeset clause on the sheet. It is a grid of pin, number and text (`22px 40px 1fr`). The level class tints `.text` with the label's bg colour, `.pencilled` adds a dashed graphite underline, and `.focus` adds a 2 px ink outline. Not-covered clauses are not drawn on the page (ADR 0001).

### 5.5 Contract sheet `.sheet`

- **Look:** a paper background; Liberation Serif 14.5/1.65; padding 48 × 56; at most 720 px wide; and the only in-page shadow.
- **Headings:** contract headings are uppercase and bold.
- **Running head:** `.running-head` at the top of the page.
- **Text colour:** the text uses near-black `#1F1F1F` (dark mode `#E8E4DC`), not `--text`, so the page reads as a printed document.

### 5.6 Hidden-text mark `mark.hidden-text`

Highlighter yellow (`--hidden-bg`) with a 1 px dashed outline in `--hidden-fg`. It is never a label colour. In the contract check, hidden text also gets a chip with an eye-off icon and the words "outlined in the contract".

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
| Command search | `.search-commands` | A 32 px toolbar box that opens the palette, with a Ctrl+K hint |

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
| Banner | `.banner` | Top of the review only: hidden text, unloaded document, playbook changed, unedited starter. It uses a banner colour, sits full width below the app bar, and holds an icon, the words and one small action. |
| Notice | `.notice` | An inline tone strip with an icon and text. It is used for information such as the governing-law chip and auto-delete. |
| Warning notice | `.notice.warn` | Unsure colours, for anything that blocks or needs a fix. *(Defined per page; see 8.1.)* |
| Toast | `.toast` | An ink bar (8 px corners) at the bottom centre with short past-tense words: "Copied", "Saved", "Replaced. Check the marked words." It is triggered by `data-toast`. |
| Reading log | `.log` (running) | Mono timestamp plus a Serif 15 line. A stopped line uses Unsure fg. The direction's "pencilled while running, inked when done" isn't built yet (see 8.3). |
| Progress bars | `.bars` (running), `.progress` (review) | 3–4 px tall: ink when done, Unsure when stopped |

### 5.12 Overlays

| Component | Class | Notes |
| --- | --- | --- |
| Dialog | `dialog` | A surface background, `--r-lg`, the dialog shadow, at most 560 px wide. It has a `.dialog-body` (24 px, gap 14) and a `.dialog-foot` (right-aligned, gap 8). |
| Wide dialog | `dialog.wide` | At most 860 px (rewrite, before and after) |
| Side panel | `dialog.panel` | Full height on the right, at most 480 px wide, square corners. Used for the detail panel and Suggestions. |
| Command palette | `dialog.palette` | 10vh from the top; a 48 px input, grouped results, and a shortcut on every row |
| Menu | `.menu` | A popover of at least 200 px, `--r-lg`, the menu shadow, 8 × 10 items |

### 5.13 Navigation

| Component | Class | Notes |
| --- | --- | --- |
| Sidebar | `.sidebar` | 232 px, sticky, on surface; ends in `.sidebar-foot` (privacy mode, credit) |
| Nav item | `.nav a` | A 16 px icon and the label. When current: sunken, 500, and a 3 px ink marker on the right. **The marker is never red.** |
| App bar | `.appbar` | 56 px, for flow screens: back, the title with a small subtitle, steps, search, actions |
| Steps | `.steps` | Numbered 18 px rings joined by 22 px hairlines. The current step is an ink disc with white text. |
| Flow footer | `.flow-foot` | Sticky at the bottom with the primary action ("Looks right, continue", "Send for review") |
| Page head | `.page-head` | The title and a muted line on the left, actions on the right |

### 5.14 Review-specific

| Component | Class | Notes |
| --- | --- | --- |
| Summary bar | `.summary` | A count for each level: a stamp, a bold number and a `?` |
| Thumbnails | `.thumbs` | A 96 px column of page thumbnails, with label dots |
| Label list | `.label-list` | 40 px rows: a pin, a mono §, and a description that truncates |
| Not-covered tick | `.label-list li.grey-confirm` | The tone row at the top of Not covered: "I've read the 35 not-covered parts" |
| Evidence trail | `.trail` | A 12 px ring "knot" plus a step: the thread, shown as a list |
| Decide buttons | `.decide` | Full-width option buttons, each with a `kbd` key hint |
| Diff | `.diff` | `del` struck through in `--text-2` (never red, ADR 0003), `ins` on the preferred bg (rewrite, before and after) |
| Fold | `details.more` | Folds the longer explanation |
| Contract link | `.contract-link` | A quiet underline that opens only after the link warning |

## 6. Patterns

**Flow screen.** New review, Contract check, Privacy check and Running use the same layout: an app bar with steps, then the work area on the left (`minmax(0,1fr)`), then a side margin of 340–400 px on surface with a left hairline, then a sticky flow footer.

**The margin.** The signature layout pattern is the margin beside the page (design direction, principle 3). The friend's notes, the reading log, the replacement list and the detail panel all sit in a right-hand surface column next to the paper. New screens should use it rather than inventing a new one.

**Detail panel order** (Spec 14.1, screen 8):

1. the quote, with the exact words highlighted;
2. the stamp and `?`;
3. why;
4. "why it could be the other level";
5. the level matched;
6. the evidence trail;
7. what to check;
8. "Looks right", "Change it", note.

**Empty state.** Say what it is, why it's empty and how to start, with real words. For example: "Check a contract against your playbook. It takes about 3 minutes…". Use one primary button and links for the rest.

**Errors.** Say what happened and why, then give the fix as a button. Use Unsure colours and say "Your files are safe" where that is true.

**Confirm deletion.** The title names the thing ("Delete 3 reviews?"). The body lists what goes and says it can't be undone. The button repeats the verb.

**Command palette.** Ctrl+K, or the "Search commands" box, opens it. It opens on the common commands, grouped, with a shortcut on each. Single keys (`data-key`, for example J for "Next unchecked") work only outside inputs.

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
- Tabs use `role="tablist"` with `aria-controls`.
- Segmented buttons use `aria-pressed`.
- Nav uses `aria-current="page"`.

**Screen readers.**

- Stamps carry their word as text.
- The `?` buttons have labels ("What Unsure means").
- Icon buttons have an `aria-label`.
- `.visually-hidden` is available for extra context.

**Text size.** In Settings, `data-text-set` scales the type to 100%, 125%, 150% or 200%.

## 8. Audit: where the prototype drifts

**Summary.** 17 screens, about 60 shared classes and 46 icons. 14 issues found, 4 fixed (7 Nov 2026). Score: 88 / 100. The tokens are well used in shared CSS. Most drift sits in page-local `<style>` blocks and inline styles.

### 8.1 Naming and duplication

| Issue | Where | Fix |
| --- | --- | --- |
| `.notice.warn` is defined three times, identically | new-review, running, privacy-check | Move it to `styles.css` |
| The flow layout (`.flow`, `.work`, `.side`/`.margin`) is redefined on each page | contract-check, running, privacy-check | One `.flow` / `.flow-work` / `.flow-margin` in `styles.css` |
| `.cl` (privacy, running) duplicates `.clause` (review) | 3 pages | One clause component with a dense modifier |
| `.thumbs` is redefined in privacy-check with a different thumbnail (`.thumb-img` vs `.t` vs `.thumb`) | review, privacy, new-review | One thumbnail component |
| The margin column is called `.side` on some pages and `.margin` on others | running vs others | Pick `.margin`, the design-direction word |

### 8.2 Tokens

| Issue | Where | Fix |
| --- | --- | --- |
| `--swap-bg/fg` are page-local | privacy-check | Move them to `:root` with the other mark tokens |
| Hardcoded hex: `#55524C` (= `--grey-fg`), `#6B665D`, `#D8D0C0`, `#bbb` ×20 (contract table borders), `#555` | running, privacy-check, review, index | Map to tokens. Contract-page greys can become `--sheet-line` and `--sheet-faint`. |
| `.key-form` uses a 10 px radius | index | `--r-lg` (two radii only) |
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
| The reading log isn't pencilled while running and inked when done | Design direction, principle 8 | Style running lines in `--pencil` and finished lines in `--text` |
| ✅ **Fixed.** The rewrite diff showed deleted words in walk-away red, which is decoration | ADR 0003 | Struck through in `--text-2` |
| 72 inline `style=` attributes in review.html (mostly `gap` and contract-table cells) | review.html | Fine for a prototype; don't carry them into the build |

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

## 9. Using the prototype

Serve it with the "prototype" launch config, or with:

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory prototype
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

`window.CT` exposes `toast()` and `applyTheme()`. `states.html` links every state in Spec 14.2 (40 links).

**Adding a component:**

1. Use existing tokens.
2. Put it in `styles.css`, not a page `<style>`.
3. Give it a colour, an icon and a word if it carries meaning.
4. Check it in greyscale and in dark mode.
5. Add a row to section 5.
