"""The regular expressions that the finders share (S4-M1-T6)."""

import re
from typing import Final

HONORIFIC_BEFORE: Final[str] = r"\b(?:Mr|Mrs|Ms|Miss|Mx|Dr)\.?[ \t]+$"
HONORIFIC_BEFORE_RE: Final[re.Pattern[str]] = re.compile(HONORIFIC_BEFORE)
CLAUSE_NUMBER: Final[str] = r"^[ \t]*(?:\(?[0-9A-Za-z]{1,3}[.)]|\d+(?:\.\d+)*\.?)[ \t]+$"
CLAUSE_NUMBER_RE: Final[re.Pattern[str]] = re.compile(CLAUSE_NUMBER)
SENTENCE_MARK: Final[str] = r"[.!?]"
SENTENCE_MARK_RE: Final[re.Pattern[str]] = re.compile(SENTENCE_MARK)
HEADING_WORD: Final[str] = r"[^\W\d_][\w'’-]*"
HEADING_WORD_RE: Final[re.Pattern[str]] = re.compile(HEADING_WORD)

EMAIL: Final[str] = r"[\w.%+-]+@[\w-]+(?:\.[\w-]+)+"
EMAIL_RE: Final[re.Pattern[str]] = re.compile(EMAIL)
PHONE: Final[str] = (
    r"(?<![\w+])(?:\+\d{1,3}[ -]?(?:\(0\))?\d[\d -]{6,14}\d"
    r"|0\d{2,4}[ -]\d{3,4}[ -]?\d{3,4}"
    r"|\(0\d{2,4}\)[ -]?\d{3,4}[ -]?\d{3,4}"
    r"|0\d{10})(?!\w)"
)
PHONE_RE: Final[re.Pattern[str]] = re.compile(PHONE)
ID_KEYWORD: Final[str] = (
    r"(?i:company (?:registration )?(?:number|no\.?)|registered (?:number|no\.?)"
    r"|registration (?:number|no\.?)"
    r"|vat (?:registration )?(?:number|no\.?)|tax id)[ \t]*(?:is|:|of)?[ \t]*"
    r"(?P<v>(?:GB[ ]?)?[A-Z]{0,2}\d[\d ]{3,12}\d)"
)
ID_KEYWORD_RE: Final[re.Pattern[str]] = re.compile(ID_KEYWORD)
SORT_CODE: Final[str] = r"(?i:sort[ ]code)[ \t]*:?[ \t]*(?P<v>\d{2}-?\d{2}-?\d{2})(?!\d)"
SORT_CODE_RE: Final[re.Pattern[str]] = re.compile(SORT_CODE)
ACCOUNT_NUMBER: Final[str] = r"(?i:account[ ](?:number|no\.?))[ \t]*:?[ \t]*(?P<v>\d{8})(?!\d)"
ACCOUNT_NUMBER_RE: Final[re.Pattern[str]] = re.compile(ACCOUNT_NUMBER)
IBAN: Final[str] = (
    r"(?<![A-Za-z0-9])[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){2,7}(?:[ ]?[A-Z0-9]{1,3})?(?![A-Za-z0-9])"
)
IBAN_RE: Final[re.Pattern[str]] = re.compile(IBAN)
NINO: Final[str] = (
    r"\b(?!BG|GB|NK|KN|NT|TN|ZZ)[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]"
    r"(?:[ ]?\d{2}){3}[ ]?[A-D]\b"
)
NINO_RE: Final[re.Pattern[str]] = re.compile(NINO)
GB_VAT: Final[str] = r"(?<![A-Za-z0-9])GB[ ]?\d{3}[ ]?\d{4}[ ]?\d{2}(?:[ ]?\d{3})?(?![A-Za-z0-9])"
GB_VAT_RE: Final[re.Pattern[str]] = re.compile(GB_VAT)
COMPANY_PREFIX: Final[str] = (
    r"(?<![A-Za-z0-9])(?:SC|NI|OC|SO|NC|LP|SL|NL|FC|R0|IP|SP|RS|CE|NP)\d{6}(?![A-Za-z0-9])"
)
COMPANY_PREFIX_RE: Final[re.Pattern[str]] = re.compile(COMPANY_PREFIX)
CARD: Final[str] = r"(?<![\d-])\d{4}(?:[ -]?\d{4}){2}[ -]?\d{1,7}(?![\d-])"
CARD_RE: Final[re.Pattern[str]] = re.compile(CARD)
CARD_CUE: Final[str] = r"(?i:\b(?:card|visa|mastercard|amex)\b)"
CARD_CUE_RE: Final[re.Pattern[str]] = re.compile(CARD_CUE)
CARD_CUE_WINDOW: Final[int] = 40
CARD_FIRST_DIGITS: Final[str] = "3456"
GB_VAT_WEIGHTS: Final[tuple[int, ...]] = (8, 7, 6, 5, 4, 3, 2, 10, 1)
H: Final[str] = r"[ \t]"
UPPER: Final[str] = "A-ZÀ-ÖØ-Þ"
LOWER: Final[str] = "a-zß-öø-ÿ"
WORD: Final[str] = rf"[{UPPER}][\w'’&-]*"
SUFFIX_WORDS: Final[str] = (
    r"(?:Ltd|Plc|PLC|LLC|LLP|LP|Inc|Corp|Corporation|Incorporated|GmbH|AG|SARL|SAS|BV|NV"
    r"|Pty|SRL|SpA|Oy|KG|UG|Pte|Co)"
)
SUFFIX: Final[str] = (
    r"(?:S\.A\.R\.L\.|L\.L\.C\.|L\.L\.P\.|P\.L\.C\.|S\.A\.|N\.V\.|B\.V\."
    rf"|Co\.?{H}+KG(?![-\w])|Pte{H}+Ltd(?![-\w])"
    rf"|Limited(?![-\w])(?!{H}+(?:Liability|Warranty|Partnership|Licen[cs]e))"
    rf"|{SUFFIX_WORDS}(?![-\w]))"
)
CONNECTOR: Final[str] = (
    rf"(?:GmbH(?={H}+&{H}+Co\b)|(?!(?:{SUFFIX_WORDS}|Limited)(?![-\w])){WORD}|&|of|and)"
)
COMPANY: Final[str] = (
    rf"(?<![\w]){WORD}(?:{H}+{CONNECTOR}){{0,5}}"
    rf"(?:,(?!{H}+NV(?![-\w])))?{H}+{SUFFIX}"
)
COMPANY_RE: Final[re.Pattern[str]] = re.compile(COMPANY)
ENDING_AFTER: Final[str] = rf"(?:,(?!{H}+NV(?![-\w])))?{H}+{SUFFIX}"
ENDING_AFTER_RE: Final[re.Pattern[str]] = re.compile(ENDING_AFTER)
CAP: Final[str] = rf"(?:[{UPPER}][{LOWER}'’-]+|UK|USA|UAE)"
STREET_PLAIN: Final[str] = r"(?:Street|St|Road|Rd|Avenue|Ave|Lane|Terrace|Gardens|Boulevard)"
STREET_AMBIG: Final[str] = r"(?:Way|Place|Court|Row|Hill|Close|Drive|Square)"
LEAD_WORD: Final[str] = r"(?:Rue|Avenue|Boulevard|Via|Calle|Strasse|Chemin|Allée)"
POST: Final[str] = r"(?:[A-Z]{1,2}\d[A-Z\d]?[ ]?\d[A-Z]{2}|\d{4,6})"
PART: Final[str] = rf",{H}*{CAP}(?:{H}+{CAP}){{0,2}}(?:{H}+{POST})?"
ADDRESS: Final[str] = (
    rf"\b\d+[A-Za-z]?{H}+(?:{CAP}{H}+){{0,3}}{STREET_PLAIN}\b(?:{PART}){{0,3}}"
    rf"|\b\d+[A-Za-z]?{H}+(?:{CAP}{H}+){{1,3}}{STREET_AMBIG}\b(?:{PART}){{0,3}}"
    rf"|\b\d+[A-Za-z]?{H}+{LEAD_WORD}{H}+{CAP}(?:{H}+{CAP}){{0,3}}(?:{PART}){{0,3}}"
)
ADDRESS_RE: Final[re.Pattern[str]] = re.compile(ADDRESS)
UK_POSTCODE: Final[str] = (
    r"\b(?:GIR ?0AA|[A-PR-UWYZ](?:[0-9]{1,2}|[A-HK-Y][0-9]{1,2}"
    r"|[0-9][A-HJKPSTUW]|[A-HK-Y][0-9][ABEHMNPRV-Y])[ ]?[0-9][ABD-HJLNP-UW-Z]{2})\b"
)
UK_POSTCODE_RE: Final[re.Pattern[str]] = re.compile(UK_POSTCODE)
US_ZIP: Final[str] = (
    r"\b(?:A[LKZR]|C[AOT]|DE|FL|GA|HI|I[DLNA]|K[SY]|LA|M[EDAINSOT]|N[EVHJMYCD]"
    r"|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])"
    r"[ ]\d{5}(?:-\d{4})?\b"
)
US_ZIP_RE: Final[re.Pattern[str]] = re.compile(US_ZIP)
CA_POSTCODE: Final[str] = r"\b[A-Z]\d[A-Z][ ]?\d[A-Z]\d\b"
CA_POSTCODE_RE: Final[re.Pattern[str]] = re.compile(CA_POSTCODE)
MONTHS: Final[str] = (
    r"(?:January|February|March|April|May|June"
    r"|July|August|September|October|November|December)"
)
START_TOKEN: Final[str] = (
    r"(?:Flat|Unit|Suite|Floor|Room|Building)[ ]+\w+|PO Box[ ]+\d+"
    rf"|\d+[A-Za-z]?(?:-\d+)?(?=[ ]+(?!{MONTHS}\b)[A-Z][a-z])"
)
START_TOKEN_RE: Final[re.Pattern[str]] = re.compile(START_TOKEN)
CUE: Final[str] = (
    r"(?i:registered office (?:is )?at|registered address (?:is )?at"
    r"|address is|located at|whose address is|whose address)[ \t]+"
)
CUE_RE: Final[re.Pattern[str]] = re.compile(CUE)
TAIL: Final[str] = (
    rf",?{H}*(?:United Kingdom|UK|England|Scotland|Wales|Northern Ireland"
    r"|USA|United States|Canada)\b"
)
TAIL_RE: Final[re.Pattern[str]] = re.compile(TAIL)
HARD_STOP: Final[str] = r"[;:()\[\]\"“”\n]|[.!?](?=\s+[A-Z0-9])"
HARD_STOP_RE: Final[re.Pattern[str]] = re.compile(HARD_STOP)
ABBREVIATION_END: Final[str] = r"\b(?:St|Rd|Ave|Dr|Ln|Ct|Sq|Mt)$"
ABBREVIATION_END_RE: Final[re.Pattern[str]] = re.compile(ABBREVIATION_END)
PARTICLE: Final[str] = r"(?:van|von|der|den|de|la|le|da|di|del|bin|ibn|bint|ben|ould|dos|du|al|el)"
TOK: Final[str] = (
    rf"(?:[{UPPER}](?:['’][{UPPER}])?[{LOWER}]+(?:[{UPPER}][{LOWER}]+)*(?:-[{UPPER}]?[{LOWER}]+)*"
    rf"|(?:al|el)-[{UPPER}][{LOWER}]+)"
)
INIT: Final[str] = rf"(?:[{UPPER}]\.)"
NAME_RUN: Final[str] = rf"{TOK}(?:{H}+(?:{INIT}{H}+|{PARTICLE}{H}+)*{TOK}){{1,3}}"
ONE_OR_TWO: Final[str] = rf"{TOK}(?:{H}+(?:{INIT}{H}+|{PARTICLE}{H}+)*{TOK})?"
CAPS_TOK: Final[str] = rf"[{UPPER}]{{2,}}(?:['’-][{UPPER}]+)*"
CAPS_RUN: Final[str] = rf"{CAPS_TOK}(?:{H}+{CAPS_TOK}){{1,2}}"
CAPS_ONE_OR_TWO: Final[str] = rf"{CAPS_TOK}(?:{H}+{CAPS_TOK})?"
TITLE_WORDS: Final[str] = (
    r"(?:Managing Director|Director|Manager|Partner|Owner|Secretary|Chief Executive Officer"
    r"|CEO|CFO|Chairman|President)"
)
HONORIFIC_PERSON: Final[str] = rf"\b(?:Mr|Mrs|Ms|Miss|Mx|Dr)\.?{H}+({ONE_OR_TWO})"
HONORIFIC_PERSON_RE: Final[re.Pattern[str]] = re.compile(HONORIFIC_PERSON)
HONORIFIC_PERSON_CAPS: Final[str] = rf"\b(?:MR|MRS|MS|MISS|MX|DR)\.?{H}+({CAPS_ONE_OR_TWO})"
HONORIFIC_PERSON_CAPS_RE: Final[re.Pattern[str]] = re.compile(HONORIFIC_PERSON_CAPS)
SIGNED_BY: Final[str] = rf"\b(?:Signed|Executed)\b[^.\n]*?\bby{H}+({NAME_RUN})"
SIGNED_BY_RE: Final[re.Pattern[str]] = re.compile(SIGNED_BY)
SIGNED_BY_CAPS: Final[str] = rf"(?i:signed|executed)\b[^.\n]*?\b(?i:by){H}+({CAPS_RUN})"
SIGNED_BY_CAPS_RE: Final[re.Pattern[str]] = re.compile(SIGNED_BY_CAPS)
NAME_BEFORE_TITLE: Final[str] = rf"({NAME_RUN}){H}*,{H}*{TITLE_WORDS}\b"
NAME_BEFORE_TITLE_RE: Final[re.Pattern[str]] = re.compile(NAME_BEFORE_TITLE)

GOVERNING_LAW_CUE: Final[str] = (
    r"(?i:governed by,?(?: and construed in accordance with,?)? the laws? of)[ \t]+"
    r"(?:the[ \t]+)?"
)
PLACE_END: Final[str] = r"(?![A-Za-z])"
