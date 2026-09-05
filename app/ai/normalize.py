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
