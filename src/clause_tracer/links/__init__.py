"""Map cross-references, defined terms and override clauses between clauses.

Implements Spec section 6.1 step 5.
"""

from clause_tracer.links.sample_clauses import (
    SampleInput,
    dump_clause_fixture,
    load_clause_fixture,
)

__all__: list[str] = [
    "SampleInput",
    "dump_clause_fixture",
    "load_clause_fixture",
]
