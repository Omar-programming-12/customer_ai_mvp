from app.ai import entities, rag


def test_category_vocabulary_contains_curated_synonyms():
    vocab = entities.build_category_vocabulary()
    assert "لابتوب" in vocab
    assert "جهاز" in vocab
    assert "لاب" in vocab


def test_category_vocabulary_excludes_denylisted_connector_word():
    vocab = entities.build_category_vocabulary()
    assert "بعد" not in vocab


def test_is_company_domain_query_matches_known_terms():
    vocab = rag.company_category_vocabulary
    assert entities.is_company_domain_query("عايز جهاز للبرمجة", vocab)
    assert entities.is_company_domain_query("رشحلي لاب كويس", vocab)


def test_is_company_domain_query_rejects_unrelated_text():
    vocab = rag.company_category_vocabulary
    assert not entities.is_company_domain_query("قولي نكتة حلوة", vocab)


def test_branch_anchor_matches_tanta_by_name_not_governorate():
    # Regression test: Tanta's city_ar field is "الغربية" (the
    # governorate) - only name_ar ("فرع طنطا") contains "طنطا" itself.
    matches = entities.find_anchor_matches(
        "انتو فاتحين في طنطا؟", rag.company_entity_anchors
    )
    assert "فرع طنطا" in [m["label"] for m in matches]


def test_branch_anchor_matches_aswan_with_and_without_hamza():
    with_hamza = entities.find_anchor_matches(
        "عندكم فرع في أسوان؟", rag.company_entity_anchors
    )
    without_hamza = entities.find_anchor_matches(
        "عندكم فرع في اسوان؟", rag.company_entity_anchors
    )
    assert "فرع أسوان" in [m["label"] for m in with_hamza]
    assert "فرع أسوان" in [m["label"] for m in without_hamza]


def test_branch_anchor_no_match_for_unrelated_question():
    matches = entities.find_anchor_matches("احكيلي نكتة", rag.company_entity_anchors)
    assert matches == []
