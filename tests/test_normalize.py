import pytest

from app.ai.normalize import normalize_text, tokenize, transliterate_franco_arabic


def test_normalize_strips_diacritics_and_unifies_alef():
    assert normalize_text("أَحْمَد") == "احمد"
    assert normalize_text("إسلام").startswith("اسلام")


def test_normalize_unifies_teh_marbuta_and_yeh():
    assert normalize_text("مدرسة") == "مدرسه"
    assert normalize_text("مصطفى") == "مصطفي"


@pytest.mark.parametrize("message,forbidden_token", [
    ("هل عندكم فرع في القاهرة؟", "هل"),
    ("كيف حالك؟", "كيف"),
    ("بكام الجهاز؟", "بكام"),
])
def test_tokenize_removes_stopwords(message, forbidden_token):
    assert forbidden_token not in tokenize(message)


def test_tokenize_keeps_content_words():
    tokens = tokenize("هل عندكم فرع في القاهرة؟")
    assert "عندكم" in tokens
    assert "فرع" in tokens


def test_tokenize_strips_al_prefix_for_long_words():
    assert tokenize("الجيمنج") == ["جيمنج"]


def test_franco_arabic_digit_mapping():
    assert transliterate_franco_arabic("2") == "ء"
    assert transliterate_franco_arabic("3") == "ع"
    assert transliterate_franco_arabic("7") == "ح"


def test_franco_arabic_leaves_pure_arabic_effectively_unchanged():
    # No digits/Latin letters present, so nothing should be substituted.
    assert transliterate_franco_arabic("طنطا") == "طنطا"


def test_franco_arabic_transliterates_mixed_text():
    result = transliterate_franco_arabic("3andko far3?")
    assert result != "3andko far3?"
    assert "ع" in result
