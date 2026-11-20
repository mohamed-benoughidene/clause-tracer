"""The not-English warning, with Lingua (ADR 0017; S2-M5-T4).

The language library is hidden in this file (B4). A contract that does not
look English is still read: the warning says so, and the user decides whether
to go on (Spec 9). A text shorter than MIN_WORDS_TO_JUDGE is never warned
about, because it is too short to tell.
"""

import functools
import re
from typing import Final

from lingua import Language, LanguageDetector, LanguageDetectorBuilder

WARNING_NOT_ENGLISH: Final[str] = "not_english"
MIN_WORDS_TO_JUDGE: Final[int] = 10  # [Assumption] tuned in testing.

_WORD: Final[re.Pattern[str]] = re.compile(r"[^\W\d_]+")


@functools.cache
def _detector() -> LanguageDetector:
    """The one detector, built on first use and reused after that."""

    return LanguageDetectorBuilder.from_all_languages().build()


def looks_not_english(text: str) -> bool:
    """True when a text holds enough words to judge and is not English.

    Input:   one text.
    Output:  False for a text shorter than MIN_WORDS_TO_JUDGE words, because it
             is too short to tell; otherwise True when Lingua names a language
             other than English. A text that Lingua cannot judge gives False.
    Effects: builds the detector on first use. No other side effect.
    """

    if len(_WORD.findall(text)) < MIN_WORDS_TO_JUDGE:
        return False
    language = _detector().detect_language_of(text)
    return language is not None and language != Language.ENGLISH
