from app.ai import tools


def test_get_product_details_by_id():
    result = tools.get_product_details(product_id="NVT-GLP-004")
    assert result["found"] is True
    assert result["product"]["name"] == "Gaming X1"
    assert result["product"]["price_egp"] == 45000


def test_get_product_details_by_exact_name():
    result = tools.get_product_details(name="Gaming X1")
    assert result["found"] is True
    assert result["product"]["id"] == "NVT-GLP-004"


def test_get_product_details_unknown_id_reports_not_found():
    result = tools.get_product_details(product_id="NOPE-000")
    assert result == {"found": False}


def test_get_product_details_franco_arabic_name_is_not_guessed():
    # No lexical bridge between Arabic-script tokens and the Latin
    # product name - this tool must not guess; RAG/search_knowledge_base
    # is the fallback for this case, not silent invention here.
    result = tools.get_product_details(name="الجيمنج اكس")
    assert result == {"found": False}


def test_search_products_use_case_programming_maps_to_expected_categories():
    result = tools.search_products(use_case="programming", limit=3)
    assert result["count"] > 0
    assert len(result["results"]) == 3
    assert all(p["category_id"] in ("LAP", "GLP") for p in result["results"])


def test_search_products_unrecognized_use_case_does_not_zero_results():
    # Regression test: an unrecognized use_case used to force allowed_ids
    # to an empty set, silently matching nothing.
    result = tools.search_products(use_case="coding")
    assert result["count"] > 0


def test_search_products_string_max_price_is_coerced_not_crashed():
    result = tools.search_products(max_price="25000", limit=50)
    assert result["count"] > 0
    assert all(p["price_egp"] <= 25000 for p in result["results"])


def test_search_products_garbage_max_price_is_ignored_not_crashed():
    result = tools.search_products(max_price="not-a-number", limit=2)
    assert result["count"] > 0


def test_search_products_string_limit_is_coerced():
    result = tools.search_products(limit="3")
    assert len(result["results"]) == 3


def test_search_products_nonexistent_category_returns_empty_not_invented():
    result = tools.search_products(keywords="موبايل")
    assert result == {"count": 0, "results": []}


def test_search_products_results_sorted_by_price_ascending():
    result = tools.search_products(category="لابتوبات ألعاب", limit=20)
    prices = [p["price_egp"] for p in result["results"]]
    assert prices == sorted(prices)


def test_search_branches_by_city_name_embedded_in_branch_name():
    # Regression test for the city_ar/name_ar bug: Tanta's city_ar is
    # "الغربية", the governorate - "طنطا" only appears in name_ar.
    result = tools.search_branches(city="طنطا")
    assert result["count"] == 1
    assert result["results"][0]["name"] == "فرع طنطا"


def test_search_branches_no_filters_returns_all_branches():
    result = tools.search_branches()
    assert result["count"] == 13


def test_search_branches_unknown_city_returns_empty():
    result = tools.search_branches(city="برلين")
    assert result == {"count": 0, "results": []}


def test_search_services_by_category():
    result = tools.search_services(category="صيانة")
    assert result["count"] > 0
    assert all("صيانة" in s["category"] for s in result["results"])


def test_search_offers_limit_caps_results_but_reports_true_count():
    result = tools.search_offers(limit=3)
    assert result["count"] == 25
    assert len(result["results"]) == 3


def test_search_offers_all_category_offers_match_any_category_filter():
    result = tools.search_offers(category="لابتوبات ألعاب", limit=25)
    assert result["count"] > 0
    matched_ids = {offer["id"] for offer in result["results"]}
    # OFF-02 applies_to_categories == "all" - must be included regardless
    # of the specific category filter requested.
    assert "OFF-02" in matched_ids


def test_tool_specs_and_functions_are_in_sync():
    spec_names = {spec["function"]["name"] for spec in tools.TOOL_SPECS}
    assert spec_names == set(tools.TOOL_FUNCTIONS.keys())
