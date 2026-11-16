"""The scan word lists and length caps, copied from the owner's table.

The owner owns the values (Constitution T11): they live in the owner
table scans.toml, and a test checks that this code copy matches it.
The code never edits the table.
"""

from collections.abc import Mapping
from types import MappingProxyType

from clause_tracer.core.enums import TextSlot

LAW_WORDS: tuple[str, ...] = (
    "legal",
    "illegal",
    "lawful",
    "unlawful",
    "enforceable",
    "unenforceable",
    "the law",
)
ADVICE_PHRASES: tuple[str, ...] = (
    "safe to sign",
    "you should sign",
    "do not sign",
    "don't sign",
    "we recommend",
)
INJECTION_PHRASES: tuple[str, ...] = (
    "ignore",
    "disregard",
    "mark every",
    "system prompt",
)
CONTACT_WORDS: tuple[str, ...] = ("call", "visit")
FIRST_PERSON_WORDS: tuple[str, ...] = (
    "I",
    "I'm",
    "I'd",
    "I'll",
    "I've",
    "we",
    "we're",
    "we'd",
    "we'll",
    "we've",
    "my",
    "our",
)
FILLER_PHRASES: tuple[str, ...] = (
    "certainly",
    "here is",
    "here's",
    "I hope",
    "it's important to note",
    "please note",
    "overall",
    "in summary",
    "as an AI",
    "feel free",
    "rest assured",
    "crucial",
    "ensure that",
)
EVALUATIVE_WORDS: tuple[str, ...] = (
    "fair",
    "unfair",
    "concerning",
    "problematic",
    "favourable",
    "standard",
    "typical",
    "risky",
)
ABBREVIATIONS: tuple[str, ...] = (
    "e.g.",
    "i.e.",
    "etc.",
    "approx.",
    "no.",
    "cl.",
    "mr.",
    "mrs.",
    "ms.",
    "dr.",
    "vs.",
)

LENGTH_CAPS: Mapping[TextSlot, int] = MappingProxyType(
    {
        TextSlot.REASON: 280,
        TextSlot.READING: 200,
        TextSlot.QUESTION: 200,
        TextSlot.MESSAGE: 3000,
        TextSlot.REWRITE: 2000,
    }
)
