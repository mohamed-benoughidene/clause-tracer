"""Read the contract file and split it into numbered clauses.

Implements Spec section 6.1 steps 1-2.
"""

from clause_tracer.ingest.clauses import (
    NUMBERING_NUMBERS,
    NUMBERING_PARAGRAPHS,
    split_clauses,
)
from clause_tracer.ingest.files import read_file
from clause_tracer.ingest.language import WARNING_NOT_ENGLISH
from clause_tracer.ingest.reading import (
    DOCUMENT_SCHEMA_VERSION,
    read_pasted_text,
    read_text_file,
)
from clause_tracer.ingest.warnings import (
    WARNING_WORD_NOTES,
    WARNING_WORD_NUMBERING_UNKNOWN,
    WARNING_WORD_SYMBOL_UNREAD,
)
from clause_tracer.ingest.word import read_word_file

__all__: list[str] = [
    "DOCUMENT_SCHEMA_VERSION",
    "NUMBERING_NUMBERS",
    "NUMBERING_PARAGRAPHS",
    "WARNING_NOT_ENGLISH",
    "WARNING_WORD_NOTES",
    "WARNING_WORD_NUMBERING_UNKNOWN",
    "WARNING_WORD_SYMBOL_UNREAD",
    "read_file",
    "read_pasted_text",
    "read_text_file",
    "read_word_file",
    "split_clauses",
]
