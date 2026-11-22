"""Find personal data in clauses and turn it into placeholder text.

Implements Spec section 6.1 steps 3-4; 8.
"""

from clause_tracer.privacy.entities import group_entities
from clause_tracer.privacy.finding import find_personal_data
from clause_tracer.privacy.placeholder import (
    anonymise,
    map_to_original,
    restore_reply,
    restore_text,
)
from clause_tracer.privacy.render import render_privacy_report
from clause_tracer.privacy.sample_input import (
    PrivacyInput,
    dump_privacy_fixture,
    load_privacy_fixture,
)

__all__: list[str] = [
    "PrivacyInput",
    "anonymise",
    "dump_privacy_fixture",
    "find_personal_data",
    "group_entities",
    "load_privacy_fixture",
    "map_to_original",
    "render_privacy_report",
    "restore_reply",
    "restore_text",
]
