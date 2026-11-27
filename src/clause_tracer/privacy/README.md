# privacy

## Purpose
Find personal data in clauses and turn it into placeholder text.

## Spec
`docs/spec.md` sections 4.2 and 8, and section 6.1 steps 3 and 4.

## Input shape
`PrivacyInput` holds the document, its clauses, the typed parties and the defined
terms. Its fields are `document` (`Document`), `clauses` (`tuple[Clause, ...]`),
`parties` (`tuple[Party, ...]`) and `terms` (`tuple[DefinedTerm, ...]`).

The detector is passed in through the `PiiDetector` port of `core`:
`find(text: str) -> tuple[PiiSuggestion, ...]`. It sees the whole text once and
returns spans in whole-text offsets counted in code points. The adapter that
implements the port is built in stage 7; `FakePiiDetector` stands in for it in
tests and in the command-line run.

## Output shape
`PiiSuggestion` holds one flagged span: `span`, `kind` (a `PlaceholderKind`) and
`source` (a `PiiSource`).

`PlaceholderEntity` holds one placeholder: `id`, `kind`, `number` and every
`span` of that name.

`PlaceholderText` holds `text`, the entities and the `segments`. Each `Segment`
holds `kind`, `sent`, `original` and `entity_id`. Its three kinds are:

- `COPY`: the same characters in both texts;
- `ENTITY`: a name span in the contract and its token in the sent text;
- `ESCAPE`: one marker character in the contract and its escaped form in the
  sent text.

The segments tile both texts, so a quote maps back exactly.

## Public calls
Each call is pure (T1): it reads no file, clock or network, and it prints
nothing.

- `PrivacyInput`: the input shape above. It raises nothing and has no effects.
- `anonymise(document, entities)`: Input: a document and its entities. Output:
  the `PlaceholderText`, the entities as given, and the segments. Raises:
  `ValueError` with `privacy: duplicate entity id`, `privacy: duplicate
  placeholder`, `privacy: entity has no span`, `privacy: entity span is
  outside the text`, `privacy: entity span is empty`, `privacy: entity spans
  overlap` or `privacy: a placeholder number starts at 1`. Effects: none.
- `dump_privacy_fixture(case)`: Input: a `PrivacyInput` whose document is a text
  document. Output: the fixture text, ending in one newline. Raises:
  `ValueError` with `privacy sample: text documents only`, `privacy sample:
  kind <kind> is not a text kind`, or a structure message from the input check
  (see the Sample fixture section). Effects: none.
- `find_personal_data(case, detector)`: Input: a `PrivacyInput` and a detector.
  Output: the kept suggestions, sorted and with no overlap. Raises:
  `ValueError` from a finder or a later step, and any error from the detector,
  which is never caught. Effects: none.
- `group_entities(document, suggestions)`: Input: a document and its
  suggestions. Output: one numbered entity for each name, in first-place order.
  Raises: `ValueError` with `privacy: suggestion span is outside the text` or
  `privacy: suggestions overlap`. Effects: none.
- `load_privacy_fixture(text)`: Input: fixture text written by
  `dump_privacy_fixture`. Output: the `PrivacyInput`. Raises: `ValueError` with
  the prefix `privacy sample: ` when the text is not a well-formed text fixture
  (for example `privacy sample: not JSON`). Effects: none.
- `map_to_original(placeholder, span)`: Input: the placeholder text and a
  non-empty span of its sent text. Output: the matching span of the contract,
  with an edge inside a placeholder snapped out to the whole name. Raises:
  `ValueError` with `privacy: span is outside the placeholder text` or
  `privacy: an empty span has no place`. Effects: none.
- `render_privacy_report(case, entities, placeholder)`: Input: the privacy
  input, its entities and its placeholder text. Output: the report text (see
  below). Raises: none. Effects: none.
- `restore_reply(placeholder, document, reply)`: Input: the placeholder text,
  the document and an AI reply. Output: the reply with each token replaced by
  the entity's first place. Raises: `ValueError` with `privacy: entity has no
  span`, `privacy: entity span is outside the text` or `privacy: unknown
  placeholder`. Effects: none.
- `restore_text(placeholder, document)`: Input: the placeholder text and the
  document that it came from. Output: the whole contract text, with each copied
  part taken from the sent text. Raises: `ValueError` with `privacy: segments
  do not tile the texts`. Effects: none.

## Rules
**Source priority and the cut rule.** Overlaps are resolved in this order:
`USER`, `PARTY_DETAILS`, `PATTERN`, `RULE`, then `NER`; then the longer span,
the earlier start and the kind rank of `TIE_RANK`. A lower-priority suggestion
is cut around the kept span, never dropped whole, so the part outside a kept
span may be a fragment. A fragment with no letter or digit is dropped.

**The allow-list and question 11.** A defined term stays readable. It is kept
unless it is the name of a party, or all of its words belong to a person or
company name inside its own definition (the Mercury rule). A term that only the
detector flags stays readable.

**The governing-law place.** A place on the owner's closed list stays readable.
A suggestion that runs into the place is cut at its edges, except a person or
company span, which stays whole.

**The sentence cut.** A detector span that crosses a sentence start is cut at
the start, and each piece is kept. A piece that is only white space is dropped.

**Variant grouping.** The variants of one name share one entity by default.
Numbers run by kind in order of first appearance. A short form that fits two or
more full names gets its own placeholder, because code never guesses.

**Tokens and numbering.** Each entity becomes one token such as
`⟦Person 1⟧`. The number starts at 1 for each kind.

**The escape form.** The marker character `⟦` becomes `[` and `⟧` becomes `]`.
Each marker is its own `ESCAPE` segment; every other run of characters is a
`COPY` segment.

**Restoring a reply.** `restore_reply` puts back the contract text of the
entity's first place, which is the place with the smallest start.

**Mapping an edge.** `map_to_original` snaps an edge that falls inside a
placeholder out to the whole name.

**Real names.** The entities and the segment map hold real names from the
contract. They must stay out of logs and error messages.

## The printed report
The line kinds come in this order: `source`, `counts`, each `entity`, each
`span`, then each `text` line. The fields after the first word are:

| Line | Fields after the first word |
| --- | --- |
| `source` | the source name, then the source length |
| `counts` | `entities N`, `spans N`, `segments N` |
| `entity` | the id, the label and number (`Person 1`), then `places N` |
| `span` | the entity id, `start-end`, then the original text of the span |
| `text` | one piece of the placeholder text, one line for each piece between line breaks |

Every free-text field has each tab, carriage return and line break replaced by
one space.

The `span` lines hold the original text of each name, so the report of a real
contract holds real names. The report is for the developer and for the invented
sample. Do not send it to a log.

## Sample fixture
`sample_input.py` holds the input of `find_personal_data` for the sample: the
document, its clauses, the typed parties and the defined terms. `privacy` may not
import `ingest` or `links`, so the sample arrives as a committed JSON fixture and
a root test keeps it in step with both modules.

The format is `{"format": "clause-tracer-privacy-sample", "version": 1, ...}`
with these keys:

- `document`: `schema_version`, `source` (`name`, `kind`, `sha256`, `size`),
  `text` and `warnings` (`code`, `page`);
- `clauses`: `id`, `number`, `heading`, `level`, `parent_id`, `start`, `end`,
  `numbering_source` and `sentences` (`id`, `start`, `end`);
- `parties`: `name`, `address` and `yours`;
- `terms`: `term`, `definition` (`start`, `end`) and `uses` (`start`, `end`).

`dump_privacy_fixture` accepts text documents only: it refuses a document with
glyphs, pages or other non-text fields, and a source kind other than `text`,
`markdown` or `pasted`. `load_privacy_fixture` checks the JSON shape once at the
door. Both then run `_check_input`, which raises `ValueError` with the prefix
`privacy sample: ` on the first failure: a span outside the text, a level below
1, a duplicate clause or sentence id, a sentence outside its clause, a clause or
sentence out of order, or an empty party name.

The caller reads and writes the fixture. `privacy` code reads no file (T1).

`tests/goldens/` holds the expected report of the sample, written only by
`--update-goldens`.

## Known limits
- A person who is not a typed party and has no honorific, signature or job title
  is found only by the detector.
- A name or an address that wraps over a line break is found by the typed party
  finder only.
- A lower-priority suggestion is cut, so the part outside a kept span may be a
  fragment; punctuation-only fragments are dropped.
- An `NER` match does not remove a defined term from the allow-list.
- Only `Ltd` and `Limited` swap.
- The address rule reads UK, US, Canadian and street-word styles. An address
  chain longer than 5 comma segments or 120 characters keeps its last part
  hidden (the nearest segments before the postcode, at most 5 and at most 120
  characters) and its earlier part readable. A chain whose nearest segment
  alone passes 120 characters gives the postcode alone.
- IBAN length per country is not checked.
- A name with an apostrophe or a hyphen (`O'Neil`, `Anne-Marie`) can be found in
  part: a one-word form such as `Neil` or `Anne` matches the word on one side of
  the mark, and the rest of the name stays readable. Only the check on real
  contracts closes this limit.
- A company name, a person name or a street word that starts with a capital
  outside Latin-1, such as `Łukasz` or a Greek or Cyrillic name, is not found:
  the patterns read A to Z and the Latin-1 capitals.
- A US state code that is also a word (`ID`, `OK`, `OR`, `IN`, `ME`, `HI`, `LA`,
  `DE`) before five digits is replaced as a ZIP, so `Employee ID 12345` becomes
  an address (owner decision of 22 Nov 2026).
- An honorific before a company name stays inside the company span (`Mr
  Brightline Studio Ltd`).
- A company name with a comma before `NV` (`Delta, NV`) is not found, because
  `NV` is also the US state Nevada. `Delta, N.V.` and `Delta NV` are found.
- Non-UK bank formats and national ID numbers other than the NINO are left to
  the detector.
- A bare 8-digit company number needs a keyword, and only the 15 prefixes of
  `COMPANY_PREFIX` are found.
- A GB VAT number is found bare only with the `GB` prefix.
- A cue-less number that passes the Luhn check and starts with 3, 4, 5 or 6 is
  replaced as a card, and a card in 4-6-5 spacing is not found.
- A NINO in lower case is not found.
- The governing-law rule keeps only the places of a closed list that the owner
  writes, and two wordings of the clause.
- A phone shape with no cue gate also replaces a reference such as
  `ref 0123 456 7890`.
- A keyword ID value can run into a following number (`1234567 5`).
- A common-word name (layer 3) at the start of a sentence stays readable when no
  honorific, `'s` or earlier use shows it is a name.
- A defined term that only the detector flags, with no finder naming the full
  name, stays readable (it is allowed).
- Only `NER` spans are joined when they overlap.

## Depends on
core only. The detector is passed in by cli.

## Run alone
`.venv/bin/uv run python -m clause_tracer.privacy`

Use `--input <path>` to read another privacy fixture.
