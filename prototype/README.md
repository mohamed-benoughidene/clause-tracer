# Clause Tracer prototype (HTML)

A clickable prototype of Clause Tracer version 1. It is plain, hand-written HTML, with one page per screen in the spec ([`docs/spec.md`](../docs/spec.md) §14.1). There's no build step and no framework.

## Run it

From the repo root:

```bash
python3 prototype/serve.py
```

Then open http://localhost:8767. In Claude Code the same server is the `prototype` entry in `.claude/launch.json`. You can also open the files straight from disk, but some browsers then forget the theme between pages.

- **`index.html`** is First launch, the app's first screen. Start here to use it like a new user.
- **`states.html`** is the prototype map. It has every flow and every state, one link each. Start here to review.
- **`review.html?sample`** is the practice review, with a planted wrong label on § 11.1.

## Related docs

- [`docs/design-system.md`](../docs/design-system.md): the tokens and components this folder uses, and an audit of where the pages still differ.
- [`docs/ux-copy.md`](../docs/ux-copy.md): the words for every screen.
- [`assets/`](../assets/): the logo master files.

This prototype replaces the FigCraft one (`Prototyping/clause-tracer/build/`), which is no longer built.

## Files

| File | What it is |
| --- | --- |
| `styles.css` | Design tokens (light and dark) and every shared component, including the window tabs, the folding sidebar, the Private mode switch, the flow stepper, the progress pie and the icon movements. The source of truth for how the app looks. |
| `app.js` | The shared behaviour: dialogs, menus, tabs, keys, toasts, theme, text size and the command palette (Ctrl+K). It also builds three shared parts, so a page carries no markup for them: the **window tabs** (Home, one tab per open review with its progress pie, “+”), the **Collapse menu** button of the sidebar (Ctrl+B), and the **flow stepper**'s motion. It runs the **Private mode switch** too. |
| `icons.js` | The icon sprite: 45 [Remix Icon](https://remixicon.com) 4.9.1 line icons and four hand-drawn ones (`approx`, `ring-dashed`, `thread`, `help`). Use `<svg class="icon"><use href="#i-NAME"/></svg>`. Take a new icon from Remix Icon, in its line style, and keep the four exceptions as they are ([design-system section 4](../docs/design-system.md#4-icons)). |
| `LICENSE-remixicon.txt` | The Remix Icon License v1.0. It covers the Remix paths in `icons.js`. The rest of the repository is under `LICENSE`. |
| `logo.svg`, `logo-dark.svg` | The logo for light and dark. Copies of the files in `assets/`. |
| `symbol.svg`, `symbol-dark.svg` | The butterfly symbol alone, for light and dark. Unchanged copies of `clause-tracer-symbol.svg` and `clause-tracer-symbol-reversed.svg` in `assets/`. Shown as the logo in the folded sidebar. |
| `serve.py` | The preview server. It sends `Cache-Control: no-store`, so the browser never shows an old stylesheet or script. |
| `hero-butterflies.webp` | The First launch picture. The full-size original is in `assets/`. |
| `home.html` | **The reference page.** Copy its head, sidebar and script tags. |

## Pages

| Page | Spec screen |
| --- | --- |
| `index.html` | 1 First launch: the picture, one paper card with two views (Welcome and Key, `?state=key`) |
| `home.html` | 2 Home |
| `new-review.html` | 3 New review |
| `contract-check.html` | 4 Contract check |
| `privacy-check.html` | 5 Privacy check |
| `running.html` | 6 Review running |
| `review.html` | 7 Review: the contract and one column. 8 Detail replaces the list in that column. 9 Change it and 10 Rewrite are dialogs, and 11 Suggestions is a side panel |
| `output.html` | 12 Output |
| `playbooks.html` | 13 Playbooks |
| `starter-preview.html` | 14 Starter preview |
| `import-preview.html` | 15 Import preview |
| `playbook-editor.html` | 16 Playbook editor |
| `customers.html` | 17 Customers |
| `settings.html` | 18 Settings |
| `help.html` | 19 Help |
| `error.html` | 20 Error |
| `states.html` | **Prototype map**: every flow to click through and every Spec §14.2 state, one link each. Start here to review. |

## Rules for writing a page

1. **Start from `home.html`.** Same `<head>` (fonts and `styles.css`), the same `<script src="icons.js">` then `<script src="app.js">` at the end of `<body>`.
   - Screens with the sidebar use `.app` > `aside.sidebar` + `main.main`. Mark the current nav link with `aria-current="page"`.
   - Flow screens (new review, the checks, running, review, output) have no sidebar. They use `header.appbar` and, where needed, `footer.flow-foot`.
2. **Semantic HTML.**
   - Use `button` for actions, `a href` for going to another page, `table` for lists of records, `dialog` for anything that opens over the page, and `label` with every input.
   - Every icon-only button gets an `aria-label`.
3. **Use the classes in `styles.css`; don't add a stylesheet.**
   - Components: `btn`, `btn-primary`, `card`, `notice`, `banner`, `stamp`, `pin`, `field`, `input`, `toggle`, `segmented`, `tabs`, `table`, `sheet`, `clause`, `menu`, `dialog`.
   - A few `style="…"` attributes for one-off spacing are fine. If you need a new reusable rule, add it at the end of `styles.css` under a comment with the page name.
4. **Behaviour comes from `app.js` data attributes**, not new scripts:
   - `data-open="dialog-id"` opens a dialog, and `data-close` closes it. A `<form method="dialog">` button closes it too.
   - `data-menu="menu-id"` toggles a `.menu`.
   - `data-key="J"` presses on a key.
   - `data-toast="Saved"` shows a toast.
   - `button.pm-switch[role="switch"][data-private-switch]` is the Private mode switch. Turning it on is one click. Turning it off opens `<dialog id="private-off">` first, if the page has one (its confirm button is `value="ok"`, and carries no `data-toast`: the switch toasts once). The choice is kept in `ct-private`. Only the privacy check has the switch. `running.html` shows the choice in words and uses `window.CT.isPrivate()` and `window.CT.setPrivate(on)`.
   - `ol.steps[data-step="n"]` is the flow stepper (new review, the checks, running). `app.js` plays its motion, and the forward button in `.flow-foot` plays a short leave.
   - `window.CT` and the `ct-progress` event: `review.html` dispatches `ct-progress` with `{id, checked, total}` and `app.js` updates the review's tab pie.
   - `role="tablist"` / `role="tab"` with `aria-controls` / `aria-selected` switches panels.
   - `.segmented > button[aria-pressed]` is a one-choice group.
   - `data-theme-set="light|dark|system"` switches the colours, and `data-text-set="125"` the text size (100, 125, 150 or 200). Both are remembered on every page.
   - Page scripts can call `window.CT.toast(text)` and `window.CT.applyTheme()`.
   - A page linked as `page.html#dialog-id` opens that dialog on load.

   A short inline `<script>` is fine only for something specific to the page.

   **Browser storage keys** (prototype only, in `localStorage` unless noted): `ct-theme`, `ct-text` (the settings), `ct-tabs` (the open reviews in the tab strip), `ct-progress` (each review's checked share), `ct-sidebar` (`collapsed` or `open`), `ct-private` (`on` or `off`) and, in `sessionStorage`, `ct-step` (the last step page).
5. **States** (Spec §14.2) live on their screen's page, switched by the URL:
   - Mark state-only markup with `data-state="name"`. It shows only on `page.html?state=name`.
   - Mark what the state replaces with `data-state-hide="name"`.
   - States that are a dialog are linked as `page.html#dialog-id`.
   - `review.html?sample` is the practice review, with the planted wrong label on § 11.1.
   - Add every new state to `states.html`.
   - Don't make a separate page per state.
6. **Labels.** A split stamp is written like this:

   ```html
   <span class="stamp walk"><span class="mark"><svg><use href="#i-x"/></svg></span><span class="word">Walk-away</span></span>
   ```

   - The kinds are `preferred` (icon `check`), `acceptable` (`approx`), `walk` (`x`), `unsure` (`help`) and `grey` for Not covered (`ring-dashed`).
   - Add the `pencilled` class when the app judged the label from the wording. Only pencilled stamps are dashed (ADR 0002).
   - Not covered clauses are never marked on the page.
   - Pins are `<span class="pin walk">4</span>`.
   - Red is only for walk-away.
7. **Copy.** Use the words in [`docs/ux-copy.md`](../docs/ux-copy.md), in British English. If a page and the copy deck disagree, fix both. The voice is plain and neutral: the app never says "I" ("This one is a walk-away"). "I" and "my" belong only to the user's own words, such as position names and notes (Spec 14.4).
   - Every on-screen string must match the deck. `python scripts/copy_lint.py` checks it, and `scripts/check.sh` runs it. A voice or look failure stops the check. Fix the page and the deck together, or add a reasoned line to `scripts/copy_lint_allow.txt`.
8. **Link every control** to the page or dialog it goes to. Nothing should look clickable and do nothing.
