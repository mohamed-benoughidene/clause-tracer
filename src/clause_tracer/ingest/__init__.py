"""Read the contract file and split it into numbered clauses.

Implements Spec section 6.1 steps 1-2.
"""

from clause_tracer.ingest.reading import (
    DOCUMENT_SCHEMA_VERSION,
    read_text_file,
)

__all__: list[str] = [
    "DOCUMENT_SCHEMA_VERSION",
    "read_text_file",
]
