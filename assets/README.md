# Assets

The Clause Tracer logo master files and the original First launch picture. Use these files whenever you need the logo outside the prototype: the app icon, the website, documents or slides.

**Which file do I need?**

- On a light background: `clause-tracer-logo.svg`.
- On a dark background: `clause-tracer-logo-reversed.svg`.
- For the app icon or a favicon: `clause-tracer-symbol.svg`.
- Where you can only use one colour (a fax, a stamp, an embossed print): the `-mono` file.

Use the SVG wherever you can. The PNGs are for tools that can't take SVG.

## Files

There are two shapes, each in four colour versions. Every file comes as an SVG and as a PNG.

| Version | Logo (1415 × 256) | Symbol (256 × 256) | Use it on |
| --- | --- | --- | --- |
| Standard | `clause-tracer-logo` | `clause-tracer-symbol` | Light backgrounds. Ink name and eyespots, oxblood line. |
| Reversed | `clause-tracer-logo-reversed` | `clause-tracer-symbol-reversed` | Dark backgrounds. Light name and eyespots, oxblood line, no background. |
| On dark | `clause-tracer-logo-on-dark` | `clause-tracer-symbol-on-dark` | Places that need the dark background built in, such as a social card or an app tile. |
| Mono | `clause-tracer-logo-mono` | `clause-tracer-symbol-mono` | One-colour printing. Everything in ink `#1F2328`. |

- The **logo** is the butterfly followed by the name.
- The **symbol** is the butterfly by itself, used as the app icon and the favicon.

| Other file | What it is |
| --- | --- |
| `Red-Eyed Butterfly Engraving Collage.png` | The full-size original of the First launch picture (1535 × 1024): a page of etched butterflies, with one red one. |
| `hero-butterflies.webp` | The compressed copy of that picture used in the app (360 KB). The prototype has the same file at `prototype/hero-butterflies.webp`. |

## Colours

| Name | Hex | Used for |
| --- | --- | --- |
| Oxblood | `#A91207` | The butterfly's line, and the one eyespot that matters |
| Ink | `#1F2328` | The name and the other three eyespots |
| Light | `#ECE8E1` | The name and eyespots on dark |
| Dark | `#1E1D1A` | The background of the on-dark files |

## Rules

- **Minimum size:** 120 px (30 mm) wide for the logo, and 16 px (5 mm) for the symbol.
- **Clear space:** leave at least one cap height empty on every side.
- **Don't:**
  - recolour the name red;
  - move the butterfly between the words or after the name;
  - outline the logo or give it a shadow;
  - redraw the line or add a fifth eyespot;
  - repeat the mark as a pattern.

The full rules and the reasons behind them are in the [logo guide](../docs/clause-tracer-logo-guide.pdf) and the [brand philosophy](../docs/clause-tracer-brand-philosophy.md).

## Where the files come from

- The artwork was drawn in vectorcraft.
- The name is IBM Plex Serif SemiBold converted to outlines, so you don't need the font to show the logo.
- The build scripts are kept outside this repo, in `Prototyping/logo/final/`. To change the logo, rebuild it there and copy the results here.
- The prototype has its own copies, `prototype/logo.svg` and `logo-dark.svg`. They are set up for the light and dark theme switch. If you change the logo, update those copies too.
