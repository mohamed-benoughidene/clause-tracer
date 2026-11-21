# links

## Purpose
Read a contract's clauses and return every link between them: cross-references,
defined terms, overrides and documents that are not loaded. Every link keeps the
span it came from, and a target that cannot be certain is kept with no target.

## Spec
`docs/spec.md` section 6.1, step 5, and section 4.5 (evidence trail).

## Public calls

### `map_links`

`map_links(document: Document, clauses: tuple[Clause, ...]) -> LinkMap`

Input: a document and its clauses, as `ingest` returns them. Output: the link
map; every span points into `document.text`, and an unresolved target is `None`.
Raises `ValueError` when a clause span lies outside the text, when a sentence
span lies outside its clause, and when `build_index` refuses the clauses
(`clauses are not in text order` or `clause {id} has a later parent`). Effects:
none.

### `render_link_map`

`render_link_map(document: Document, clauses: tuple[Clause, ...], link_map: LinkMap) -> str`

Returns the link map as tab-separated lines, joined by one newline and ending in
one newline. The first line is the source, the second the counts, and each later
line is one reference, term, override, outside document or undefined term. A text
field replaces each tab and line break with one space. A dash (`-`) stands for no
clause or no target. Raises `ValueError` when `build_index` refuses the clauses,
with the same two messages as `map_links`. No side effects.

### `SampleInput`, `dump_clause_fixture`, `load_clause_fixture`

These three write and read the sample clause fixture. [The sample
fixture](#the-sample-fixture) says what each one does.

## Input shape
A `Document` and its `Clause` tuple from `core`. Every clause span and sentence
span points into `document.text`, and the clauses are in text order. `links`
reads all of `document.text`. The heading of the first clause that has one
decides the contract's own title (see [Known limits](#known-limits)).

## Output shape
A `LinkMap` from `core`, with five tuples.

- `references`: one `CrossReference` for each target. `source` is the span of the
  words read, and `target` is the clause id, or `None` when no clause is certain.
  A list or a range gives one reference for each target, with the source span of
  the whole list or range. Sorted by `source.start`; the keys of one match keep
  their order.
- `terms`: one `DefinedTerm` for each definition, in definition order. `term` is
  the words inside the quotes without a leading "the". `definition` is the
  trimmed span of the sentence that defines it. `uses` holds the span of each
  use, in text order. A term defined twice gives two entries, and both hold the
  same uses.
- `overrides`: one `Override` for each target. `clause_id` is the clause that
  holds the evidence. `target` is the clause the override names, or `None` when
  it names nothing: such an override joins every trail (Spec 4.5).
  `overrides_target` is true when that clause wins, and false when the target
  qualifies this clause. Sorted by `evidence.start`, then by target, with `None`
  first, and an identical override is kept once.
- `outside_documents`: one `OutsideDocument` for each mention of a document that
  is not loaded, in text order. `name` is the words as written, and `evidence` is
  the span of the name. Each mention is one entry.
- `undefined_terms`: the span of each capitalised run that is used but never
  defined, sorted by start.

## What it reads

### Cross-references
`clauses`, `sections`, `paragraphs`, `sub-clauses` and `subclauses`, followed by
a number, in any case. Lists ("clauses 4, 5 and 6") and ranges ("clauses 4 to 6",
with "to", a hyphen or a dash) give one reference for each member. `articles`
take an Arabic number or a Roman number built from `I`, `V`, `X`, `L` and `C`.
`schedule`, `annex`, `appendix` and `exhibit` take a number or one capital
letter. "This Clause" and its other forms ("this section", "this paragraph",
"this schedule" and so on) point at the clause or schedule that holds them.

A clause's own number in its heading is not a reference to itself. A reference
followed by "of", "in" or "under" and a document noun points into another
document, so it has no target: `under Section 3 of the Master Agreement` is one
reference with no target.

### Defined terms
A quoted term followed by `means`, `shall mean` or `has the meaning`, and these
bracket forms: `("the Agency")`, `(the "Agency")`, `(each a "Party")` and
`(together the "Parties")`. The quotes may be straight or curly. A term starts
with a capital letter and holds up to six words.

A definition in the middle of a sentence is read after a colon, a semicolon or a
comma. It is also read after "and" or "or" when an earlier definition of the same
sentence was read.

### Uses of a term
A whole-word match of the term, in any case, that starts with a capital letter in
the contract. It must lie outside the term's own quotes and outside the use of a
longer term. "Agency's" counts; "agency" and "Agencyship" do not. Plurals are not
uses. The longest term is read first, so "Master Agreement" takes the use inside
"Agreement".

### Documents that are not loaded
One to four capitalised words, a hyphenated word counting as one, then a document
noun: `Agreement`, `Contract`, `Deed`, `Addendum`, `Licence`, `License`,
`Statement of Work`, `Terms and Conditions`. Leading words such as "the" are
dropped from the name.

A mention is not read after "this", inside the term's own quotes, in a heading,
or as the contract's own name or title. The contract's own name is a defined term
whose definition says "this agreement", "this contract" or "this deed", or a
bracket that names the agreement itself.

### Overrides
- `Notwithstanding` before a reference: this clause overrides the target.
- `Subject to`, `save as set out in`, `save as provided in`, `except as set out
  in` and `except as provided in` before a reference: the target qualifies this
  clause.
- Between the phrase and the reference there may be only spaces, or "the
  provisions of" (also "terms" or "requirements", with "of" or "in").
- A list joined by "and", "or" or a comma gives one override for each target, and
  a range gives one for each member. A reference to "this Clause" or "this
  Agreement" is never the target.
- `Notwithstanding anything (else) (contained) (to the contrary) in this
  Agreement`, and `Notwithstanding any other provision of this Agreement` (the
  noun may be `provisions`, `term` or `terms`, and `of` may be `in`), give an
  override with no target. They give none when the sentence names a document
  that is not loaded.
- A sentence with `prevails` or `takes precedence`: the plain words before the
  verb, after the last comma that is not inside a reference, say who wins. "This
  Agreement" or "this Clause" wins over every reference in the sentence that
  resolves. A reference that wins qualifies this clause.
- A heading sentence gives no override.

### Terms used but never defined
A run of 2 to 4 capitalised words in the middle of a sentence. A heading
sentence and a table row are skipped. A run is not read when it is a defined
term, a use, inside a term's quotes or a document that is not loaded. Single
words are left out because they are most often names and places.

## The sample fixture
`samples/developer-agreement.clauses.json` is the clause fixture for the sample
contract. It is the `ingest` output for
`src/clause_tracer/ingest/samples/developer-agreement.txt`. Regenerate it only
with:

```bash
.venv/bin/uv run pytest tests/test_links_sample.py --update-goldens
```

Never edit the fixture by hand. A root test rebuilds it from `ingest` and
compares the two. `samples/README.md` says the same. The module cannot call
`ingest`, because the import rules keep pipeline modules apart (ADR 0004).

- `SampleInput`: frozen dataclass with two fields, `document: Document` and
  `clauses: tuple[Clause, ...]`.
- `dump_clause_fixture(document, clauses) -> str`
  - Input: a `Document` for a text file, and its clauses.
  - Output: the fixture as JSON text, ending in one newline.
  - Raises `ValueError` with the message `links sample: text documents only` when
    the document holds `char_map`, `glyphs`, `pages`, `furniture`, `hidden`,
    `undecodable` or `tracked_changes`.
  - Raises `ValueError` with the message `links sample: kind <kind> is not a text
    kind` when the source kind is not `text`, `markdown` or `pasted`.
  - Runs the structure checks below, so the writer refuses what the loader
    refuses.
- `load_clause_fixture(text) -> SampleInput`
  - Input: fixture text, as written by `dump_clause_fixture`.
  - Output: a `SampleInput`. The non-text fields of its `Document` are empty.
  - Raises `ValueError` with a message that starts `links sample: ` when the text
    fails one of these checks: it is not JSON; the top level is not an object;
    `format` or `version` is wrong; a key is unknown or missing; a value has the
    wrong type; a source kind is not a text kind; a clause or sentence span lies
    outside the text; a clause id is repeated; a parent id is unknown; a sentence
    span lies outside its clause; a level is below 1; a level does not fit its
    parent; a clause overlaps an earlier clause; a sentence id is repeated.

The writer and the loader share one structure check. For each clause, in order,
it raises on the first failure:

1. The clause span lies inside the text.
2. Every sentence span of the clause lies inside the text.
3. The clause id is not one an earlier clause has.
4. The clause has no `parent_id`, or its `parent_id` names an earlier clause.
5. Every sentence span of the clause lies inside the clause span.
6. The level is 1 or more, and then it is 1 with no parent, or the parent's level
   plus 1.
7. The clause starts at or after the end of the clause before it.
8. Every sentence id of the clause is not one an earlier sentence in the document
   has.

Fixture format: `format` is `clause-tracer-links-sample` and `version` is `1`.
The layout is:

```
format
version
document: schema_version, source {name, kind, sha256, size}, text, warnings [{code, page}]
clauses: [{id, number, heading, level, parent_id, start, end, numbering_source,
           sentences [{id, start, end}]}]
```

The printed link map of the sample is in
`tests/goldens/developer-agreement.links.txt`. Write it only with
`--update-goldens`, in a commit of its own, and ask the owner to read the diff.

`tests/case_builder.py` (`build_case`, `span_of`) is test code. It is not
exported.

## Known limits
`links` never guesses. When the wording cannot tell, a reference stays with no
target, and a term stays undefined.

Left to later stages:

- Building a label's evidence trail from the link map, and so filling
  `LabelInput.outside_documents` for Rule 10: stage 8. Showing the "Refers to a
  document that isn't loaded" line: stage 12.
- The privacy allow-list built from `LinkMap.terms`: stage 4. Passing that list
  into `privacy`: stage 6.
- Storing the link map as a derived record, with its cache key and its version
  constant (`derived_by`): stage 6.
- Checking that a rewrite keeps every cross-reference: stage 11.
- Hidden text in Word and PDF files. `links` reads all of `Document.text`,
  including text that stage 5 flags as hidden. Whether it skips
  `Document.hidden` spans is decided in stage 5 (Spec 8.4).
- Subject overrides, such as "the payment terms prevail": stage 8 (question 8).

Reference styles this stage does not read: `cl. 5`, `Part 2`, "the clause above",
"the preceding paragraph", a definition written without quotes (`Charges
means`), and a definition list in a schedule that uses a table.

Rules that stay cautious:

- A duplicated number is never resolved, so the reference keeps no target.
- `Annex 1` and `Appendix 1` share the id `A1` in `ingest`, so both stay
  unresolved.
- An article with a `.` part or a bracket, such as `Article 5.1`, stays
  unresolved.
- `paragraph (a)` and `clause 4 (a)`, with a space before the bracket, are not
  read as a whole.
- Articles read `I`, `V`, `X`, `L` and `C` only. A schedule reads an upper-case
  designation only, so `annex a` is not read.
- "X prevails over Y" is read only when X is this clause or this Agreement, or a
  reference that names one clause.
- Lower-case document mentions are not outside documents. A lower-case name
  therefore does not stop a "this Clause prevails" override with no target.
- A name written in capitals (`THE MASTER AGREEMENT`) is not read.
- A name longer than four capitalised words is cut to its last four.
- `Standard Form Agreement`, `Agency Agreement` and every other generic name that
  the rule accepts are listed as outside documents.
- Each mention of an outside document is one entry, so a screen lists names once.
- Names and places show up as terms used but never defined until `privacy` runs.
  Stage 8 decides how the list is used.

Limits from the code reviews:

- A capitalised run at the start of a sentence is never reported as used but
  never defined (the owner chose this limit on 20 Nov 2026).
- The contract's own title is the heading of the first clause that has one. A
  first clause headed like a document name hides later mentions of that name.
- Quote marks of a definition are not paired. A mismatched pair, such as a double
  quote closed by a straight apostrophe, can give a false definition.
- A definition in the middle of a sentence is read only after a colon, a
  semicolon or a comma, or after "and" or "or" when an earlier definition of the
  same sentence was read.
- Only the first `prevails` verb of a sentence is read. A second claim in the
  same sentence is missed and gives no override (the owner chose this limit on
  20 Nov 2026).
- References broken by a zero-width or bidi character are not found. Stage 5
  flags those characters as hidden text.

## Depends on
`core` only. Tests may import the owner-table loader and the hazard alphabet from
`clause_tracer.core.tests`, and they never import another pipeline module.

## Run alone
`.venv/bin/uv run python -m clause_tracer.links` prints the link map of the sample
clause fixture.

`.venv/bin/uv run python -m clause_tracer.links --input path/to/fixture.json`
reads another clause fixture. Write the sample fixture from the sample text with
`.venv/bin/uv run pytest tests/test_links_sample.py --update-goldens`.

Exit 0 prints the link map and ends. Exit 3 means the file could not be read, or
it is not a valid fixture; the message names the reason.
