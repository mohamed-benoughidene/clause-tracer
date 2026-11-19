"""Checks on Lingua itself, whose answer becomes the not-English warning."""

from importlib.metadata import version

from lingua import Language, LanguageDetectorBuilder

DETECTOR = LanguageDetectorBuilder.from_all_languages().build()

FRENCH = "Les factures sont payées dans un délai de soixante jours à compter de la date de facture."
ENGLISH = "Invoices will be paid within 60 days of the invoice date."


def test_lingua_version_is_pinned() -> None:
    assert version("lingua-language-detector") == "2.2.0"


def test_french_sentence() -> None:
    assert DETECTOR.detect_language_of(FRENCH) == Language.FRENCH


def test_english_sentence() -> None:
    assert DETECTOR.detect_language_of(ENGLISH) == Language.ENGLISH


def test_same_answer_twice() -> None:
    first = DETECTOR.detect_language_of(FRENCH)

    assert DETECTOR.detect_language_of(FRENCH) == first
