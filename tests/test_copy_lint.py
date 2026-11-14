"""Tests for scripts/copy_lint.py: small inline strings, no dependence on the real deck or pages."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "copy_lint.py"
_spec = importlib.util.spec_from_file_location("copy_lint", SCRIPT)
assert _spec is not None and _spec.loader is not None
cl = importlib.util.module_from_spec(_spec)
sys.modules["copy_lint"] = cl  # dataclasses look their module up here
_spec.loader.exec_module(cl)


def unit(text, *, source="page", scope="", is_toast=False, page="", file="prototype/x.html"):
    return cl.Unit(file, 1, text, source, scope, is_toast, page)


def codes(findings):
    return sorted({f.code for f in findings})


def check(text, not_terms=(), **kw):
    return cl.check_unit(unit(text, **kw), not_terms)


# ---------------------------------------------------------------- FAIL checks on copy

FAILING = {
    "client": "Send it to your client.",
    "open-source": "It is open-source software.",
    "new-tab": "Open site (opens in a new tab)",
    "exclamation": "Saved!",
    "banned-word": "Please check the quote.",
    "first-person": "I'd walk away from this one.",
    "tap-press": "Tap the label.",
    "us-spelling": "Pick a color.",
    "emoji": "Done \U0001f389",
}
PASSING = {
    "client": "Send it to your customer.",
    "open-source": "The code is source available.",
    "new-tab": "Open site (opens in your browser)",
    "exclamation": "Saved.",
    "banned-word": "Check the quote.",
    "first-person": "This one is a walk-away.",
    "tap-press": "Click the label.",
    "us-spelling": "Pick a colour.",
    "emoji": "Done · 5 pages … “quoted” it’s → § 5.4",
}


@pytest.mark.parametrize("code", sorted(FAILING))
def test_failing_copy_is_caught(code):
    found = check(FAILING[code])
    assert code in codes(found)
    assert all(f.severity == "FAIL" for f in found if f.code == code)


@pytest.mark.parametrize("code", sorted(PASSING))
def test_passing_copy_is_clean(code):
    assert code not in codes(check(PASSING[code]))


def test_client_is_a_whole_word():
    assert "client" in codes(check("Your clients agree."))
    assert "client" not in codes(check("Clientele"))


@pytest.mark.parametrize(
    "word", ["simply", "oops", "sorry", "seamlessly", "powerful", "robust", "unlock", "leverage"]
)
def test_each_banned_word_fails(word):
    assert "banned-word" in codes(check(f"This is {word} done."))


def test_banned_phrase_fails():
    assert "banned-word" in codes(check("Something went wrong."))


def test_banned_word_inside_a_longer_word_passes():
    assert "banned-word" not in codes(check("Pleasant, and a leveraged buyout."))


def test_open_source_with_a_space_fails():
    assert "open-source" in codes(check("An open source tool."))


def test_new_tab_phrase_fails():
    assert "new-tab" in codes(check("Opens in a new tab."))


@pytest.mark.parametrize("text", ["I", "I'm", "I’ve", "my", "me", "myself", "Show me"])
def test_first_person_words_fail(text):
    assert "first-person" in codes(check(f"Then {text} left."))


def test_first_person_ignores_letters_inside_words():
    assert "first-person" not in codes(check("Items, mine and the Meter."))


def test_tap_and_press_a_control_fail():
    assert "tap-press" in codes(check("Press Replace to swap it."))
    assert "tap-press" in codes(check("tap here"))


def test_press_a_key_is_allowed():
    assert "tap-press" not in codes(check("Press M to merge."))
    assert "tap-press" not in codes(check("Press Esc to close."))


def test_us_spellings_fail():
    for word in ["summarize", "recognize", "organize", "labeled", "favorite", "center", "colors"]:
        assert "us-spelling" in codes(check(f"The {word} one.")), word


def test_license_as_a_common_noun_fails_but_names_pass():
    assert "us-spelling" in codes(check("Read the license."))
    assert "us-spelling" not in codes(check("The Functional Source License applies."))
    assert "us-spelling" not in codes(check("See the LICENSE file and COMMERCIAL_LICENSE."))
    assert "us-spelling" not in codes(check("Read the licence."))


def test_not_column_term_fails_and_other_words_pass():
    terms = ["analysis", "rule set", "client", "ai-generated"]
    assert "not-column" in codes(check("Start the analysis.", terms))
    assert "not-column" in codes(check("Use a rule set here.", terms))
    assert "not-column" in codes(check("This is AI-generated.", terms))
    assert "not-column" not in codes(check("Start the review.", terms))


def test_not_column_matches_a_plural():
    assert "not-column" in codes(check("Two analyses and some scans.", ["scan"]))


def test_toast_over_five_words_fails_and_five_passes():
    assert "toast-length" in codes(check("Back to the tool label now", is_toast=True))
    assert "toast-length" not in codes(check("Back to tool label now", is_toast=True))
    assert "toast-length" not in codes(check("A long sentence that is not a toast at all."))


def test_emoji_in_copy_fails_and_label_icons_are_not_copy():
    assert "emoji" in codes(check("Walk-away ✕"))
    assert "emoji" in codes(check("Ticked ✓"))
    assert "emoji" not in codes(check("Walk-away · 3 days … § 5"))


# ---------------------------------------------------------------- WARN checks on copy


def test_soft_words_warn():
    found = check("It is just very easy and really quick, easily.")
    soft = [f for f in found if f.code == "soft-word"]
    assert len(soft) == 4
    assert all(f.severity == "WARN" for f in soft)
    assert "soft-word" not in codes(check("Edited a moment ago."))


def test_long_sentence_warns_over_25_words():
    long = " ".join(["Word"] * 26) + "."
    fine = " ".join(["Word"] * 25) + "."
    assert "long-sentence" in codes(check(long))
    assert "long-sentence" not in codes(check(fine))
    assert "long-sentence" not in codes(check(fine + " " + fine))


def test_repeated_number_warns_at_three_in_one_scope():
    units = [
        unit("Cost $0.42.", scope="d"),
        unit("Spent $0.42.", scope="d"),
        unit("$0.42", scope="d"),
    ]
    found = cl.check_repeated_numbers(units)
    assert codes(found) == ["repeated-number"]
    assert found[0].severity == "WARN"


def test_repeated_number_passes_with_two_or_across_scopes_or_single_digits():
    two = [unit("Cost $0.42.", scope="d"), unit("Spent $0.42.", scope="d")]
    assert cl.check_repeated_numbers(two) == []
    split = [unit("$0.42", scope=s) for s in "abc"]
    assert cl.check_repeated_numbers(split) == []
    digits = [unit("Step 1 of 4", scope="d")] * 3
    assert cl.check_repeated_numbers(digits) == []


def test_straight_quote_in_a_deck_cell_warns():
    bad = cl.DeckRow(7, "x.html", "Row", [], 'Say "hello"')
    good = cl.DeckRow(8, "x.html", "Row", [], "Say “hello”")
    assert codes(cl.check_straight_quotes([bad])) == ["straight-quote"]
    assert cl.check_straight_quotes([good]) == []


def test_straight_quote_ignores_code_spans():
    row = cl.DeckRow(9, "x.html", "Row", [], 'Key `"x"` here')
    assert cl.check_straight_quotes([row]) == []


# ---------------------------------------------------------------- the deck

DECK = """\
# Deck

## 1. Voice

| Rule | Do | Don't |
| --- | --- | --- |
| Never client | customer | client |

## 2. Word list

| Use | Not | Notes |
| --- | --- | --- |
| review | analysis, scan, job | One contract. |
| your party / the other side | client, counterparty, you / them | |
| OpenRouter key | API key, AI key | See 6.1. |

## 4. Screen by screen

### 4.1 First launch (`index.html`)

| Element | Copy |
| --- | --- |
| Heading | Check a contract. |
| Key field | OpenRouter key · placeholder `sk-or-…` |
| Maintainer note (not on screen) | This is a client note. |
| Delete dialog | Delete it? · Cancel / Delete · toast: Review deleted · (Not shown: a client) |
| Step | Check 9 → (Ready to check: the unchecked count) |

### 4.17 Everywhere

| Element | Copy | Written by |
| --- | --- | --- |
| Toasts | Saved · Copied | code |

## 5. Localisation notes

| Element | Copy |
| --- | --- |
| Sentence | This client sentence is not copy. |
"""


def test_parse_deck_reads_only_section_4_copy_cells():
    rows = cl.parse_deck(DECK)
    texts = [t for r in rows for t, _ in r.units]
    assert "Check a contract." in texts
    assert "Cancel / Delete" in texts
    assert "Saved" in texts
    assert not any("client" in t for t in texts)  # sections 1, 5 and the maintainer note


def test_parse_deck_skips_backticks_and_notes():
    texts = [t for r in cl.parse_deck(DECK) for t, _ in r.units]
    assert "OpenRouter key" in texts
    assert not any("sk-or" in t for t in texts)
    assert not any("Not shown" in t for t in texts)
    assert "Check 9 →" in " ".join(texts)  # a long parenthetical note is dropped


def test_parse_deck_names_the_page_and_marks_toasts():
    rows = {r.first_cell: r for r in cl.parse_deck(DECK)}
    assert rows["Delete dialog"].page == "index.html"
    assert rows["Delete dialog"].units[-1] == ("Review deleted", True)
    assert rows["Delete dialog"].units[0] == ("Delete it?", False)
    assert rows["Toasts"].page == ""
    assert all(is_toast for _, is_toast in rows["Toasts"].units)


def test_parse_deck_lines_point_at_the_row():
    rows = cl.parse_deck(DECK)
    heading = next(r for r in rows if r.first_cell == "Heading")
    assert DECK.splitlines()[heading.line - 1].startswith("| Heading")


def test_parse_not_terms_splits_on_commas_and_slashes():
    terms = cl.parse_not_terms(DECK)
    assert terms == [
        "analysis", "scan", "job", "client", "counterparty", "you", "them", "api key", "ai key",
    ]  # fmt: skip


def test_not_terms_come_from_the_deck_at_run_time():
    files = {cl.DECK_PATH: DECK, "prototype/a.html": "<p>Start the analysis.</p>"}
    found = [f for f in cl.collect_findings(files) if f.code == "not-column"]
    assert [f.file for f in found] == ["prototype/a.html"]


# ---------------------------------------------------------------- the pages


def page(html, file="prototype/p.html"):
    return cl.parse_page(html, file)


def texts(html):
    return [u.text for u in page(html).units]


def test_page_text_nodes_join_inline_tags():
    assert texts("<p>This one is <b>a walk-away</b>. Read 5.4.</p>") == [
        "This one is a walk-away. Read 5.4."
    ]


def test_page_blocks_are_separate_strings_with_a_line_number():
    parsed = page("<h1>Title</h1>\n<p>\n  Body text.\n</p>")
    assert [(u.text, u.line) for u in parsed.units] == [("Title", 1), ("Body text.", 3)]


def test_page_puts_back_a_space_between_run_together_elements():
    assert texts("<div><b>5.4</b><span>Charges</span></div>") == ["5.4 Charges"]
    assert texts("<p><b>word</b>.</p>") == ["word."]


def test_page_skips_script_style_comment_and_svg():
    html = (
        "<p>Visible.</p><script>var x = 'Please';</script><style>a{color:red}</style>"
        "<!-- Oops --><svg><title>Sorry</title><text>Simply</text></svg>"
    )
    assert texts(html) == ["Visible."]


def test_page_skips_the_contract_sheet_and_its_contents():
    html = '<p>App text.</p><article class="sheet"><p>The client shall pay!</p></article>'
    assert texts(html) == ["App text."]
    assert cl.check_units(page(html).units) == []


def test_page_skips_nested_skip_class_but_resumes_after_it():
    html = '<div class="doc"><p>Contract.</p></div><p>After.</p>'
    assert texts(html) == ["After."]


def test_page_skips_the_state_link_list():
    html = '<div class="map"><a href="a.html">Oops state</a></div><p>Real.</p>'
    assert texts(html) == ["Real."]


def test_page_reads_the_copy_attributes():
    html = (
        '<button aria-label="Close" title="Close it" data-toast="Saved">x</button>'
        '<input placeholder="sk-or-…"><img alt="A butterfly">'
    )
    assert sorted(texts(html)) == ["A butterfly", "Close", "Close it", "Saved", "sk-or-…", "x"]


def test_page_reads_value_on_buttons_only():
    html = (
        '<button value="ok">Go</button><input type="text" value="secret">'
        '<option value="a">A</option>'
    )
    assert "ok" in texts(html)
    assert "secret" not in texts(html)


def test_page_marks_data_toast_as_a_toast_and_checks_its_length():
    html = '<button data-toast="Back to the tool label now">x</button>'
    parsed = page(html)
    assert any(u.is_toast for u in parsed.units)
    assert "toast-length" in codes(cl.check_units(parsed.units))


def test_page_scopes_a_dialog_for_the_repeated_number_check():
    html = (
        "<dialog><p>Cost $0.42.</p><p>Spent $0.42.</p>"
        '<button data-toast="$0.42">x</button></dialog>'
        "<p>Outside $0.42</p>"
    )
    assert "repeated-number" in codes(cl.check_units(page(html).units))


def test_link_out_fails_without_the_phrase_and_passes_with_it():
    bad = page('<a href="https://example.com">Add credit</a>')
    assert codes(cl.check_anchors(bad.anchors)) == ["link-out"]
    blank = page('<a href="x.html" target="_blank">Open</a>')
    assert codes(cl.check_anchors(blank.anchors)) == ["link-out"]
    good = page(
        '<a href="https://example.com">Add credit<span class="visually-hidden"> '
        "(opens in your browser)</span></a>"
    )
    assert cl.check_anchors(good.anchors) == []
    release = page('<a href="https://e.com">Check (opens the release page in your browser)</a>')
    assert cl.check_anchors(release.anchors) == []


def test_link_out_ignores_in_app_links_and_links_in_the_contract():
    assert cl.check_anchors(page('<a href="home.html">Reviews</a>').anchors) == []
    sheet = page('<article class="sheet"><a href="https://e.com">https://e.com</a></article>')
    assert cl.check_anchors(sheet.anchors) == []


# ---------------------------------------------------------------- CSS


def css_codes(css, base=()):
    return codes(cl.check_css(cl.parse_css(css, "s.css", 1, base)))


def test_parse_css_reads_nested_rules_and_media():
    decls = cl.parse_css(
        "/* c */\n:root { --a: 1px; }\n@media (max-width: 9px) { .a { color: red; } }\n"
        'html:is([x="1"]) {\n  .b { margin: 0; }\n}\n',
        "s.css",
    )
    found = {(d.selector, d.prop, d.line) for d in decls if not d.prop.startswith("@")}
    assert (":root", "--a", 2) in found
    assert (".a", "color", 3) in found
    assert (".b", "margin", 5) in found


def test_parse_css_keeps_semicolons_inside_urls_and_strings():
    decls = cl.parse_css(
        '.a { background: url(data:image/png;base64,AA); content: "a;b"; }', "s.css"
    )
    assert [(d.prop, d.value) for d in decls] == [
        ("background", "url(data:image/png;base64,AA)"),
        ("content", '"a;b"'),
    ]


def test_red_outside_the_walk_label_fails():
    assert "red-outside-walk" in css_codes(".btn { color: var(--red); }")
    assert "red-outside-walk" in css_codes(".nav a { background: var(--walk-bg); }")
    assert "red-outside-walk" in css_codes(".x { border-color: #a91207; }")
    assert "red-outside-walk" in css_codes(".x { --red-tint: #fff; }")


def test_red_on_walk_selectors_and_tokens_passes():
    assert (
        css_codes(".stamp.walk { color: var(--walk); } .pin.walk .word { color: var(--walk-fg); }")
        == []
    )
    assert css_codes(":root { --red: #A91207; } :root[data-theme='dark'] { --red: #E0523F; }") == []
    assert css_codes(".logo { color: var(--red); }") == []
    assert css_codes(".btn { color: var(--text); }") == []


def test_red_in_a_selector_list_must_be_allowed_in_every_part():
    assert "red-outside-walk" in css_codes(".stamp.walk, .btn { color: var(--walk); }")


def test_red_in_a_style_attribute_uses_the_elements_classes():
    assert "red-outside-walk" in css_codes("background: var(--walk)", ("i",))
    assert css_codes("background: var(--walk)", ("span.pin.walk",)) == []


@pytest.mark.parametrize(
    "decl",
    [
        "background: linear-gradient(red, blue)",
        "background: radial-gradient(red, blue)",
        "filter: blur(4px)",
        "backdrop-filter: blur(4px)",
        "animation: spin 1s",
        "animation-name: spin",
    ],
)
def test_effects_fail(decl):
    assert "effect" in css_codes(f".x {{ {decl}; }}")


def test_keyframes_fail_and_flat_css_passes():
    assert "effect" in css_codes("@keyframes spin { from { opacity: 0 } to { opacity: 1 } }")
    assert (
        css_codes(".x { background: var(--bg-tone); box-shadow: none; transition: left .15s; }")
        == []
    )


@pytest.mark.parametrize("value", ["10px", "6px", "12px 4px", "var(--r-xl)", "5%"])
def test_bad_radius_fails(value):
    assert "radius" in css_codes(f".x {{ border-radius: {value}; }}")


@pytest.mark.parametrize(
    "value",
    ["var(--r)", "var(--r-lg)", "0", "2px", "3px", "4px", "8px", "50%", "999px", "4px 4px 0 0"],
)
def test_allowed_radius_passes(value):
    assert css_codes(f".x {{ border-radius: {value}; }}") == []


def test_corner_radius_properties_are_checked_too():
    assert "radius" in css_codes(".x { border-top-left-radius: 10px; }")


def test_emoji_in_css_content_fails():
    assert "emoji" in css_codes('.x::before { content: "✓"; }')
    assert "emoji" not in css_codes('.x::before { content: "→"; }')


def test_style_blocks_and_attributes_in_a_page_are_checked():
    html = (
        "<style>.a { border-radius: 12px; }</style>"
        '<p class="x" style="background: linear-gradient(red, blue)">Text</p>'
    )
    found = cl.check_css(page(html).css)
    assert codes(found) == ["effect", "radius"]


# ---------------------------------------------------------------- mismatch


def test_normalise_lowers_case_strips_ends_and_wildcards_digits():
    assert cl.normalise("  Saved as a Draft. ") == "saved as a draft"
    assert cl.normalise("Check 9 \u2192") == f"check {cl.WILD} \u2192"
    assert cl.normalise("\u201cMs Jones\u201d is here") == 'ms jones" is here'
    assert cl.normalise("Spent $0.05 of about $0.42") == f"spent ${cl.WILD} of about ${cl.WILD}"


def test_normalise_deck_placeholders_become_wildcards_and_buttons_keep_words():
    assert cl.normalise("[n] pencilled in", deck=True) == f"{cl.WILD} pencilled in"
    assert cl.normalise("Delete “[name]”?", deck=True) == f'delete "{cl.WILD}'
    assert cl.normalise("[Save key] now", deck=True) == "save key now"


def test_strings_match_with_placeholders_digits_and_containment():
    deck = cl.normalise("Delete “[name]”? This can't be undone.", deck=True)
    shown = cl.normalise("Delete “Atlas Media retainer”? This can't be undone.")
    assert cl.strings_match(deck, shown)
    assert cl.strings_match(cl.normalise("[n] reviews", deck=True), cl.normalise("6 reviews"))
    assert cl.strings_match("open the review", "click open the review now")
    assert not cl.strings_match("open the review", "close the app")


def test_mismatch_warns_both_ways_and_passes_a_match():
    deck = [
        unit("Your review is ready", source="deck", page="running.html", file=cl.DECK_PATH),
        unit("Wrote the explanations now", source="deck", page="running.html", file=cl.DECK_PATH),
    ]
    shown = [
        unit("Your review is ready", file="prototype/running.html"),
        unit("Totally different words here", file="prototype/running.html"),
    ]
    found = cl.check_mismatch(deck, shown)
    assert codes(found) == ["deck-prototype-mismatch"]
    assert all(f.severity == "WARN" for f in found)
    by_file = {f.file for f in found}
    assert by_file == {"prototype/running.html", cl.DECK_PATH}
    assert len(found) == 2


def test_mismatch_ignores_strings_under_three_words_and_pages_without_a_deck_page():
    deck = [unit("Saved", source="deck", page="running.html", file=cl.DECK_PATH)]
    shown = [unit("Two words", file="prototype/running.html")]
    assert cl.check_mismatch(deck, shown) == []


def test_mismatch_uses_the_everywhere_section_for_every_page():
    deck = [unit("Not legal advice here", source="deck", page="", file=cl.DECK_PATH)]
    shown = [unit("Not legal advice here", file="prototype/help.html")]
    assert cl.check_mismatch(deck, shown) == []


# ---------------------------------------------------------------- the allow-list


def test_allow_entry_without_a_reason_fails():
    entries, problems = cl.parse_allow("first-person | * | Show me\n")
    assert entries == []
    assert codes(problems) == ["allow-reason"] or codes(problems) == ["allow-syntax"]
    assert all(p.severity == "FAIL" for p in problems)


def test_allow_entry_with_an_empty_reason_fails():
    entries, problems = cl.parse_allow("first-person | * | Show me | \n")
    assert entries == [] and codes(problems) == ["allow-reason"]


def test_allow_entry_with_a_bad_regex_or_missing_fields_fails():
    _, bad_regex = cl.parse_allow("x | * | re:( | why")
    assert codes(bad_regex) == ["allow-syntax"]
    _, short = cl.parse_allow("just one field")
    assert codes(short) == ["allow-syntax"]


def test_allow_list_ignores_comments_and_blank_lines():
    entries, problems = cl.parse_allow("# note\n\nclient | * | the client | a name\n")
    assert len(entries) == 1 and problems == []
    assert entries[0].reason == "a name"


def test_allow_regex_may_use_a_bare_bar():
    entries, problems = cl.parse_allow("first-person | * | re:a|b | reason here")
    assert problems == [] and entries[0].pattern == "a|b" and entries[0].is_regex


def finding(code="first-person", file="prototype/a.html", match="me", context="Show me"):
    return cl.Finding("FAIL", file, 3, code, "msg", match, context)


def test_allow_entry_silences_a_matching_finding_and_only_that_code():
    entries, _ = cl.parse_allow("first-person | * | Show me | A button.")
    kept, unused = cl.apply_allow([finding(), finding(code="client")], entries)
    assert [f.code for f in kept] == ["client"]
    assert unused == []


def test_allow_entry_matches_the_word_or_the_whole_string_not_a_part():
    entries, _ = cl.parse_allow("not-column | * | change | The verb.")
    assert (
        cl.apply_allow([finding("not-column", match="change", context="Change it")], entries)[0]
        == []
    )
    kept, _ = cl.apply_allow([finding("not-column", match="edit", context="change edit")], entries)
    assert len(kept) == 1


def test_allow_entry_regex_matches_the_word_fully_or_is_found_in_the_string():
    entries, _ = cl.parse_allow("first-person | * | re:Before I sign | Sample message.")
    hit = finding(match="I", context="Thanks. Before I sign, could we look?")
    miss = finding(match="I", context="I walk away")
    assert cl.apply_allow([hit], entries)[0] == []
    assert len(cl.apply_allow([miss], entries)[0]) == 1


def test_allow_entry_is_limited_to_its_file_or_glob():
    one, _ = cl.parse_allow("first-person | prototype/a.html | Show me | Button.")
    assert cl.apply_allow([finding()], one)[0] == []
    assert len(cl.apply_allow([finding(file="prototype/b.html")], one)[0]) == 1
    glob, _ = cl.parse_allow("first-person | prototype/* | Show me | Button.")
    assert cl.apply_allow([finding(file="prototype/b.html")], glob)[0] == []


def test_allow_entry_ignores_case_and_curly_quotes():
    entries, _ = cl.parse_allow("first-person | * | Days until I'm paid | A position name.")
    f = finding(match="I’m", context="DAYS UNTIL I’M PAID")
    assert cl.apply_allow([f], entries)[0] == []


def test_unused_allow_entry_warns():
    entries, _ = cl.parse_allow("first-person | * | Never seen | Nothing matches this.")
    kept, unused = cl.apply_allow([finding()], entries)
    assert len(kept) == 1
    assert [(u.code, u.severity, u.file, u.line) for u in unused] == [
        ("allow-unused", "WARN", cl.ALLOW_PATH, 1)
    ]


# ---------------------------------------------------------------- the whole run


def run(files):
    return cl.collect_findings(files)


def test_a_clean_page_gives_no_fail():
    files = {cl.DECK_PATH: DECK, "prototype/index.html": "<h1>Check a contract.</h1>"}
    assert not [f for f in run(files) if f.severity == "FAIL"]


def test_a_planted_violation_is_found_with_its_file_and_line():
    files = {cl.DECK_PATH: DECK, "prototype/index.html": "<p>Fine.</p>\n<p>Please wait!</p>"}
    found = [f for f in run(files) if f.severity == "FAIL"]
    assert {(f.file, f.line, f.code) for f in found} == {
        ("prototype/index.html", 2, "banned-word"),
        ("prototype/index.html", 2, "exclamation"),
    }


def test_the_allow_file_silences_a_finding_and_flags_its_own_problems():
    page_html = "<button>Show me</button>"
    files = {cl.DECK_PATH: DECK, "prototype/index.html": page_html}
    assert "first-person" in codes(run(files))
    files[cl.ALLOW_PATH] = "first-person | * | Show me | A button.\nclient | * | x | y\n"
    result = run(files)
    assert "first-person" not in codes(result)
    assert "allow-unused" in codes(result)
    files[cl.ALLOW_PATH] = "first-person | * | Show me\n"
    assert any(f.severity == "FAIL" and f.code.startswith("allow-") for f in run(files))


def test_findings_are_sorted_and_deduplicated():
    files = {
        cl.DECK_PATH: DECK,
        "prototype/b.html": "<p>Oops!</p>",
        "prototype/a.html": "<p>Oops!</p>",
    }
    found = run(files)
    keys = [(f.file, f.line, f.code) for f in found]
    assert keys == sorted(keys)
    assert len(keys) == len(set((*k, f.message) for k, f in zip(keys, found, strict=True)))


def test_css_in_the_stylesheet_file_is_checked():
    files = {cl.DECK_PATH: DECK, cl.STYLES_PATH: ".btn { border-radius: 12px; }"}
    found = [f for f in run(files) if f.code == "radius"]
    assert [(f.file, f.line) for f in found] == [(cl.STYLES_PATH, 1)]


def test_format_summary_and_exit_code():
    fail = cl.Finding("FAIL", "a.html", 4, "client", "no", "", "")
    warn = cl.Finding("WARN", "a.html", 5, "soft-word", "maybe", "", "")
    assert cl.format_finding(fail) == "FAIL  a.html:4  client  no"
    assert cl.summary([fail, warn]) == "copy_lint: 1 FAIL, 1 WARN"
    assert cl.exit_code([fail, warn], warnings_as_errors=False) == 1
    assert cl.exit_code([warn], warnings_as_errors=False) == 0
    assert cl.exit_code([warn], warnings_as_errors=True) == 1
    assert cl.exit_code([], warnings_as_errors=True) == 0


def test_main_quiet_prints_failures_only(tmp_path, capsys, monkeypatch):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "ux-copy.md").write_text(DECK, encoding="utf-8")
    (tmp_path / "prototype").mkdir()
    (tmp_path / "prototype" / "a.html").write_text("<p>Oops. It is just so.</p>", encoding="utf-8")
    monkeypatch.setattr(cl, "ROOT", tmp_path)
    assert cl.main(["--quiet"]) == 1
    out = capsys.readouterr().out
    assert "FAIL  prototype/a.html:1  banned-word" in out
    assert "soft-word" not in out
    assert out.strip().splitlines()[-1].startswith("copy_lint: 1 FAIL, ")
    assert cl.main([]) == 1
    assert "soft-word" in capsys.readouterr().out
