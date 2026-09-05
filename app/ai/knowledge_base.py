import json
from pathlib import Path

from app.config import KNOWLEDGE_BASE_DIR


SPEC_LABELS_AR = {
    "processor": "المعالج",
    "ram": "الرام",
    "storage": "التخزين",
    "screen_size": "مقاس الشاشة",
    "gpu": "كارت الشاشة",
    "refresh_rate_hz": "معدل التحديث",
    "size_inch": "المقاس (بوصة)",
    "resolution": "الدقة",
    "panel_type": "نوع الشاشة",
    "type": "النوع",
    "connectivity": "الاتصال",
    "backlight": "الإضاءة الخلفية",
    "dpi": "دقة الحساسية (DPI)",
    "buttons": "عدد الأزرار",
    "capacity": "السعة",
    "interface": "الواجهة",
    "speed": "السرعة",
    "ports": "عدد المنافذ",
    "color_support": "الطباعة",
    "battery_life": "عمر البطارية",
    "fps": "معدل الإطارات",
    "microphone": "الميكروفون",
    "license_type": "نوع الترخيص",
    "duration": "مدة الاشتراك",
    "devices_covered": "عدد الأجهزة المدعومة",
    "battery_capacity_mah": "سعة البطارية (mAh)",
    "vram": "ذاكرة الكارت (VRAM)",
    "wattage": "القدرة (واط)",
    "certification": "شهادة الكفاءة",
    "socket": "نوع المقبس (Socket)",
    "chipset": "الشيبست",
    "cooling_type": "نوع التبريد",
    "form_factor": "الحجم القياسي",
    "compatibility": "التوافق",
}

_AVAILABLE_AT_LABELS_AR = {
    "all_branches": "جميع الفروع",
    "repair_center_branches": "الفروع التي تحتوي على مركز صيانة",
}

_DISCOUNT_TYPE_LABELS_AR = {
    "percentage": "نسبة خصم",
    "fixed_amount": "خصم بمبلغ ثابت",
    "bundle": "عرض باقة",
}

_OFFER_STATUS_LABELS_AR = {
    "ongoing": "دائم",
    "seasonal": "موسمي",
}


def _load_json(path: Path):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _load_markdown_chunks(path: Path) -> list[str]:

    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    return [
        chunk.strip()
        for chunk in text.split("\n\n")
        if chunk.strip()
    ]


# ==========================================
# Structured-entity renderers (JSON -> text chunk)
# ==========================================

def _render_company_info(info: dict) -> list[str]:

    return [
        (
            f"عن الشركة ({info['brand_name']}):\n"
            f"{info['description_ar']}\n"
            f"تأسست عام {info['founded_year']}.\n"
            f"المقر الرئيسي: {info['headquarters_address_ar']}.\n"
            f"نطاق الخدمة: {info['service_area_ar']}."
        ),
        (
            f"بيانات التواصل مع {info['brand_name']}:\n"
            f"الهاتف: {info['phone']}.\n"
            f"البريد الإلكتروني: {info['email']}.\n"
            f"الموقع الإلكتروني: {info['website']}.\n"
            f"صفحة فيسبوك: {info['facebook_page']}."
        ),
        (
            f"{info['brand_name']} بالأرقام:\n"
            f"عدد الفروع: {info['branch_count']}.\n"
            f"عدد الموظفين التقريبي: {info['employee_count_approx']}.\n"
            f"لغات الدعم: {', '.join(info['languages_supported'])}.\n"
            f"العملة: {info['currency']}."
        ),
        info["disclaimer_ar"],
    ]


def _render_categories_overview(categories: list[dict]) -> str:

    lines = ["فئات المنتجات المتوفرة لدى الشركة:"]

    for category in categories:
        lines.append(
            f"- {category['name_ar']} ({category['name_en']}): "
            f"{category['product_count']} منتج."
        )

    return "\n".join(lines)


def _render_product(product: dict, category_name_ar: str) -> str:

    lines = [f"{product['name']} ({category_name_ar}):"]
    lines.append(f"السعر: {product['price_egp']} جنيه.")

    for key, value in product["specs"].items():
        label = SPEC_LABELS_AR.get(key, key)
        lines.append(f"{label}: {value}.")

    lines.append(f"الحالة: {product['status_ar']}.")

    if product["warranty_months"]:
        lines.append(f"الضمان: {product['warranty_months']} شهرًا. {product['warranty_note_ar']}")
    else:
        lines.append(f"الضمان: {product['warranty_note_ar']}")

    return "\n".join(lines)


def render_branch(branch: dict) -> str:

    return (
        f"{branch['name_ar']} ({branch['city_ar']}):\n"
        f"العنوان: {branch['address_ar']}.\n"
        f"الهاتف: {branch['phone']}.\n"
        f"مواعيد العمل: {branch['hours_weekdays']}. الجمعة: {branch['hours_friday']}.\n"
        f"يحتوي على مركز صيانة: {'نعم' if branch['has_repair_center'] else 'لا'}.\n"
        f"الخدمات المتاحة: {', '.join(branch['services_ar'])}."
    )


def _render_service(service: dict) -> str:

    available_at = _AVAILABLE_AT_LABELS_AR.get(
        service["available_at"], service["available_at"]
    )

    return (
        f"خدمة: {service['name_ar']} ({service['category_ar']}).\n"
        f"{service['description_ar']}\n"
        f"متاحة في: {available_at}.\n"
        f"التكلفة: {service['price_note_ar']}."
    )


def _render_offer(offer: dict) -> str:

    discount_type_ar = _DISCOUNT_TYPE_LABELS_AR.get(
        offer["discount_type"], offer["discount_type"]
    )
    status_ar = _OFFER_STATUS_LABELS_AR.get(offer["status"], offer["status"])

    applies_to = offer["applies_to_categories"]
    applies_to_ar = "جميع الفئات" if applies_to == "all" else ", ".join(applies_to)

    lines = [f"عرض: {offer['title_ar']}.", offer["description_ar"]]
    lines.append(f"نوع الخصم: {discount_type_ar}.")

    if offer["discount_value"] is not None:
        if offer["discount_type"] == "percentage":
            lines.append(f"قيمة الخصم: {offer['discount_value']}%.")
        else:
            lines.append(f"قيمة الخصم: {offer['discount_value']} جنيه.")

    lines.append(f"الفئات المشمولة: {applies_to_ar}.")
    lines.append(f"الشروط: {offer['conditions_ar']}")
    lines.append(f"حالة العرض: {status_ar}.")
    lines.append(
        "يمكن الجمع مع عروض أخرى: "
        + ("نعم." if offer["stackable"] else "لا، لا يمكن الجمع بين أكثر من عرض على نفس الطلب.")
    )

    return "\n".join(lines)


# ==========================================
# Knowledge base loading
# ==========================================

_POLICY_FILES = [
    "return_policy.md",
    "exchange_policy.md",
    "shipping_policy.md",
    "warranty_policy.md",
    "payment_methods.md",
    "cancellation_policy.md",
    "discounts_and_offers.md",
    "business_hours.md",
    "customer_support.md",
]


def load_branches() -> list[dict]:

    return _load_json(KNOWLEDGE_BASE_DIR / "branches" / "branches.json")


def load_categories() -> list[dict]:

    return _load_json(KNOWLEDGE_BASE_DIR / "catalog" / "categories.json")


def load_products() -> list[dict]:

    return _load_json(KNOWLEDGE_BASE_DIR / "catalog" / "products.json")


def load_services() -> list[dict]:

    return _load_json(KNOWLEDGE_BASE_DIR / "services" / "services.json")


def load_offers() -> list[dict]:

    return _load_json(KNOWLEDGE_BASE_DIR / "offers" / "offers.json")


def load_company_info() -> dict:

    return _load_json(KNOWLEDGE_BASE_DIR / "company" / "company_info.json")


def load_all_chunks() -> list[str]:

    company_info = load_company_info()
    categories = load_categories()
    products = load_products()
    branches = load_branches()
    services = load_services()
    offers = load_offers()

    category_names_ar = {
        category["id"]: category["name_ar"]
        for category in categories
    }

    chunks: list[str] = []

    chunks += _render_company_info(company_info)
    chunks.append(_render_categories_overview(categories))

    chunks += [
        _render_product(product, category_names_ar.get(product["category_id"], ""))
        for product in products
    ]

    chunks += [render_branch(branch) for branch in branches]
    chunks += [_render_service(service) for service in services]
    chunks += [_render_offer(offer) for offer in offers]

    for policy_file in _POLICY_FILES:
        chunks += _load_markdown_chunks(KNOWLEDGE_BASE_DIR / "policies" / policy_file)

    chunks += _load_markdown_chunks(KNOWLEDGE_BASE_DIR / "faq" / "faq.md")

    print("Number of chunks:", len(chunks))

    return chunks
