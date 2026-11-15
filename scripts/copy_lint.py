#!/usr/bin/env python3
"""Lint the fixed copy and the look of the Clause Tracer prototype.

Run from the repo root: ``python scripts/copy_lint.py`` (or through ``uv run``).

It reads three things and checks them against the voice and design rules:

1. the on-screen strings of ``docs/ux-copy.md`` (the "Copy" cells in section 4);
2. the visible text of every ``prototype/*.html``;
3. the CSS of ``prototype/styles.css``, every ``<style>`` block and every ``style=`` attribute.

Each finding prints as ``FAIL|WARN  file:line  code  message``. Exit code 1 when any FAIL exists.
Standard library only. No network, no AI.

Constitution T1 and T2: every parser and every check is a pure function (text in, findings out).
Only ``main()`` reads files and prints.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK_PATH = "docs/ux-copy.md"
ALLOW_PATH = "scripts/copy_lint_allow.txt"
STYLES_PATH = "prototype/styles.css"
PROTOTYPE_DIR = "prototype"

FAIL = "FAIL"
WARN = "WARN"

# ---------------------------------------------------------------------------------------------
# Constants: every list a person may need to edit lives here.
# ---------------------------------------------------------------------------------------------

# Contract sample text is prototype data, not copy (Spec 14.5). Elements with one of these classes
# are skipped, with everything inside them: `.sheet` is the typeset contract page, `.doc` is the
# running page's wrapper around it, `.map` is the list of state links on states.html.
SKIP_CLASSES = frozenset({"sheet", "doc", "map"})

# Never copy: their text is not on screen.
SKIP_TAGS = frozenset({"script", "style", "svg", "template"})

# Attributes whose value a person or a screen reader sees.
COPY_ATTRS = ("aria-label", "title", "placeholder", "alt", "data-toast")

# Elements that do not close, so they never hold text.
VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "wbr"}
)

# Inline tags join into the text of their parent block; any other tag starts a new string.
INLINE_TAGS = frozenset(
    {
        "a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "del", "dfn", "em", "i", "ins",
        "kbd", "mark", "q", "s", "samp", "small", "span", "strong", "sub", "sup", "time", "u",
        "var",
    }
)  # fmt: skip

BANNED_WORDS = (
    "please", "simply", "oops", "sorry", "seamless", "seamlessly", "powerful", "effortless",
    "effortlessly", "leverage", "delve", "robust", "unlock",
)  # fmt: skip
BANNED_PHRASES = ("something went wrong",)
SOFT_WORDS = ("just", "easily", "very", "really")
US_SPELLINGS = (
    "color", "colors", "summarize", "summarized", "recognize", "organize", "labeled", "labeling",
    "favorite", "center",
)  # fmt: skip

# Key names that may follow "press" in a key hint ("press Esc"). A control name may not.
KEY_NAMES = frozenset({"Esc", "Escape", "Enter", "Return", "Tab", "Ctrl", "Shift", "Alt", "Space"})

# Link text that tells a screen reader the link leaves the app (ux-copy section 3, "Link out").
LINK_OUT_PHRASES = ("(opens in your browser)", "(opens the release page in your browser)")

MAX_TOAST_WORDS = 5
MAX_SENTENCE_WORDS = 25
REPEATED_NUMBER_LIMIT = 3

# The words "red" tokens are made of: oxblood and its tints, in light and dark (styles.css `:root`).
OXBLOOD_HEX = ("A91207", "8E0F06", "F8E3E1", "E0523F", "3A1512", "D23A2C", "FF9A8F")

# Selectors where red is allowed (ADR 0003, design-system rule 3). Built from styles.css:
# `:root` and `:root[data-theme="dark"]` define the tokens, every walk-away component carries a
# `.walk` class (`.stamp.walk`, `.pin.walk`, `.clause.walk`, `.quote.walk`), the logo is an image.
RED_ALLOWED_SELECTORS = (r"^:root\b", r"\.walk\b", r"\blogo\b")

# Radii the design system names (design-system 3.7): --r, --r-lg, the 3 px stamp, 50% circles,
# and 0. 2 px is the hairline rounding of thumbnails and bars. 100 px and up is full rounding.
ALLOWED_RADII = frozenset(
    {"0", "0px", "2px", "3px", "4px", "8px", "50%", "inherit", "initial", "unset", "var(--r)",
     "var(--r-lg)"}
)  # fmt: skip
FULL_ROUND_RE = re.compile(r"^\d{3,}px$")

EFFECT_VALUE_PATTERNS = ("linear-gradient(", "radial-gradient(", "conic-gradient(", "blur(")
EFFECT_PROPS = ("backdrop-filter", "animation", "animation-name")

# Deck rows whose first cell starts with this are notes for the maintainer, not copy.
DECK_SKIP_FIRST_CELL = "maintainer note"

# A parenthetical in a deck cell with this many words or more is a note to the maintainer.
DECK_NOTE_MIN_WORDS = 3
DECK_NOTE_KEEP_PREFIXES = ("opens",)  # "(opens in your browser)" is copy

# Single digits are list numbers and keys, not facts, so the repeated-number check ignores them.
NUMBER_RE = re.compile(r"\$?\d[\d.,]*%?")

EMOJI_RE = re.compile(
    "[\U0001f000-\U0001faff\u2600-\u27bf\u2b50\u2b55\u2b1b\u2b1c\u231a\u231b\u23e9-\u23f3"
    "\u23f8-\u23fa\u203c\u2049\ufe0f\u200d]"
)

WILD = "\x00"

# ---------------------------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    severity: str
    file: str
    line: int
    code: str
    message: str
    match: str = ""  # the offending word, for the allow-list
    context: str = ""  # the whole string it came from, for the allow-list


@dataclass(frozen=True)
class Unit:
    """One string of copy: a sentence, a button label, an attribute value, a deck cell part."""

    file: str
    line: int
    text: str
    source: str  # "deck" or "page"
    scope: str = ""  # a deck row or a prototype dialog, for the repeated-number check
    is_toast: bool = False
    page: str = ""  # the prototype file a deck string belongs to


@dataclass(frozen=True)
class Anchor:
    file: str
    line: int
    href: str
    target: str
    text: str


@dataclass(frozen=True)
class Decl:
    """One CSS declaration, or an at-rule header (prop starts with "@")."""

    file: str
    line: int
    selectors: tuple[str, ...]
    prop: str
    value: str

    @property
    def selector(self) -> str:
        plain = [s for s in self.selectors if not s.startswith("@")]
        return plain[-1] if plain else ""


@dataclass(frozen=True)
class ParsedPage:
    units: list[Unit]
    anchors: list[Anchor]
    css: list[Decl]


@dataclass(frozen=True)
class AllowEntry:
    line: int
    code: str
    file: str
    pattern: str
    reason: str
    is_regex: bool


# ---------------------------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------------------------


def fold(text: str) -> str:
    """Case-folded text with curly quotes made straight, for comparing strings."""
    swaps = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'}
    return re.sub(r"\s+", " ", "".join(swaps.get(c, c) for c in text)).strip().casefold()


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def glued(before: str, after: str) -> bool:
    """True when two pieces of text touch with no space where a reader would see one."""
    if not before or not after or before[-1].isspace() or after[0].isspace():
        return False
    ends_word = before[-1].isalnum()
    ends_sentence = before[-1] in ".!?:;"
    starts_word = after[0].isalnum()
    lower_to_lower = before[-1].islower() and after[0].islower()
    return starts_word and (ends_sentence or (ends_word and not lower_to_lower))


def count_words(text: str) -> int:
    return sum(1 for token in text.split() if re.search(r"\w", token))


def whole_word(words: Iterable[str]) -> re.Pattern[str]:
    body = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
    return re.compile(rf"(?<![\w'\u2019-])(?:{body})(?![\w'\u2019-])", re.IGNORECASE)


def split_top_level(text: str, sep: str) -> list[str]:
    """Split on `sep` outside parentheses and quotes."""
    parts: list[str] = []
    depth = 0
    quote = ""
    start = 0
    for i, ch in enumerate(text):
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == sep and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return parts


# ---------------------------------------------------------------------------------------------
# The deck
# ---------------------------------------------------------------------------------------------


def _table_cells(line: str) -> list[str]:
    inner = line.strip()
    inner = inner.removeprefix("|").removesuffix("|")
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", inner)]


def _is_separator(cells: Sequence[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c) and any(cells)


def parse_not_terms(deck: str) -> list[str]:
    """The terms of the "Not" column in section 2 (the word list), lower-case and split."""
    terms: list[str] = []
    in_list = False
    not_index: int | None = None
    for raw in deck.splitlines():
        if raw.startswith("## "):
            in_list = raw.startswith("## 2.")
            not_index = None
            continue
        if not in_list or not raw.lstrip().startswith("|"):
            continue
        cells = _table_cells(raw)
        if not_index is None:
            lowered = [c.casefold() for c in cells]
            if "not" in lowered:
                not_index = lowered.index("not")
            continue
        if _is_separator(cells) or not_index >= len(cells):
            continue
        for chunk in re.split(r",", cells[not_index]):
            for term in chunk.split(" / "):
                clean = fold(term.replace("`", "")).strip(" .")
                if clean and clean not in terms:
                    terms.append(clean)
    return terms


def clean_deck_cell(cell: str) -> str:
    """Remove what is not on screen: code spans, bold marks and notes in long parentheses."""
    text = re.sub(r"`[^`]*`", "", cell).replace("**", "").replace("\\|", "|")

    def drop_note(match: re.Match[str]) -> str:
        inner = match.group(1)
        long_enough = count_words(inner) >= DECK_NOTE_MIN_WORDS
        keeps = inner.casefold().startswith(DECK_NOTE_KEEP_PREFIXES)
        return "" if long_enough and not keeps else match.group(0)

    return re.sub(r"\(([^()]*)\)", drop_note, text)


_TOAST_MARK = re.compile(r"^toasts?:\s*", re.IGNORECASE)
_OTHER_MARK = re.compile(
    r"^(?:log|footer|columns?|rows?|placeholder|menu|after [\w ]+|leave dialog text|dialog|notice|"
    r"name placeholder|side placeholder|topic placeholder|note placeholder|path line):\s*",
    re.IGNORECASE,
)


def deck_units(cell: str, first_cell: str) -> list[tuple[str, bool]]:
    """Split a deck cell into strings. Returns (text, is_toast) pairs."""
    text = clean_deck_cell(cell)
    toast_mode = "toast" in first_cell.casefold()
    out: list[tuple[str, bool]] = []
    for part in text.split(" \u00b7 "):
        piece = collapse(part)
        if _TOAST_MARK.match(piece):
            toast_mode = True
            piece = _TOAST_MARK.sub("", piece)
        elif _OTHER_MARK.match(piece):
            toast_mode = False
        # a note wrapped in whole parentheses is not copy
        if not piece or (piece.startswith("(") and piece.endswith(")")):
            continue
        out.append((piece, toast_mode))
    return out


@dataclass(frozen=True)
class DeckRow:
    line: int
    page: str
    first_cell: str
    units: list[tuple[str, bool]]
    raw_cell: str


def parse_deck(deck: str) -> list[DeckRow]:
    """The "Copy" cells of the section 4 tables, one DeckRow per table row."""
    rows: list[DeckRow] = []
    in_screens = False
    page = ""
    copy_index: int | None = None
    in_table = False
    for number, raw in enumerate(deck.splitlines(), start=1):
        if raw.startswith("## "):
            in_screens = raw.startswith("## 4.")
            page = ""
            in_table = False
            continue
        if not in_screens:
            continue
        if raw.startswith("### "):
            found = re.search(r"\(`([\w-]+\.html)`", raw)
            page = found.group(1) if found else ""
            in_table = False
            continue
        if not raw.lstrip().startswith("|"):
            in_table = False
            continue
        cells = _table_cells(raw)
        if not in_table:
            lowered = [c.casefold() for c in cells]
            copy_index = lowered.index("copy") if "copy" in lowered else None
            in_table = True
            continue
        if copy_index is None or _is_separator(cells) or copy_index >= len(cells):
            continue
        first = cells[0].replace("**", "")
        if first.casefold().startswith(DECK_SKIP_FIRST_CELL):
            continue
        rows.append(
            DeckRow(number, page, first, deck_units(cells[copy_index], first), cells[copy_index])
        )
    return rows


def deck_to_units(rows: Sequence[DeckRow]) -> list[Unit]:
    units: list[Unit] = []
    for row in rows:
        for text, is_toast in row.units:
            units.append(
                Unit(DECK_PATH, row.line, text, "deck", f"deck:{row.line}", is_toast, row.page)
            )
    return units


# ---------------------------------------------------------------------------------------------
# The prototype pages
# ---------------------------------------------------------------------------------------------


@dataclass
class _Frame:
    tag: str
    skip: bool
    scope: str


@dataclass
class _AnchorDraft:
    line: int
    href: str
    target: str
    parts: list[str]
    skip: bool = False


class _PageParser(HTMLParser):
    def __init__(self, file: str) -> None:
        super().__init__(convert_charrefs=True)
        self.file = file
        self.units: list[Unit] = []
        self.anchors: list[Anchor] = []
        self.css: list[Decl] = []
        self._stack: list[_Frame] = []
        self._buf: list[tuple[str, int]] = []
        self._open_anchors: list[_AnchorDraft] = []
        self._style_buf: list[str] = []
        self._style_line = 1
        self._dialogs = 0

    # -- helpers
    def _skipping(self) -> bool:
        return bool(self._stack and self._stack[-1].skip)

    def _scope(self) -> str:
        return self._stack[-1].scope if self._stack else ""

    def _flush(self) -> None:
        if not self._buf:
            return
        text = collapse("".join(piece for piece, _ in self._buf))
        line = self._buf[0][1]
        self._buf = []
        if text:
            self.units.append(Unit(self.file, line, text, "page", self._scope()))

    def _emit_attr(self, name: str, value: str, line: int, scope: str) -> None:
        text = collapse(value)
        if text:
            self.units.append(
                Unit(self.file, line, text, "page", scope, is_toast=name == "data-toast")
            )

    # -- parser callbacks
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        attr = {k: (v or "") for k, v in attrs}
        classes = set(attr.get("class", "").split())
        parent_skip = self._skipping()
        if tag not in INLINE_TAGS:
            self._flush()
        scope = self._scope()
        if tag == "dialog":
            self._dialogs += 1
            scope = f"{self.file}:dialog{self._dialogs}"
        skip = parent_skip or tag in SKIP_TAGS or bool(classes & SKIP_CLASSES)
        if not parent_skip and tag not in SKIP_TAGS:
            for name in COPY_ATTRS:
                if name in attr:
                    self._emit_attr(name, attr[name], line, scope)
            is_button = tag == "button" or (
                tag == "input" and attr.get("type") in {"button", "submit", "reset"}
            )
            if is_button and "value" in attr:
                self._emit_attr("value", attr["value"], line, scope)
        if "style" in attr:
            hint = tag + "".join(f".{c}" for c in sorted(classes))
            self.css.extend(parse_css(attr["style"], self.file, line, (hint,)))
        if tag == "a":
            label = attr.get("aria-label", "")
            draft = _AnchorDraft(
                line, attr.get("href", ""), attr.get("target", ""), [label], parent_skip or skip
            )
            self._open_anchors.append(draft)
        if tag in VOID_TAGS:
            if tag == "br":
                self._flush()
            return
        self._stack.append(_Frame(tag, skip, scope))
        if tag == "style":
            self._style_buf = []
            self._style_line = line

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if tag not in INLINE_TAGS:
            self._flush()
        names = [f.tag for f in self._stack]
        if tag not in names:
            return
        while self._stack:
            frame = self._stack.pop()
            if frame.tag == tag:
                break
        if tag == "style":
            self.css.extend(parse_css("".join(self._style_buf), self.file, self._style_line))
            self._style_buf = []
        if tag == "a" and self._open_anchors:
            draft = self._open_anchors.pop()
            if draft.skip:
                return
            self.anchors.append(
                Anchor(
                    self.file, draft.line, draft.href, draft.target, collapse("".join(draft.parts))
                )
            )

    def handle_data(self, data: str) -> None:
        top = self._stack[-1].tag if self._stack else ""
        if top == "style":
            self._style_buf.append(data)
            return
        if self._skipping() or top == "script":
            return
        for draft in self._open_anchors:
            draft.parts.append(data)
        stripped = data.lstrip()
        if not stripped:
            if self._buf:
                self._buf.append((" ", self._buf[-1][1]))
            return
        offset = len(data) - len(stripped)
        line = self.getpos()[0] + data[:offset].count("\n")
        if not self._buf:
            self._buf.append((stripped, line))
            return
        # Elements that are side by side in the HTML but drawn on separate lines run together
        # ("dateWhy", "review.Show"). Put a space back where a word or a sentence ended.
        before = "".join(piece for piece, _ in self._buf)
        if glued(before, data):
            self._buf.append((" ", line))
        self._buf.append((data, line))

    def finish(self) -> ParsedPage:
        self.close()
        self._flush()
        return ParsedPage(self.units, self.anchors, self.css)


def parse_page(html: str, file: str) -> ParsedPage:
    """Visible text, links and CSS of one prototype page."""
    parser = _PageParser(file)
    parser.feed(html)
    return parser.finish()


# ---------------------------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------------------------


def _blank_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.DOTALL)


def parse_css(css: str, file: str, first_line: int = 1, base: tuple[str, ...] = ()) -> list[Decl]:
    """Declarations of a stylesheet, with nesting and at-rules. `base` holds enclosing selectors."""
    text = _blank_comments(css)
    decls: list[Decl] = []
    stack: list[str] = []
    buf: list[str] = []
    buf_line = first_line
    started = False  # the buffer holds something other than white space
    line = first_line
    paren = 0
    quote = ""

    def chain() -> tuple[str, ...]:
        return base + tuple(stack)

    def flush_decl() -> None:
        nonlocal started
        body = "".join(buf).strip()
        if body and ":" in body and (stack or base):
            prop, _, value = body.partition(":")
            decls.append(Decl(file, buf_line, chain(), prop.strip().lower(), value.strip()))
        buf.clear()
        started = False

    for i, ch in enumerate(text):
        if not started and not ch.isspace():
            buf_line = line
            started = True
        if quote:
            buf.append(ch)
            if ch == quote and text[i - 1] != "\\":
                quote = ""
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == "(":
            paren += 1
            buf.append(ch)
        elif ch == ")":
            paren = max(0, paren - 1)
            buf.append(ch)
        elif paren == 0 and ch == "{":
            prelude = collapse("".join(buf))
            if prelude.startswith("@"):
                name, _, rest = prelude.partition(" ")
                decls.append(Decl(file, buf_line, chain() + (prelude,), name.lower(), rest))
            stack.append(prelude)
            buf.clear()
            started = False
        elif paren == 0 and ch == ";":
            flush_decl()
        elif paren == 0 and ch == "}":
            flush_decl()
            if stack:
                stack.pop()
        else:
            buf.append(ch)
        if ch == "\n":
            line += 1
    flush_decl()
    return decls


# ---------------------------------------------------------------------------------------------
# Checks on copy
# ---------------------------------------------------------------------------------------------

CLIENT_RE = re.compile(r"\bclients?\b", re.IGNORECASE)
OPEN_SOURCE_RE = re.compile(r"\bopen[- ]source\b", re.IGNORECASE)
NEW_TAB_RE = re.compile(r"\(opens in a new tab\)|\bnew tab\b", re.IGNORECASE)
BANNED_RE = whole_word(BANNED_WORDS)
BANNED_PHRASE_RE = re.compile("|".join(re.escape(p) for p in BANNED_PHRASES), re.IGNORECASE)
SOFT_RE = whole_word(SOFT_WORDS)
US_RE = whole_word(US_SPELLINGS)
LICENSE_RE = re.compile(r"(?<!Source )(?<!Apache )(?<![\w_])[Ll]icense(?![\w_])")
FIRST_PERSON_RE = re.compile(
    r"(?<![\w'\u2019-])(?:I(?:['\u2019](?:m|ve|d|ll))?|(?i:my|me|myself))(?![\w'\u2019-])"
)
TAP_RE = re.compile(r"\btap\b", re.IGNORECASE)
PRESS_RE = re.compile(r"(?i:\bpress\b)\s+([A-Z][a-z]\w*)")


def _finding(unit: Unit, code: str, message: str, match: str, severity: str = FAIL) -> Finding:
    return Finding(severity, unit.file, unit.line, code, message, match, unit.text)


def term_regex(term: str) -> re.Pattern[str]:
    words = r"\s+".join(re.escape(w) for w in term.split())
    return re.compile(rf"(?<![\w'\u2019-]){words}s?(?![\w'\u2019-])", re.IGNORECASE)


def check_unit(unit: Unit, not_terms: Sequence[str] = ()) -> list[Finding]:
    """Every per-string check. Pure: the string in, findings out."""
    text = unit.text
    found: list[Finding] = []

    def hits(pattern: re.Pattern[str], code: str, message: str, severity: str = FAIL) -> None:
        for m in pattern.finditer(text):
            found.append(_finding(unit, code, message.format(m.group(0)), m.group(0), severity))

    hits(CLIENT_RE, "client", "'{}': the deck says customer, the other side or your party")
    hits(OPEN_SOURCE_RE, "open-source", "'{}': say source available")
    hits(
        NEW_TAB_RE, "new-tab", "'{}': it is a desktop app with no tabs; say (opens in your browser)"
    )
    for m in re.finditer("!", text):
        found.append(_finding(unit, "exclamation", "exclamation mark", m.group(0)))
    hits(BANNED_RE, "banned-word", "'{}' is a softener, a cheer or a filler word")
    hits(BANNED_PHRASE_RE, "banned-word", "'{}' says nothing; say what happened and the fix")
    for term in not_terms:
        for m in term_regex(term).finditer(text):
            found.append(
                _finding(
                    unit,
                    "not-column",
                    f"'{m.group(0)}' is in the Not column; use the word list",
                    term,
                )
            )
    hits(
        FIRST_PERSON_RE, "first-person", "'{}': the app never says I; only the user's own words do"
    )
    hits(TAP_RE, "tap-press", "'{}': say click")
    for m in PRESS_RE.finditer(text):
        if m.group(1) not in KEY_NAMES:
            found.append(_finding(unit, "tap-press", f"'{m.group(0)}': say click", m.group(0)))
    hits(US_RE, "us-spelling", "'{}': write British English")
    hits(
        LICENSE_RE,
        "us-spelling",
        "'{}': the noun is licence (the Functional Source License keeps its name)",
    )
    for m in EMOJI_RE.finditer(text):
        found.append(_finding(unit, "emoji", f"emoji U+{ord(m.group(0)):04X}", m.group(0)))
    if unit.is_toast and count_words(text) > MAX_TOAST_WORDS:
        found.append(
            _finding(
                unit,
                "toast-length",
                f"toast has {count_words(text)} words; the limit is {MAX_TOAST_WORDS}",
                text,
            )
        )
    # soft signs
    hits(SOFT_RE, "soft-word", "'{}' may be a filler", WARN)
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z\u201c\"(\[])", text):
        if count_words(sentence) > MAX_SENTENCE_WORDS:
            found.append(
                _finding(
                    unit,
                    "long-sentence",
                    f"sentence of {count_words(sentence)} words; the limit is {MAX_SENTENCE_WORDS}",
                    sentence[:40],
                    WARN,
                )
            )
    return found


def check_units(units: Sequence[Unit], not_terms: Sequence[str] = ()) -> list[Finding]:
    found: list[Finding] = []
    for unit in units:
        found.extend(check_unit(unit, not_terms))
    found.extend(check_repeated_numbers(units))
    return found


def check_repeated_numbers(units: Sequence[Unit]) -> list[Finding]:
    """The same number three or more times in one deck row or one prototype dialog."""
    groups: dict[str, list[Unit]] = defaultdict(list)
    for unit in units:
        if unit.scope:
            groups[unit.scope].append(unit)
    found: list[Finding] = []
    for members in groups.values():
        counts: Counter[str] = Counter()
        for unit in members:
            for number in NUMBER_RE.findall(unit.text):
                token = number.rstrip(".,")
                if re.fullmatch(r"\d", token):
                    continue
                counts[token] += 1
        for token, n in sorted(counts.items()):
            if n >= REPEATED_NUMBER_LIMIT:
                first = members[0]
                found.append(
                    Finding(
                        WARN,
                        first.file,
                        first.line,
                        "repeated-number",
                        f"'{token}' appears {n} times in one {_scope_name(first)}",
                        token,
                        first.text,
                    )
                )
    return found


def _scope_name(unit: Unit) -> str:
    return "deck row" if unit.source == "deck" else "dialog"


def check_straight_quotes(rows: Sequence[DeckRow]) -> list[Finding]:
    found: list[Finding] = []
    for row in rows:
        cleaned = clean_deck_cell(row.raw_cell)
        if '"' in cleaned:
            found.append(
                Finding(
                    WARN,
                    DECK_PATH,
                    row.line,
                    "straight-quote",
                    "straight double quote in copy; use \u201c \u201d",
                    '"',
                    collapse(cleaned),
                )
            )
    return found


def check_anchors(anchors: Sequence[Anchor]) -> list[Finding]:
    found: list[Finding] = []
    for a in anchors:
        leaves = a.target == "_blank" or a.href.startswith("http")
        if leaves and not any(p in a.text for p in LINK_OUT_PHRASES):
            found.append(
                Finding(
                    FAIL,
                    a.file,
                    a.line,
                    "link-out",
                    f"link to {a.href or 'a new window'} has no '(opens in your browser)' text",
                    a.href,
                    a.text,
                )
            )
    return found


# ---------------------------------------------------------------------------------------------
# Checks on CSS
# ---------------------------------------------------------------------------------------------


def _css_finding(d: Decl, code: str, message: str, match: str) -> Finding:
    return Finding(
        FAIL, d.file, d.line, code, message, match, f"{d.selector} {{ {d.prop}: {d.value} }}"
    )


def _selector_parts(selector: str) -> list[str]:
    return [p.strip() for p in split_top_level(selector, ",") if p.strip()]


def red_allowed(selector: str) -> bool:
    parts = _selector_parts(selector)
    return bool(parts) and all(
        any(re.search(pattern, part) for pattern in RED_ALLOWED_SELECTORS) for part in parts
    )


_RED_VALUE_RE = re.compile(
    r"var\(\s*--(?:red|walk)[\w-]*|#(?:" + "|".join(OXBLOOD_HEX) + r")\b", re.IGNORECASE
)
_RADIUS_PROP_RE = re.compile(r"^border(-[a-z]+)*-radius$")


def check_decl(d: Decl) -> list[Finding]:
    found: list[Finding] = []
    # red
    red_in_value = _RED_VALUE_RE.search(d.value)
    red_in_prop = re.match(r"--(?:red|walk)", d.prop)
    if (red_in_value or red_in_prop) and d.selector and not red_allowed(d.selector):
        token = red_in_value.group(0) if red_in_value else d.prop
        found.append(
            _css_finding(
                d,
                "red-outside-walk",
                f"{token} used in '{d.selector}', which is not the walk-away label or the logo",
                token,
            )
        )
    # effects
    lowered = d.value.casefold()
    for pattern in EFFECT_VALUE_PATTERNS:
        if pattern in lowered:
            found.append(_css_finding(d, "effect", f"'{pattern}' in '{d.selector}'", pattern))
    if d.prop in EFFECT_PROPS:
        found.append(_css_finding(d, "effect", f"'{d.prop}' in '{d.selector}'", d.prop))
    if d.prop == "@keyframes":
        found.append(_css_finding(d, "effect", f"@keyframes {d.value}", "@keyframes"))
    # radius
    if _RADIUS_PROP_RE.match(d.prop):
        for token in re.findall(r"var\([^)]*\)|[^\s/]+", d.value):
            plain = token.replace(" ", "")
            if plain not in ALLOWED_RADII and not FULL_ROUND_RE.match(plain):
                found.append(
                    _css_finding(
                        d,
                        "radius",
                        f"{d.prop}: {token} in '{d.selector}'; use var(--r) or var(--r-lg)",
                        token,
                    )
                )
    # emoji in generated content
    for m in EMOJI_RE.finditer(d.value):
        found.append(_css_finding(d, "emoji", f"emoji U+{ord(m.group(0)):04X} in CSS", m.group(0)))
    return found


def check_css(decls: Sequence[Decl]) -> list[Finding]:
    found: list[Finding] = []
    for d in decls:
        found.extend(check_decl(d))
    return found


# ---------------------------------------------------------------------------------------------
# Deck and prototype mismatch (warns only, for now)
# ---------------------------------------------------------------------------------------------


def normalise(text: str, *, deck: bool = False) -> str:
    """Lower-case, quotes straight, spaces collapsed, ends stripped of punctuation.

    Digits become a wildcard. On the deck side a lower-case bracket ("[n]", "[name]") is a
    placeholder and becomes a wildcard too; a capitalised bracket ("[Save key]") is a button,
    and keeps its words.
    """
    out = text
    if deck:

        def bracket(m: re.Match[str]) -> str:
            inner = m.group(1)
            return inner if inner[:1].isupper() else WILD

        out = re.sub(r"\[([^\]]*)\]", bracket, out)
    out = fold(out)
    out = re.sub(r"\d+(?:[.,]\d+)*", WILD, out)
    out = re.sub(rf"{WILD}(?:\s*{WILD})+", WILD, out)
    return out.strip(" .,;:!?\u2026\"'()-\u2013\u2014\u00b7").strip()


def _to_regex(norm: str) -> re.Pattern[str]:
    return re.compile(".*?".join(re.escape(p) for p in norm.split(WILD)), re.DOTALL)


def strings_match(deck_norm: str, page_norm: str) -> bool:
    """A deck string and a page string match when one holds the other (placeholders are wild)."""
    if not deck_norm or not page_norm:
        return False
    if _to_regex(deck_norm).fullmatch(page_norm):
        return True
    if _to_regex(deck_norm).search(page_norm):
        return True
    return bool(_to_regex(page_norm).search(deck_norm.replace(WILD, "0")))


def _fragments(text: str) -> list[str]:
    parts = [text]
    if " / " in text:
        parts.extend(p for p in text.split(" / ") if p.strip())
    return parts


def check_mismatch(deck_units_: Sequence[Unit], page_units: Sequence[Unit]) -> list[Finding]:
    """Page strings with no deck match, and deck strings with no page match (3 words or more)."""
    deck_by_page: dict[str, list[Unit]] = defaultdict(list)
    everywhere: list[Unit] = []
    for unit in deck_units_:
        if unit.page:
            deck_by_page[unit.page].append(unit)
        else:
            everywhere.append(unit)
    pages_by_file: dict[str, list[Unit]] = defaultdict(list)
    for unit in page_units:
        pages_by_file[unit.file.rsplit("/", 1)[-1]].append(unit)

    def norms(units: Iterable[Unit], *, deck: bool) -> list[str]:
        result: list[str] = []
        for u in units:
            for piece in _fragments(u.text):
                n = normalise(piece, deck=deck)
                if n:
                    result.append(n)
        return result

    found: list[Finding] = []
    global_norms = norms(everywhere, deck=True)
    for name, units in sorted(pages_by_file.items()):
        deck_norms = norms(deck_by_page.get(name, ()), deck=True) + global_norms
        for unit in units:
            if count_words(unit.text) < 3:
                continue
            pn = normalise(unit.text)
            if not any(strings_match(d, pn) for d in deck_norms):
                found.append(
                    Finding(
                        WARN,
                        unit.file,
                        unit.line,
                        "deck-prototype-mismatch",
                        f"[{name}] no matching string in {DECK_PATH}: {unit.text[:90]}",
                        unit.text,
                        unit.text,
                    )
                )
    for name, units in sorted(deck_by_page.items()):
        if name not in pages_by_file:
            continue
        page_norms = [normalise(u.text) for u in pages_by_file[name]]
        for unit in units:
            if count_words(unit.text) < 3:
                continue
            candidates = [normalise(p, deck=True) for p in _fragments(unit.text)]
            if not any(strings_match(c, pn) for c in candidates for pn in page_norms):
                found.append(
                    Finding(
                        WARN,
                        unit.file,
                        unit.line,
                        "deck-prototype-mismatch",
                        f"[{name}] no matching string in the prototype: {unit.text[:90]}",
                        unit.text,
                        unit.text,
                    )
                )
    return found


# ---------------------------------------------------------------------------------------------
# The allow-list
# ---------------------------------------------------------------------------------------------


def parse_allow(text: str) -> tuple[list[AllowEntry], list[Finding]]:
    """`code | file-or-* | exact text or re:regex | reason`, fields split on " | ".

    A regex may hold a bare `|` (as in `a|b`). A missing reason fails.
    """
    entries: list[AllowEntry] = []
    problems: list[Finding] = []

    def problem(number: int, code: str, message: str, raw: str) -> None:
        problems.append(Finding(FAIL, ALLOW_PATH, number, code, message, "", raw))

    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        head = line.split(" | ", 2)
        if len(head) < 3 or not head[0].strip() or not head[1].strip():
            problem(number, "allow-syntax", "an entry is: code | file-or-* | text | reason", raw)
            continue
        code, file = head[0].strip(), head[1].strip()
        pattern, _, reason = head[2].rpartition(" | ")
        if not pattern:  # no third separator: all of it is the text
            pattern, reason = head[2], ""
        pattern, reason = pattern.strip(), reason.strip()
        if not reason:
            problem(number, "allow-reason", "this entry has no reason; say why it is allowed", raw)
            continue
        is_regex = pattern.startswith("re:")
        if is_regex:
            pattern = pattern[3:]
            try:
                re.compile(pattern)
            except re.error as err:
                problem(number, "allow-syntax", f"bad regex: {err}", raw)
                continue
        entries.append(AllowEntry(number, code, file, pattern, reason, is_regex))
    return entries, problems


def allow_matches(entry: AllowEntry, f: Finding) -> bool:
    if entry.code != f.code:
        return False
    if entry.file != "*" and not fnmatch.fnmatchcase(f.file, entry.file):
        return False
    if entry.is_regex:
        return bool(
            re.fullmatch(entry.pattern, f.match, re.IGNORECASE)
            or re.search(entry.pattern, f.context)
        )
    wanted = fold(entry.pattern)
    return wanted in (fold(f.match), fold(f.context))


def apply_allow(
    findings: Sequence[Finding], entries: Sequence[AllowEntry]
) -> tuple[list[Finding], list[Finding]]:
    """Drop allowed findings. Also returns a WARN for each entry that matched nothing."""
    used: set[int] = set()
    kept: list[Finding] = []
    for f in findings:
        hit = [e for e in entries if allow_matches(e, f)]
        used.update(e.line for e in hit)
        if not hit:
            kept.append(f)
    unused = [
        Finding(
            WARN,
            ALLOW_PATH,
            e.line,
            "allow-unused",
            f"entry matched nothing: {e.code} | {e.file} | {e.pattern}",
            "",
            "",
        )
        for e in entries
        if e.line not in used
    ]
    return kept, unused


# ---------------------------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------------------------


def sort_key(f: Finding) -> tuple[str, int, str, str]:
    return (f.file, f.line, f.code, f.message)


def collect_findings(files: dict[str, str]) -> list[Finding]:
    """All findings for a set of files, keyed by repo-relative path. Pure."""
    deck_text = files.get(DECK_PATH, "")
    rows = parse_deck(deck_text)
    not_terms = parse_not_terms(deck_text)
    deck_units_ = deck_to_units(rows)
    findings: list[Finding] = []
    findings.extend(check_units(deck_units_, not_terms))
    findings.extend(check_straight_quotes(rows))
    page_units: list[Unit] = []
    css: list[Decl] = []
    for path in sorted(files):
        if path.endswith(".html"):
            page = parse_page(files[path], path)
            page_units.extend(page.units)
            findings.extend(check_anchors(page.anchors))
            css.extend(page.css)
    if STYLES_PATH in files:
        css.extend(parse_css(files[STYLES_PATH], STYLES_PATH))
    findings.extend(check_units(page_units, not_terms))
    findings.extend(check_css(css))
    findings.extend(check_mismatch(deck_units_, page_units))
    allow_entries, allow_problems = parse_allow(files.get(ALLOW_PATH, ""))
    kept, unused = apply_allow(sorted(set(findings), key=sort_key), allow_entries)
    return sorted(set(kept + unused + allow_problems), key=sort_key)


def format_finding(f: Finding) -> str:
    return f"{f.severity}  {f.file}:{f.line}  {f.code}  {f.message}"


def summary(findings: Sequence[Finding]) -> str:
    fails = sum(1 for f in findings if f.severity == FAIL)
    warns = len(findings) - fails
    return f"copy_lint: {fails} FAIL, {warns} WARN"


def exit_code(findings: Sequence[Finding], *, warnings_as_errors: bool) -> int:
    has_fail = any(f.severity == FAIL for f in findings)
    has_warn = any(f.severity == WARN for f in findings)
    return 1 if has_fail or (warnings_as_errors and has_warn) else 0


def read_files(root: Path) -> dict[str, str]:
    paths = [root / DECK_PATH, root / ALLOW_PATH, root / STYLES_PATH]
    paths.extend(sorted((root / PROTOTYPE_DIR).glob("*.html")))
    return {
        p.relative_to(root).as_posix(): p.read_text(encoding="utf-8") for p in paths if p.exists()
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint the fixed copy and look of the prototype.")
    parser.add_argument("--warnings-as-errors", action="store_true", help="exit 1 on a WARN too")
    parser.add_argument("--quiet", action="store_true", help="print failures only")
    args = parser.parse_args(argv)
    findings = collect_findings(read_files(ROOT))
    for f in findings:
        if f.severity == FAIL or not args.quiet:
            print(format_finding(f))
    print(summary(findings))
    return exit_code(findings, warnings_as_errors=args.warnings_as_errors)


if __name__ == "__main__":
    sys.exit(main())
