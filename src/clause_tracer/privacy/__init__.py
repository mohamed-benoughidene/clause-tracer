"""Find personal data in clauses and turn it into placeholder text.

Implements Spec section 6.1 steps 3-4; 8.
"""

from clause_tracer.privacy.sample_input import (
    PrivacyInput,
    dump_privacy_fixture,
    load_privacy_fixture,
)

__all__: list[str] = [
    "PrivacyInput",
    "dump_privacy_fixture",
    "load_privacy_fixture",
]
