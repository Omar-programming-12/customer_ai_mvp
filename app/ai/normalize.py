import re


_DIACRITICS_PATTERN = re.compile(r"[ؐ-ًؚ-ٟۖ-ٰۭ]")
_TATWEEL_PATTERN = re.compile(r"ـ")
_ALEF_VARIANTS_PATTERN = re.compile(r"[إأآا]")
_YEH_VARIANT_PATTERN = re.compile(r"ى")
_TEH_MARBUTA_PATTERN = re.compile(r"ة")
_NON_WORD_PATTERN = re.compile(r"[^\w]+", re.UNICODE)

_STOPWORDS = {
    "في", "من", "على", "الى", "إلى", "عن", "مع",
    "هل", "ما", "او", "أو", "ال", "يا", "لل", "و", "ف", "ب",
    "كام", "بكام", "فين", "ايه", "إيه",
    # Generic interrogative/filler words: they carry no topic-specific
    # meaning on their own, so treating them as content tokens lets a
    # question match any chunk that happens to share the same question
    # word (e.g. "كيف حالك؟" matching FAQ entries that start with "كيف").
    "كيف", "إزاي", "كم", "ماذا", "لماذا", "ليه", "متى", "اين", "أين", "مين"
}


def normalize_text(text: str) -> str:

    text = text.strip().lower()

    text = _DIACRITICS_PATTERN.sub("", text)
    text = _TATWEEL_PATTERN.sub("", text)
    text = _ALEF_VARIANTS_PATTERN.sub("ا", text)
    text = _YEH_VARIANT_PATTERN.sub("ي", text)
    text = _TEH_MARBUTA_PATTERN.sub("ه", text)

    return text


def tokenize(text: str) -> list[str]:

    normalized = normalize_text(text)

    raw_tokens = _NON_WORD_PATTERN.split(normalized)

    tokens = []

    for token in raw_tokens:

        if not token:
            continue

        if token in _STOPWORDS:
            continue

        if token.startswith("ال") and len(token) > 4:
            token = token[2:]

        tokens.append(token)

    return tokens


# Franco-Arabic ("Arabic chat alphabet") digit-for-letter and common
# digraph conventions. Approximate by nature - Franco-Arabic has no single
# standard spelling (e.g. ت/ط and س/ص are often both written with the
# plain Latin letter), so this aims for "close enough to help retrieval
# find something real", not a linguistically exact transliteration.
# Multi-character sequences are listed first and matched longest-first so
# "sh" becomes ش rather than س+ه.
_FRANCO_ARABIC_DIGRAPHS = [
    ("kh", "خ"), ("sh", "ش"), ("th", "ث"), ("gh", "غ"), ("dh", "ذ"),
]

_FRANCO_ARABIC_SINGLES = {
    "2": "ء", "3": "ع", "5": "خ", "6": "ط", "7": "ح", "8": "ق", "9": "ص",
    "a": "ا", "b": "ب", "t": "ت", "g": "ج", "j": "ج", "d": "د", "r": "ر",
    "z": "ز", "s": "س", "f": "ف", "q": "ق", "k": "ك", "l": "ل", "m": "م",
    "n": "ن", "h": "ه", "w": "و", "o": "و", "u": "و", "y": "ي", "i": "ي",
    "e": "ي", "c": "ك",
}


def transliterate_franco_arabic(text: str) -> str:
    """Best-effort Franco-Arabic -> Arabic-script transliteration, meant
    only as a fallback re-attempt for a message that scored no signal at
    all in its original form (see app.ai.router) - never as a blanket
    preprocessing step, since it would just as happily (and wrongly)
    mangle a legitimate English product name like "Gaming X1" or
    "laptop" into meaningless Arabic-looking text."""

    text = text.lower()

    for latin, arabic in _FRANCO_ARABIC_DIGRAPHS:
        text = text.replace(latin, arabic)

    return "".join(_FRANCO_ARABIC_SINGLES.get(char, char) for char in text)
