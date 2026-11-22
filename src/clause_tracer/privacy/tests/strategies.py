"""Planted cases and the property-test strategies (S4-M3-T11).

Test code, not exported from `privacy`. The hazard alphabet comes from `core`,
so every strategy uses the same characters that break offsets and folds.
"""

from dataclasses import dataclass
from typing import Final

from hypothesis import HealthCheck, settings
from hypothesis import strategies as st
from hypothesis.strategies import DrawFn, SearchStrategy, composite

from clause_tracer.core.enums import PiiSource, PlaceholderKind
from clause_tracer.core.placeholders import PiiSuggestion
from clause_tracer.core.tests.strategies import HAZARD_ALPHABET
from clause_tracer.core.wording import Span
from clause_tracer.privacy._spans import trimmed_span
from clause_tracer.privacy.resolve import resolve_overlaps, trim_suggestions
from clause_tracer.privacy.sample_input import PrivacyInput
from clause_tracer.privacy.tests.case_builder import make_case

PERSON: Final = PlaceholderKind.PERSON
COMPANY: Final = PlaceholderKind.COMPANY
ADDRESS: Final = PlaceholderKind.ADDRESS
EMAIL: Final = PlaceholderKind.EMAIL

POOL: Final[tuple[tuple[str, PlaceholderKind], ...]] = (
    ("Sarah Jones", PERSON),
    ("Ms Jones", PERSON),
    ("Sarah", PERSON),
    ("Zoë Brown", PERSON),
    ("Zed Corp", COMPANY),
    ("Brightline Studio", COMPANY),
    ("14 Harbour Street, Leeds LS1 4AB", ADDRESS),
    ("a@b.com", EMAIL),
)

PLAIN_ALPHABET: Final[tuple[str, ...]] = tuple(
    character for character in HAZARD_ALPHABET if not character.isspace()
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PlantedCase:
    """One generated case, the suggestions planted in it, and the names used."""

    case: PrivacyInput
    planted: tuple[PiiSuggestion, ...]
    names: tuple[str, ...]


@composite
def planted_cases(draw: DrawFn) -> PlantedCase:
    """Sentences of names and plain text, with one detector span per name."""

    sentences: list[str] = []
    planted: list[PiiSuggestion] = []
    names: list[str] = []
    for _ in range(draw(st.integers(1, 4))):
        parts: list[str] = []
        local: list[tuple[int, int, PlaceholderKind, str]] = []
        position = 0
        for _ in range(draw(st.integers(1, 5))):
            if parts:
                position += 1
            if draw(st.booleans()):
                name, kind = draw(st.sampled_from(POOL))
                local.append((position, position + len(name), kind, name))
                parts.append(name)
                position += len(name)
            else:
                plain = draw(st.text(alphabet=PLAIN_ALPHABET, min_size=1, max_size=6))
                parts.append(plain)
                position += len(plain)
        sentence = " ".join(parts)
        start = sum(len(item) + 1 for item in sentences)
        for span_start, span_end, kind, name in local:
            planted.append(
                PiiSuggestion(
                    span=Span(start=start + span_start, end=start + span_end),
                    kind=kind,
                    source=PiiSource.NER,
                )
            )
            names.append(name)
        sentences.append(sentence)
    if len(sentences) >= 2 and draw(st.booleans()):
        index = draw(st.integers(0, len(sentences) - 2))
        start = sum(len(item) + 1 for item in sentences[: index + 1])
        planted.append(
            PiiSuggestion(
                span=Span(start=start - 2, end=start + 1),
                kind=ADDRESS,
                source=PiiSource.NER,
            )
        )
    return PlantedCase(
        case=make_case(sentences),
        planted=tuple(planted),
        names=tuple(names),
    )


ALPHABET: Final[tuple[str, ...]] = tuple(HAZARD_ALPHABET) + (".", ",", "(", ")", " ", "A", "b")
LAW_PLAIN_ALPHABET: Final[tuple[str, ...]] = tuple(c for c in ALPHABET if not c.isspace())
LAW_POOL: Final[tuple[tuple[str, PlaceholderKind], ...]] = POOL + (
    ("England and Wales", ADDRESS),
    ("Wales", ADDRESS),
    ("Sam", PERSON),
)
LAW_SENTENCE: Final[str] = "This is governed by the laws of England and Wales."
SETTINGS: Final[settings] = settings(
    max_examples=1000, deadline=None, suppress_health_check=list(HealthCheck), database=None
)
TEXTS: Final[SearchStrategy[str]] = st.text(alphabet=ALPHABET, max_size=40)
OFFSETS: Final[SearchStrategy[object]] = st.one_of(
    st.integers(-3, 25),
    st.booleans(),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-3, max_value=25),
    st.none(),
)


@composite
def with_suggestions(draw: DrawFn) -> tuple[str, tuple[PiiSuggestion, ...]]:
    text = draw(TEXTS)
    raw: list[PiiSuggestion] = []
    for _ in range(draw(st.integers(0, 12))):
        a = draw(st.integers(0, len(text)))
        b = draw(st.integers(0, len(text)))
        raw.append(
            PiiSuggestion(
                span=Span(start=min(a, b), end=max(a, b)),
                kind=draw(st.sampled_from(list(PlaceholderKind))),
                source=draw(st.sampled_from(list(PiiSource))),
            )
        )
    return text, trim_suggestions(text, raw)


@composite
def clean_input(draw: DrawFn) -> tuple[str, tuple[PiiSuggestion, ...]]:
    text = draw(TEXTS)
    cuts = sorted(draw(st.lists(st.integers(0, len(text)), max_size=8)))
    kept: list[PiiSuggestion] = []
    for a, b in zip(cuts[::2], cuts[1::2], strict=False):
        span = trimmed_span(text, Span(start=a, end=b))
        if (
            span
            and any(c.isalnum() for c in text[span.start : span.end])
            and (not kept or kept[-1].span.end <= span.start)
        ):
            kept.append(
                PiiSuggestion(
                    span=span,
                    kind=draw(st.sampled_from(list(PlaceholderKind))),
                    source=draw(st.sampled_from(list(PiiSource))),
                )
            )
    return text, tuple(kept)


@composite
def with_starts(draw: DrawFn) -> tuple[str, tuple[PiiSuggestion, ...], list[int]]:
    text, suggestions = draw(with_suggestions())
    starts = sorted(set(draw(st.lists(st.integers(0, len(text)), max_size=8))))
    return text, resolve_overlaps(text, suggestions), starts


@composite
def law_cases(draw: DrawFn) -> PlantedCase:
    """Cases that hold the governing-law sentence, for properties P11 and P12."""

    sentences: list[str] = []
    planted: list[PiiSuggestion] = []
    names: list[str] = []
    law_indexes: list[int] = []
    for _ in range(draw(st.integers(1, 4))):
        is_law_sentence = draw(st.booleans()) and draw(st.integers(0, 3)) == 0
        if is_law_sentence:
            law_indexes.append(len(sentences))
            sentences.append(LAW_SENTENCE)
            continue
        parts: list[str] = []
        local: list[tuple[int, int, PlaceholderKind, str]] = []
        position = 0
        for _ in range(draw(st.integers(1, 5))):
            if parts:
                position += 1
            if draw(st.booleans()):
                name, kind = draw(st.sampled_from(LAW_POOL))
                local.append((position, position + len(name), kind, name))
                parts.append(name)
                position += len(name)
            else:
                plain = draw(st.text(alphabet=LAW_PLAIN_ALPHABET, min_size=1, max_size=6))
                parts.append(plain)
                position += len(plain)
        sentence = " ".join(parts)
        start = sum(len(item) + 1 for item in sentences)
        for span_start, span_end, kind, name in local:
            planted.append(
                PiiSuggestion(
                    span=Span(start=start + span_start, end=start + span_end),
                    kind=kind,
                    source=PiiSource.NER,
                )
            )
            names.append(name)
        sentences.append(sentence)

    starts: list[int] = []
    offset = 0
    for sentence in sentences:
        starts.append(offset)
        offset += len(sentence) + 1

    for index in law_indexes:
        base = starts[index]
        if draw(st.booleans()):
            planted.append(
                PiiSuggestion(
                    span=Span(
                        start=base + LAW_SENTENCE.index("laws"),
                        end=base + LAW_SENTENCE.index("Wales") + len("Wales"),
                    ),
                    kind=draw(st.sampled_from(list(PlaceholderKind))),
                    source=draw(
                        st.sampled_from([PiiSource.NER, PiiSource.RULE, PiiSource.PATTERN])
                    ),
                )
            )
    if len(sentences) >= 2 and draw(st.booleans()):
        index = draw(st.integers(0, len(sentences) - 2))
        edge = starts[index + 1]
        planted.append(
            PiiSuggestion(
                span=Span(start=edge - 2, end=edge + 1),
                kind=ADDRESS,
                source=PiiSource.NER,
            )
        )

    text_length = len(" ".join(sentences))
    kept = tuple(item for item in planted if item.span.end <= text_length)
    return PlantedCase(case=make_case(sentences), planted=kept, names=tuple(names))
