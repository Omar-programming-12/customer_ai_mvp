"""Structured-data tools for the LLM (Groq function-calling).

Deterministic, pure-Python lookups directly over knowledge_base/*.json -
no Gemini/Groq calls, no semantic embeddings, no RAG involved. Each
function here can be called and tested directly with plain arguments, and
is also exposed to Groq as a callable "tool" (see TOOL_SPECS/TOOL_FUNCTIONS
below) so the model can request an exact structured fact - a price, a
spec, a branch's hours, the active offers - instead of inferring one from
loosely-related RAG context chunks.

knowledge_base/ is the only source of truth: nothing here hardcodes a
product, price, or branch - every tool re-reads the JSON files through
app.ai.knowledge_base's loaders on each call, the same loaders app.ai.rag
uses to build the RAG chunks. A knowledge_base/ edit takes effect for both
paths without any code change here.
"""

from app.ai.knowledge_base import (
    load_branches,
    load_categories,
    load_offers,
    load_products,
    load_services,
)
from app.ai.normalize import normalize_text, tokenize


_DEFAULT_LIMIT = 5
_MAX_LIMIT = 20


def _clamp_limit(limit: int | None) -> int:

    if not limit:
        return _DEFAULT_LIMIT

    return max(1, min(int(limit), _MAX_LIMIT))


def _token_overlap(haystack: str, needle_tokens: set[str]) -> bool:
    """True if any needle token appears among haystack's own tokens - the
    same tokenizer BM25 already uses (diacritics/alef/teh-marbuta
    normalization, stopword removal), so a tool's idea of a "match" stays
    consistent with the rest of the app's Arabic text handling."""

    if not needle_tokens:
        return True

    return bool(set(tokenize(haystack)) & needle_tokens)


# ==========================================
# 1 & 2. Products
# ==========================================

# Maps a natural-language use case onto the *existing* category ids
# already defined in knowledge_base/catalog/categories.json - this
# interprets customer intent, it does not invent a category, product, or
# price. categories.json remains the source of truth for what each id
# actually contains.
_USE_CASE_CATEGORY_IDS = {
    "gaming": ["GLP"],
    "programming": ["LAP", "GLP"],
    "study": ["LAP", "TAB"],
    "business": ["LAP"],
    "office": ["LAP", "DSK", "MPC"],
    "design": ["LAP", "DSK"],
}

_AVAILABILITY_STATUS_AR = {
    "in_stock": "متوفر",
    "limited": "كمية محدودة",
    "out_of_stock": "غير متوفر حاليًا",
}


def _category_lookup() -> dict[str, dict]:

    return {category["id"]: category for category in load_categories()}


def _resolve_category_ids(category: str | None, categories: dict[str, dict]) -> set[str] | None:
    """A category filter may come in as an id ("GLP"), an Arabic name
    ("لابتوبات ألعاب"), or an English name ("Gaming Laptops") - match any
    of them against the real categories.json entries, never a guess."""

    if not category:
        return None

    normalized = normalize_text(category)

    return {
        c["id"] for c in categories.values()
        if normalize_text(c["id"]) == normalized
        or normalized in normalize_text(c["name_ar"])
        or normalized in normalize_text(c["name_en"])
    }


def _format_product(product: dict, categories: dict[str, dict]) -> dict:

    category = categories.get(product["category_id"], {})

    return {
        "id": product["id"],
        "name": product["name"],
        "category": category.get("name_ar"),
        "category_id": product["category_id"],
        "price_egp": product["price_egp"],
        "specs": product["specs"],
        "status": product["status_ar"],
        "warranty_months": product["warranty_months"],
    }


def search_products(
    category: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    use_case: str | None = None,
    availability: str | None = None,
    keywords: str | None = None,
    limit: int | None = None,
) -> dict:
    """Filter knowledge_base/catalog/products.json by any combination of
    the given, all-optional criteria (combined with AND). Deterministic:
    same inputs always produce the same results, no ranking heuristics
    beyond a plain price-ascending sort.

    Returns {"count": int, "results": [product, ...]} - count is the
    number of matches BEFORE the limit was applied, so the caller (the
    LLM) can tell "only 3 exist" from "there are more than the 5 shown"."""

    categories = _category_lookup()

    allowed_ids = None

    if use_case:
        allowed_ids = set(_USE_CASE_CATEGORY_IDS.get(normalize_text(use_case), []))

    category_ids = _resolve_category_ids(category, categories)

    if category_ids is not None:
        allowed_ids = category_ids if allowed_ids is None else (allowed_ids & category_ids)

    keyword_tokens = set(tokenize(keywords)) if keywords else set()
    target_status = _AVAILABILITY_STATUS_AR.get(availability) if availability else None

    matches = []

    for product in load_products():

        if allowed_ids is not None and product["category_id"] not in allowed_ids:
            continue

        if max_price is not None and product["price_egp"] > max_price:
            continue

        if min_price is not None and product["price_egp"] < min_price:
            continue

        if target_status is not None and product["status_ar"] != target_status:
            continue

        if keyword_tokens:
            category_name = categories.get(product["category_id"], {}).get("name_ar", "")
            searchable_text = " ".join([
                product["name"],
                category_name,
                " ".join(str(value) for value in product["specs"].values()),
            ])
            if not _token_overlap(searchable_text, keyword_tokens):
                continue

        matches.append(product)

    matches.sort(key=lambda product: product["price_egp"])

    limited = matches[:_clamp_limit(limit)]

    return {
        "count": len(matches),
        "results": [_format_product(product, categories) for product in limited],
    }


def get_product_details(
    product_id: str | None = None,
    name: str | None = None,
) -> dict:
    """Look up exactly one product by id (exact) or name (exact match
    first, then best token-overlap match). Returns {"found": False} - not
    a guess - when nothing matches, so the caller never has to infer
    non-existence from an empty list."""

    categories = _category_lookup()
    products = load_products()

    if product_id:
        normalized_id = product_id.strip().upper()
        for product in products:
            if product["id"].upper() == normalized_id:
                return {"found": True, "product": _format_product(product, categories)}
        return {"found": False}

    if name:
        normalized_name = normalize_text(name)

        for product in products:
            if normalize_text(product["name"]) == normalized_name:
                return {"found": True, "product": _format_product(product, categories)}

        name_tokens = set(tokenize(name))
        best_product = None
        best_overlap = 0

        for product in products:
            overlap = len(set(tokenize(product["name"])) & name_tokens)
            if overlap > best_overlap:
                best_product, best_overlap = product, overlap

        if best_product is not None:
            return {"found": True, "product": _format_product(best_product, categories)}

        return {"found": False}

    return {"found": False}


# ==========================================
# 3. Branches
# ==========================================

def search_branches(
    city: str | None = None,
    name: str | None = None,
) -> dict:
    """Filter knowledge_base/branches/branches.json by city and/or branch
    name. Both filters match against city_ar AND name_ar together: a
    branch's "city" in this data is its governorate (e.g. "الغربية" for
    Tanta), while the actual city/neighborhood a customer would name (e.g.
    "طنطا") only appears inside name_ar ("فرع طنطا") - the same quirk
    app.ai.entities' branch aliases already account for. Matched via the
    shared Arabic-normalization + tokenizer, so spelling variants like
    "أسوان"/"اسوان" both match. No filters returns every branch."""

    city_tokens = set(tokenize(city)) if city else set()
    name_tokens = set(tokenize(name)) if name else set()

    matches = []

    for branch in load_branches():

        searchable_text = f"{branch['city_ar']} {branch['name_ar']}"

        if city_tokens and not _token_overlap(searchable_text, city_tokens):
            continue

        if name_tokens and not _token_overlap(searchable_text, name_tokens):
            continue

        matches.append({
            "id": branch["id"],
            "name": branch["name_ar"],
            "city": branch["city_ar"],
            "address": branch["address_ar"],
            "phone": branch["phone"],
            "hours_weekdays": branch["hours_weekdays"],
            "hours_friday": branch["hours_friday"],
            "has_repair_center": branch["has_repair_center"],
            "services": branch["services_ar"],
        })

    return {"count": len(matches), "results": matches}


# ==========================================
# 4. Services
# ==========================================

def search_services(
    category: str | None = None,
    keywords: str | None = None,
) -> dict:
    """Filter knowledge_base/services/services.json by category label
    and/or free-text keywords."""

    category_tokens = set(tokenize(category)) if category else set()
    keyword_tokens = set(tokenize(keywords)) if keywords else set()

    matches = []

    for service in load_services():

        if category_tokens and not _token_overlap(service["category_ar"], category_tokens):
            continue

        if keyword_tokens:
            searchable_text = f"{service['name_ar']} {service['description_ar']}"
            if not _token_overlap(searchable_text, keyword_tokens):
                continue

        matches.append({
            "id": service["id"],
            "name": service["name_ar"],
            "category": service["category_ar"],
            "description": service["description_ar"],
            "available_at": service["available_at"],
            "price_note": service["price_note_ar"],
        })

    return {"count": len(matches), "results": matches}


# ==========================================
# 5. Offers
# ==========================================

def search_offers(
    category: str | None = None,
    status: str | None = None,
    limit: int | None = None,
) -> dict:
    """Filter knowledge_base/offers/offers.json by the product category it
    applies to and/or its status ("ongoing"/"seasonal"). An offer with
    applies_to_categories == "all" always matches any category filter,
    since that's what "all" means in the source data. Capped at `limit`
    (default 5, same as the other tools) - offers.json currently holds 25
    entries, and returning all of them unfiltered would be a needlessly
    large payload for a chat reply; `count` still reports the true total."""

    categories = _category_lookup()
    category_ids = _resolve_category_ids(category, categories)

    matches = []

    for offer in load_offers():

        if status and offer["status"] != status:
            continue

        if category_ids is not None:
            applies_to = offer["applies_to_categories"]
            if applies_to != "all" and not (category_ids & set(applies_to)):
                continue

        matches.append({
            "id": offer["id"],
            "title": offer["title_ar"],
            "description": offer["description_ar"],
            "discount_type": offer["discount_type"],
            "discount_value": offer["discount_value"],
            "applies_to_categories": offer["applies_to_categories"],
            "conditions": offer["conditions_ar"],
            "status": offer["status"],
            "stackable": offer["stackable"],
        })

    limited = matches[:_clamp_limit(limit)]

    return {"count": len(matches), "results": limited}


# ==========================================
# Groq tool specs + dispatch table
# ==========================================

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "ابحث في كتالوج منتجات NovaTech الفعلي بمعايير محددة. "
                "استخدمها دائمًا عند طلب توصية منتج، أو تصفية حسب فئة/سعر/ميزانية، "
                "بدل الاعتماد على وصف عام."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "اسم الفئة أو الـid، مثل 'لابتوبات ألعاب' أو 'GLP'."
                    },
                    "max_price": {"type": "number", "description": "أعلى سعر بالجنيه المصري."},
                    "min_price": {"type": "number", "description": "أقل سعر بالجنيه المصري."},
                    "use_case": {
                        "type": "string",
                        "enum": list(_USE_CASE_CATEGORY_IDS.keys()),
                        "description": "الغرض من الاستخدام إن ذكره العميل."
                    },
                    "availability": {
                        "type": "string",
                        "enum": list(_AVAILABILITY_STATUS_AR.keys()),
                    },
                    "keywords": {"type": "string", "description": "كلمات بحث حرة إضافية."},
                    "limit": {"type": "integer", "description": "أقصى عدد نتائج (افتراضي 5)."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": (
                "اجلب تفاصيل منتج واحد محدد بدقة عبر الـID أو الاسم. "
                "استخدمها دائمًا عند سؤال العميل عن سعر أو مواصفات منتج بعينه بالاسم."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "name": {"type": "string", "description": "اسم المنتج كما ذكره العميل."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_branches",
            "description": (
                "ابحث عن فرع بالاسم أو المدينة، وأرجع بياناته الدقيقة "
                "(العنوان، الهاتف، مواعيد العمل، توفر مركز صيانة). "
                "استخدمها دائمًا عند سؤال العميل عن فرع أو مدينة محددة."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "name": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_services",
            "description": "ابحث عن الخدمات المتاحة (صيانة، تجميع، دعم فني، ...).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "مثل 'صيانة' أو 'دعم فني'."},
                    "keywords": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_offers",
            "description": "ابحث عن العروض والخصومات الحالية، اختياريًا مفلترة بفئة منتج.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "status": {"type": "string", "enum": ["ongoing", "seasonal"]},
                    "limit": {"type": "integer", "description": "أقصى عدد نتائج (افتراضي 5)."},
                },
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "search_branches": search_branches,
    "search_services": search_services,
    "search_offers": search_offers,
}
