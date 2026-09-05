"""
Generates the fictional NovaTech Knowledge Base used to test the RAG system
at a realistic medium-business scale.

This is a dev-time tool only - the running FastAPI app never imports or
executes this script. It makes no network/API calls; all data is deterministic
Python data written to JSON/Markdown files under knowledge_base/.

ALL DATA IS FICTIONAL. NovaTech is not a real company. No real personal
information is used anywhere in this dataset.

Run manually to (re)generate the dataset:
    python scripts/generate_knowledge_base.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "knowledge_base"


# ==========================================
# Company information
# ==========================================

COMPANY_INFO = {
    "legal_name_ar": "نوفاتك لتجارة أجهزة الكمبيوتر ش.م.م (بيانات وهمية تجريبية)",
    "brand_name": "NovaTech",
    "founded_year": 2018,
    "industry_ar": "بيع أجهزة الكمبيوتر واللابتوب والملحقات وخدمات الصيانة والدعم الفني",
    "description_ar": (
        "NovaTech هي شركة مصرية متخصصة في بيع أجهزة اللابتوب والكمبيوتر "
        "وملحقاتهما، وتقديم خدمات الصيانة والدعم الفني للأفراد والشركات "
        "والمؤسسات التعليمية، من خلال شبكة فروع تغطي عدة محافظات."
    ),
    "headquarters_address_ar": "مدينة نصر، شارع عباس العقاد، القاهرة",
    "phone": "01000000000",
    "email": "support@novatech.example",
    "website": "www.novatech.example",
    "facebook_page": "facebook.com/novatech.example",
    "service_area_ar": "جميع محافظات جمهورية مصر العربية عبر 13 فرعًا ونظام شحن وطني",
    "branch_count": 13,
    "employee_count_approx": 260,
    "languages_supported": ["العربية", "الإنجليزية"],
    "currency": "EGP",
    "disclaimer_ar": (
        "بيانات وهمية بالكامل تم إنشاؤها لأغراض الاختبار والتطوير فقط، "
        "ولا تمثل شركة حقيقية أو معلومات شخصية حقيقية."
    ),
}


# ==========================================
# Product categories
# ==========================================

CATEGORIES = [
    {"id": "LAP", "name_ar": "لابتوبات عامة وأعمال", "name_en": "Laptops"},
    {"id": "GLP", "name_ar": "لابتوبات ألعاب", "name_en": "Gaming Laptops"},
    {"id": "DSK", "name_ar": "أجهزة كمبيوتر مكتبية", "name_en": "Desktop PCs"},
    {"id": "MPC", "name_ar": "أجهزة مصغرة", "name_en": "Mini PCs"},
    {"id": "MON", "name_ar": "شاشات", "name_en": "Monitors"},
    {"id": "KEY", "name_ar": "لوحات مفاتيح", "name_en": "Keyboards"},
    {"id": "MSE", "name_ar": "ماوس", "name_en": "Mice"},
    {"id": "STG", "name_ar": "وسائط تخزين", "name_en": "Storage"},
    {"id": "NET", "name_ar": "أجهزة شبكات", "name_en": "Networking"},
    {"id": "PRN", "name_ar": "طابعات وماسحات ضوئية", "name_en": "Printers & Scanners"},
    {"id": "AUD", "name_ar": "سماعات ومكبرات صوت", "name_en": "Audio"},
    {"id": "CAM", "name_ar": "كاميرات ويب", "name_en": "Webcams"},
    {"id": "SFT", "name_ar": "برامج وتراخيص", "name_en": "Software & Licenses"},
    {"id": "TAB", "name_ar": "أجهزة لوحية", "name_en": "Tablets"},
    {"id": "CMP", "name_ar": "قطع غيار ومكونات", "name_en": "Components"},
    {"id": "ACC", "name_ar": "كابلات وإكسسوارات", "name_en": "Cables & Accessories"},
]

WARRANTY_MONTHS_BY_CATEGORY = {
    "LAP": 12, "GLP": 12, "DSK": 12, "MPC": 12, "MON": 12,
    "KEY": 12, "MSE": 12, "STG": 24, "NET": 12, "PRN": 12,
    "AUD": 12, "CAM": 12, "TAB": 12, "CMP": 12, "ACC": 6, "SFT": None,
}

WARRANTY_NOTE_HARDWARE_AR = (
    "ضمان الشركة المصنعة ضد عيوب التصنيع، ولا يشمل الكسر أو التلف "
    "بالسوائل أو سوء الاستخدام."
)
WARRANTY_NOTE_SOFTWARE_AR = (
    "لا يخضع لضمان الأجهزة، ويعمل وفق شروط ترخيص البرنامج المحددة عند الشراء."
)

# Products that must keep their original values from the first-phase dataset
# (company.txt), preserved here so the catalog stays backward-consistent.
LEGACY_STATUS_OVERRIDES_AR = {
    "Ultra Mini PC": "غير متوفر حاليًا",
}


def determine_status_ar(name: str, global_index: int) -> str:

    if name in LEGACY_STATUS_OVERRIDES_AR:
        return LEGACY_STATUS_OVERRIDES_AR[name]

    if global_index % 11 == 0:
        return "غير متوفر حاليًا"

    if global_index % 17 == 0:
        return "كمية محدودة"

    return "متوفر"


def build_products_raw() -> list[tuple[str, str, int, dict]]:
    """(name, category_id, price_egp, specs) for every product."""

    raw: list[tuple[str, str, int, dict]] = []

    raw += [
        ("Laptop Value 15", "LAP", 14500, {"processor": "Intel Core i3", "ram": "8GB", "storage": "256GB SSD", "screen_size": "15.6 بوصة"}),
        ("Student Book 15", "LAP", 18000, {"processor": "Intel Core i5", "ram": "8GB", "storage": "256GB SSD", "screen_size": "15.6 بوصة"}),
        ("Laptop Air 13", "LAP", 21000, {"processor": "Intel Core i5", "ram": "8GB", "storage": "512GB SSD", "screen_size": "13.3 بوصة"}),
        ("Laptop Air 14", "LAP", 24000, {"processor": "Intel Core i5", "ram": "16GB", "storage": "512GB SSD", "screen_size": "14 بوصة"}),
        ("Laptop Slim 14", "LAP", 26500, {"processor": "Intel Core i5", "ram": "16GB", "storage": "512GB SSD", "screen_size": "14 بوصة"}),
        ("Laptop Business 14", "LAP", 29000, {"processor": "Intel Core i7", "ram": "16GB", "storage": "512GB SSD", "screen_size": "14 بوصة"}),
        ("Laptop 2in1 14 Touch", "LAP", 31000, {"processor": "Intel Core i5", "ram": "16GB", "storage": "512GB SSD", "screen_size": "14 بوصة تعمل باللمس"}),
        ("Laptop Business 15 Pro", "LAP", 33000, {"processor": "Intel Core i7", "ram": "16GB", "storage": "1TB SSD", "screen_size": "15.6 بوصة"}),
        ("Laptop Pro 15", "LAP", 35000, {"processor": "Intel Core i7", "ram": "16GB", "storage": "512GB SSD", "screen_size": "15.6 بوصة"}),
        ("Laptop Creator 16", "LAP", 42000, {"processor": "Intel Core i9", "ram": "32GB", "storage": "1TB SSD", "screen_size": "16 بوصة"}),
    ]

    raw += [
        ("Gaming Nova 15", "GLP", 41000, {"processor": "AMD Ryzen 5", "ram": "16GB", "storage": "512GB SSD", "gpu": "RTX 4050", "refresh_rate_hz": "144Hz", "screen_size": "15.6 بوصة"}),
        ("Gaming X2", "GLP", 39000, {"processor": "AMD Ryzen 5", "ram": "16GB", "storage": "512GB SSD", "gpu": "RTX 4050", "refresh_rate_hz": "144Hz", "screen_size": "15.6 بوصة"}),
        ("Gaming Stealth 14", "GLP", 47000, {"processor": "Intel Core i7", "ram": "16GB", "storage": "1TB SSD", "gpu": "RTX 4060", "refresh_rate_hz": "165Hz", "screen_size": "14 بوصة"}),
        ("Gaming X1", "GLP", 45000, {"processor": "AMD Ryzen 7", "ram": "32GB", "storage": "1TB SSD", "gpu": "RTX 4060", "refresh_rate_hz": "165Hz", "screen_size": "15.6 بوصة"}),
        ("Gaming Vortex 15", "GLP", 52000, {"processor": "AMD Ryzen 7", "ram": "32GB", "storage": "1TB SSD", "gpu": "RTX 4070", "refresh_rate_hz": "165Hz", "screen_size": "15.6 بوصة"}),
        ("Gaming X3 Pro", "GLP", 58000, {"processor": "Intel Core i7", "ram": "32GB", "storage": "1TB SSD", "gpu": "RTX 4070", "refresh_rate_hz": "165Hz", "screen_size": "16 بوصة"}),
        ("Gaming Vortex 17", "GLP", 64000, {"processor": "Intel Core i9", "ram": "32GB", "storage": "2TB SSD", "gpu": "RTX 4080", "refresh_rate_hz": "240Hz", "screen_size": "17.3 بوصة"}),
        ("Gaming Titan 16", "GLP", 89000, {"processor": "Intel Core i9", "ram": "64GB", "storage": "2TB SSD", "gpu": "RTX 4090", "refresh_rate_hz": "240Hz", "screen_size": "16 بوصة"}),
    ]

    raw += [
        ("Desktop Home 1", "DSK", 13000, {"processor": "Intel Core i3", "ram": "8GB", "storage": "256GB SSD", "gpu": "مدمج"}),
        ("Desktop Office 1", "DSK", 15500, {"processor": "Intel Core i5", "ram": "8GB", "storage": "256GB SSD", "gpu": "مدمج"}),
        ("Desktop Home 2", "DSK", 16500, {"processor": "Intel Core i5", "ram": "8GB", "storage": "512GB SSD", "gpu": "مدمج"}),
        ("Desktop Office 2", "DSK", 19000, {"processor": "Intel Core i5", "ram": "16GB", "storage": "512GB SSD", "gpu": "مدمج"}),
        ("Desktop Creator 1", "DSK", 34000, {"processor": "Intel Core i7", "ram": "32GB", "storage": "1TB SSD", "gpu": "RTX 4060"}),
        ("Desktop Gaming Tower 1", "DSK", 42000, {"processor": "AMD Ryzen 7", "ram": "16GB", "storage": "1TB SSD", "gpu": "RTX 4070"}),
        ("Desktop Creator 2", "DSK", 46000, {"processor": "Intel Core i9", "ram": "32GB", "storage": "1TB SSD", "gpu": "RTX 4070"}),
        ("Desktop Gaming Tower 2", "DSK", 68000, {"processor": "AMD Ryzen 9", "ram": "32GB", "storage": "2TB SSD", "gpu": "RTX 4080"}),
    ]

    raw += [
        ("Mini PC Lite", "MPC", 8500, {"processor": "Intel Core i3", "ram": "8GB", "storage": "256GB SSD"}),
        ("Mini PC Home", "MPC", 10500, {"processor": "Intel Core i5", "ram": "8GB", "storage": "256GB SSD"}),
        ("Ultra Mini PC", "MPC", 12000, {"ram": "16GB", "storage": "512GB SSD"}),
        ("Mini PC Office", "MPC", 13500, {"processor": "Intel Core i5", "ram": "16GB", "storage": "512GB SSD"}),
        ("Mini PC Pro", "MPC", 17500, {"processor": "Intel Core i7", "ram": "16GB", "storage": "512GB SSD"}),
        ("Mini PC Studio", "MPC", 22000, {"processor": "Intel Core i7", "ram": "32GB", "storage": "1TB SSD"}),
    ]

    raw += [
        ("NovaView 21", "MON", 3200, {"size_inch": "21.5", "resolution": "1920x1080", "panel_type": "IPS", "refresh_rate_hz": "75Hz"}),
        ("NovaView 24", "MON", 4200, {"size_inch": "24", "resolution": "1920x1080", "panel_type": "IPS", "refresh_rate_hz": "100Hz"}),
        ("NovaView Portable 15", "MON", 6200, {"size_inch": "15.6", "resolution": "1920x1080", "panel_type": "IPS", "refresh_rate_hz": "60Hz"}),
        ("NovaView 27", "MON", 5800, {"size_inch": "27", "resolution": "1920x1080", "panel_type": "IPS", "refresh_rate_hz": "100Hz"}),
        ("NovaView Curved 27", "MON", 8800, {"size_inch": "27", "resolution": "2560x1440", "panel_type": "VA منحني", "refresh_rate_hz": "144Hz"}),
        ("NovaView Gaming 24", "MON", 7200, {"size_inch": "24", "resolution": "1920x1080", "panel_type": "IPS", "refresh_rate_hz": "165Hz"}),
        ("NovaView Gaming 27", "MON", 9500, {"size_inch": "27", "resolution": "2560x1440", "panel_type": "IPS", "refresh_rate_hz": "165Hz"}),
        ("NovaView 4K 27", "MON", 12500, {"size_inch": "27", "resolution": "3840x2160", "panel_type": "IPS", "refresh_rate_hz": "60Hz"}),
        ("NovaView 4K 32", "MON", 15800, {"size_inch": "32", "resolution": "3840x2160", "panel_type": "IPS", "refresh_rate_hz": "60Hz"}),
        ("NovaView Curved 34 Ultrawide", "MON", 16500, {"size_inch": "34", "resolution": "3440x1440", "panel_type": "VA منحني", "refresh_rate_hz": "144Hz"}),
    ]

    raw += [
        ("NovaKey Office Standard", "KEY", 350, {"type": "غشائي", "connectivity": "سلكي", "backlight": "بدون إضاءة"}),
        ("NovaKey Compact 60%", "KEY", 650, {"type": "ميكانيكي", "connectivity": "سلكي", "backlight": "RGB"}),
        ("NovaKey Wireless Slim", "KEY", 750, {"type": "غشائي", "connectivity": "لاسلكي", "backlight": "بدون إضاءة"}),
        ("NovaKey Wireless Multi-Device", "KEY", 950, {"type": "غشائي", "connectivity": "بلوتوث/لاسلكي", "backlight": "إضاءة بيضاء"}),
        ("NovaKey Ergonomic Split", "KEY", 1450, {"type": "غشائي", "connectivity": "سلكي", "backlight": "بدون إضاءة"}),
        ("NovaKey Mechanical Silent", "KEY", 1200, {"type": "ميكانيكي هادئ", "connectivity": "سلكي", "backlight": "RGB"}),
        ("NovaKey Mechanical RGB", "KEY", 1350, {"type": "ميكانيكي", "connectivity": "سلكي", "backlight": "RGB"}),
        ("NovaKey Gaming Pro", "KEY", 1650, {"type": "ميكانيكي", "connectivity": "سلكي", "backlight": "RGB لكل مفتاح"}),
    ]

    raw += [
        ("NovaClick Compact Travel", "MSE", 250, {"connectivity": "سلكي", "dpi": "1000", "buttons": "3"}),
        ("NovaClick Silent", "MSE", 350, {"connectivity": "سلكي", "dpi": "1200", "buttons": "3"}),
        ("NovaClick Wireless", "MSE", 450, {"connectivity": "لاسلكي", "dpi": "1600", "buttons": "4"}),
        ("NovaClick Bluetooth", "MSE", 550, {"connectivity": "بلوتوث", "dpi": "1600", "buttons": "4"}),
        ("NovaClick Ergonomic", "MSE", 600, {"connectivity": "سلكي", "dpi": "1600", "buttons": "5"}),
        ("NovaClick Vertical", "MSE", 750, {"connectivity": "لاسلكي", "dpi": "1600", "buttons": "5"}),
        ("NovaClick Gaming RGB", "MSE", 950, {"connectivity": "سلكي", "dpi": "6400", "buttons": "6"}),
        ("NovaClick Gaming Pro", "MSE", 1450, {"connectivity": "سلكي", "dpi": "16000", "buttons": "8"}),
    ]

    raw += [
        ("NovaDrive USB Flash 32GB", "STG", 180, {"type": "فلاش ميموري", "capacity": "32GB", "interface": "USB 3.0"}),
        ("NovaDrive USB Flash 64GB", "STG", 260, {"type": "فلاش ميموري", "capacity": "64GB", "interface": "USB 3.0"}),
        ("NovaDrive USB Flash 128GB", "STG", 380, {"type": "فلاش ميموري", "capacity": "128GB", "interface": "USB 3.0"}),
        ("NovaDrive SSD 256GB", "STG", 1400, {"type": "SATA SSD", "capacity": "256GB", "interface": "SATA III"}),
        ("NovaDrive HDD 1TB External", "STG", 1600, {"type": "هارد خارجي", "capacity": "1TB", "interface": "USB 3.0"}),
        ("NovaDrive SSD 512GB", "STG", 2100, {"type": "SATA SSD", "capacity": "512GB", "interface": "SATA III"}),
        ("NovaDrive NVMe 512GB", "STG", 2600, {"type": "NVMe SSD", "capacity": "512GB", "interface": "PCIe 4.0"}),
        ("NovaDrive HDD 2TB External", "STG", 2400, {"type": "هارد خارجي", "capacity": "2TB", "interface": "USB 3.0"}),
        ("NovaDrive SSD 1TB", "STG", 3400, {"type": "SATA SSD", "capacity": "1TB", "interface": "SATA III"}),
        ("NovaDrive HDD 4TB External", "STG", 3600, {"type": "هارد خارجي", "capacity": "4TB", "interface": "USB 3.0"}),
        ("NovaDrive NVMe 1TB", "STG", 4200, {"type": "NVMe SSD", "capacity": "1TB", "interface": "PCIe 4.0"}),
        ("NovaDrive NVMe 2TB", "STG", 7800, {"type": "NVMe SSD", "capacity": "2TB", "interface": "PCIe 4.0"}),
    ]

    raw += [
        ("NovaNet USB WiFi Adapter", "NET", 480, {"type": "محول واي فاي", "speed": "AC600", "ports": "-"}),
        ("NovaNet Range Extender", "NET", 850, {"type": "موسع شبكة", "speed": "AC1200", "ports": "-"}),
        ("NovaNet Switch 8-Port", "NET", 950, {"type": "سويتش شبكة", "speed": "1 جيجابت", "ports": "8"}),
        ("NovaNet Router AC1200", "NET", 1200, {"type": "راوتر", "speed": "AC1200", "ports": "4"}),
        ("NovaNet Switch 16-Port", "NET", 1850, {"type": "سويتش شبكة", "speed": "1 جيجابت", "ports": "16"}),
        ("NovaNet Router AX3000", "NET", 2400, {"type": "راوتر واي فاي 6", "speed": "AX3000", "ports": "4"}),
        ("NovaNet Mesh System (Pack of 2)", "NET", 3800, {"type": "نظام مش شبكة", "speed": "AX3000", "ports": "-"}),
        ("NovaNet Mesh System (Pack of 3)", "NET", 5400, {"type": "نظام مش شبكة", "speed": "AX3000", "ports": "-"}),
    ]

    raw += [
        ("NovaPrint Label Printer", "PRN", 1600, {"type": "طابعة لاصقات حرارية", "color_support": "أبيض وأسود", "connectivity": "USB"}),
        ("NovaPrint InkJet Basic", "PRN", 2200, {"type": "نافثة حبر", "color_support": "ألوان", "connectivity": "USB"}),
        ("NovaScan Portable", "PRN", 2100, {"type": "ماسح ضوئي محمول", "color_support": "ألوان", "connectivity": "USB"}),
        ("NovaScan Flatbed", "PRN", 2800, {"type": "ماسح ضوئي مسطح", "color_support": "ألوان", "connectivity": "USB"}),
        ("NovaPrint InkJet All-in-One", "PRN", 3400, {"type": "نافثة حبر (طباعة/مسح/تصوير)", "color_support": "ألوان", "connectivity": "USB وواي فاي"}),
        ("NovaPrint Photo Printer", "PRN", 3600, {"type": "طابعة صور", "color_support": "ألوان", "connectivity": "واي فاي"}),
        ("NovaPrint Laser Mono", "PRN", 4200, {"type": "ليزر", "color_support": "أبيض وأسود", "connectivity": "USB وواي فاي"}),
        ("NovaPrint Laser Color", "PRN", 7800, {"type": "ليزر", "color_support": "ألوان", "connectivity": "USB وواي فاي"}),
    ]

    raw += [
        ("NovaSound Headset Wired", "AUD", 550, {"type": "سماعة رأس", "connectivity": "سلكي", "battery_life": "-"}),
        ("NovaSound Earbuds", "AUD", 650, {"type": "سماعة أذن لاسلكية", "connectivity": "بلوتوث", "battery_life": "24 ساعة (مع العلبة)"}),
        ("NovaSound Speaker Desktop 2.0", "AUD", 750, {"type": "سماعة مكتبية", "connectivity": "سلكي", "battery_life": "-"}),
        ("NovaSound Speaker Portable", "AUD", 950, {"type": "سماعة محمولة", "connectivity": "بلوتوث", "battery_life": "12 ساعة"}),
        ("NovaSound Headset Wireless", "AUD", 1250, {"type": "سماعة رأس لاسلكية", "connectivity": "بلوتوث", "battery_life": "20 ساعة"}),
        ("NovaSound Earbuds Pro ANC", "AUD", 1450, {"type": "سماعة أذن لاسلكية بعزل ضوضاء", "connectivity": "بلوتوث", "battery_life": "30 ساعة (مع العلبة)"}),
        ("NovaSound Speaker Desktop 2.1", "AUD", 1350, {"type": "سماعة مكتبية مع سب ووفر", "connectivity": "سلكي", "battery_life": "-"}),
        ("NovaSound Headset Gaming RGB", "AUD", 1650, {"type": "سماعة رأس ألعاب", "connectivity": "سلكي (7.1 محيطي)", "battery_life": "-"}),
        ("NovaSound Soundbar", "AUD", 2600, {"type": "ساوند بار", "connectivity": "سلكي/بلوتوث", "battery_life": "-"}),
        ("NovaSound Studio Monitor (Pair)", "AUD", 4800, {"type": "سماعات استوديو", "connectivity": "سلكي", "battery_life": "-"}),
    ]

    raw += [
        ("NovaCam HD 720p", "CAM", 450, {"resolution": "720p", "fps": "30", "microphone": "مدمج"}),
        ("NovaCam FHD 1080p", "CAM", 850, {"resolution": "1080p", "fps": "30", "microphone": "مدمج"}),
        ("NovaCam Conference Wide-Angle", "CAM", 1600, {"resolution": "1080p", "fps": "30", "microphone": "مصفوفة ميكروفونات"}),
        ("NovaCam 4K Pro", "CAM", 2200, {"resolution": "4K", "fps": "30", "microphone": "مزدوج"}),
        ("NovaCam Streaming Kit", "CAM", 2800, {"resolution": "1080p", "fps": "60", "microphone": "مزدوج + إضاءة حلقية"}),
    ]

    raw += [
        ("NovaShield Antivirus 1-Year (1 Device)", "SFT", 350, {"license_type": "مكافح فيروسات", "duration": "سنة واحدة", "devices_covered": "جهاز واحد"}),
        ("NovaShield Antivirus 1-Year (3 Devices)", "SFT", 550, {"license_type": "مكافح فيروسات", "duration": "سنة واحدة", "devices_covered": "3 أجهزة"}),
        ("NovaBackup Cloud 100GB/Year", "SFT", 450, {"license_type": "نسخ احتياطي سحابي", "duration": "سنة واحدة", "devices_covered": "غير محدود"}),
        ("NovaVPN 1-Year", "SFT", 650, {"license_type": "شبكة افتراضية خاصة", "duration": "سنة واحدة", "devices_covered": "5 أجهزة"}),
        ("NovaShield Antivirus 2-Year (3 Devices)", "SFT", 950, {"license_type": "مكافح فيروسات", "duration": "سنتان", "devices_covered": "3 أجهزة"}),
        ("NovaBackup Cloud 500GB/Year", "SFT", 950, {"license_type": "نسخ احتياطي سحابي", "duration": "سنة واحدة", "devices_covered": "غير محدود"}),
        ("NovaOffice Home & Student", "SFT", 1800, {"license_type": "حزمة مكتبية", "duration": "مدى الحياة", "devices_covered": "جهاز واحد"}),
        ("Windows License (Home)", "SFT", 2200, {"license_type": "نظام تشغيل", "duration": "مدى الحياة", "devices_covered": "جهاز واحد"}),
        ("NovaOffice Business (Annual)", "SFT", 2400, {"license_type": "حزمة مكتبية للشركات", "duration": "سنة واحدة", "devices_covered": "جهاز واحد"}),
        ("Windows License (Pro)", "SFT", 3200, {"license_type": "نظام تشغيل", "duration": "مدى الحياة", "devices_covered": "جهاز واحد"}),
    ]

    raw += [
        ("NovaTab Kids 8", "TAB", 3800, {"screen_size": "8 بوصة", "ram": "3GB", "storage": "32GB", "battery_capacity_mah": "4000"}),
        ("NovaTab 8 Lite", "TAB", 5200, {"screen_size": "8 بوصة", "ram": "4GB", "storage": "64GB", "battery_capacity_mah": "5000"}),
        ("NovaTab 10", "TAB", 7500, {"screen_size": "10.1 بوصة", "ram": "4GB", "storage": "64GB", "battery_capacity_mah": "7000"}),
        ("NovaTab 10 Pro", "TAB", 11500, {"screen_size": "10.9 بوصة", "ram": "8GB", "storage": "128GB", "battery_capacity_mah": "8000"}),
        ("NovaTab Business 12", "TAB", 16500, {"screen_size": "12.4 بوصة", "ram": "8GB", "storage": "256GB", "battery_capacity_mah": "10000"}),
        ("NovaTab 11 Pro Max", "TAB", 21000, {"screen_size": "11 بوصة", "ram": "8GB", "storage": "256GB", "battery_capacity_mah": "9000"}),
    ]

    raw += [
        ("NovaMem RAM 8GB DDR4", "CMP", 850, {"type": "رام", "capacity": "8GB", "speed": "DDR4"}),
        ("NovaMem RAM 16GB DDR4", "CMP", 1500, {"type": "رام", "capacity": "16GB", "speed": "DDR4"}),
        ("NovaCase ATX Mid Tower", "CMP", 2200, {"type": "كيس كمبيوتر", "form_factor": "ATX Mid Tower"}),
        ("NovaMem RAM 16GB DDR5", "CMP", 2100, {"type": "رام", "capacity": "16GB", "speed": "DDR5"}),
        ("NovaPower PSU 550W 80+ Bronze", "CMP", 1600, {"type": "باور سبلاي", "wattage": "550W", "certification": "80+ Bronze"}),
        ("NovaCool Liquid Cooler 240mm", "CMP", 2800, {"type": "تبريد مائي", "cooling_type": "Liquid 240mm", "socket": "متوافق مع Intel وAMD"}),
        ("NovaPower PSU 750W 80+ Gold", "CMP", 2600, {"type": "باور سبلاي", "wattage": "750W", "certification": "80+ Gold"}),
        ("NovaMem RAM 32GB DDR5", "CMP", 3900, {"type": "رام", "capacity": "32GB", "speed": "DDR5"}),
        ("NovaPower PSU 850W 80+ Gold", "CMP", 3200, {"type": "باور سبلاي", "wattage": "850W", "certification": "80+ Gold"}),
        ("NovaBoard B760 (Intel)", "CMP", 5200, {"type": "مذربورد", "socket": "LGA1700", "chipset": "B760"}),
        ("NovaGraphics RX 7600", "CMP", 13500, {"type": "كارت شاشة", "vram": "8GB GDDR6", "chipset": "AMD RX 7600"}),
        ("NovaGraphics RTX 4060", "CMP", 16500, {"type": "كارت شاشة", "vram": "8GB GDDR6", "chipset": "NVIDIA RTX 4060"}),
        ("NovaBoard Z790 (Intel)", "CMP", 8500, {"type": "مذربورد", "socket": "LGA1700", "chipset": "Z790"}),
        ("NovaGraphics RTX 4070", "CMP", 26000, {"type": "كارت شاشة", "vram": "12GB GDDR6X", "chipset": "NVIDIA RTX 4070"}),
        ("NovaGraphics RTX 4080", "CMP", 42000, {"type": "كارت شاشة", "vram": "16GB GDDR6X", "chipset": "NVIDIA RTX 4080"}),
    ]

    raw += [
        ("NovaLink Screen Protector (Laptop)", "ACC", 150, {"type": "واقي شاشة", "compatibility": "عام"}),
        ("NovaLink USB-C Cable 1m", "ACC", 120, {"type": "كابل USB-C إلى USB-C", "compatibility": "عام"}),
        ("NovaLink Cleaning Kit", "ACC", 220, {"type": "طقم تنظيف", "compatibility": "شاشات وكيبورد"}),
        ("NovaLink HDMI Cable 2m", "ACC", 180, {"type": "كابل HDMI 2.1", "compatibility": "عام"}),
        ("NovaLink Cooling Pad", "ACC", 480, {"type": "قاعدة تبريد لابتوب", "compatibility": "حتى 17 بوصة"}),
        ("NovaLink Laptop Stand", "ACC", 550, {"type": "ستاند لابتوب ألومنيوم", "compatibility": "عام"}),
        ("NovaLink Laptop Bag 15-inch", "ACC", 650, {"type": "شنطة لابتوب", "compatibility": "حتى 15.6 بوصة"}),
        ("NovaLink USB-C Hub 6-in-1", "ACC", 950, {"type": "هَب USB-C متعدد المنافذ", "compatibility": "عام"}),
    ]

    return raw


def assemble_products() -> list[dict]:

    raw = build_products_raw()
    products = []
    category_counters: dict[str, int] = {}

    for global_index, (name, category_id, price_egp, specs) in enumerate(raw):

        category_counters[category_id] = category_counters.get(category_id, 0) + 1
        product_id = f"NVT-{category_id}-{category_counters[category_id]:03d}"

        is_software = category_id == "SFT"

        products.append(
            {
                "id": product_id,
                "name": name,
                "category_id": category_id,
                "price_egp": price_egp,
                "specs": specs,
                "status_ar": determine_status_ar(name, global_index),
                "warranty_months": WARRANTY_MONTHS_BY_CATEGORY[category_id],
                "warranty_note_ar": (
                    WARRANTY_NOTE_SOFTWARE_AR if is_software else WARRANTY_NOTE_HARDWARE_AR
                ),
            }
        )

    assert len(products) == len({p["id"] for p in products}), "duplicate product id"
    assert len(products) == len({p["name"] for p in products}), "duplicate product name"

    return products


# ==========================================
# Branches
# ==========================================

_STANDARD_HOURS = {"hours_weekdays": "10:00 ص - 8:00 م", "hours_friday": "مغلق"}

_BASE_SERVICES_AR = ["بيع أجهزة كمبيوتر ولابتوب", "دعم فني أولي", "استلام واستبدال المنتجات"]
_REPAIR_EXTRA_SERVICES_AR = ["صيانة أجهزة", "تركيب وتجميع أجهزة مخصصة"]


def _branch(branch_id, name_ar, city_ar, address_ar, phone, has_repair_center):

    services_ar = list(_BASE_SERVICES_AR)

    if has_repair_center:
        services_ar += _REPAIR_EXTRA_SERVICES_AR

    return {
        "id": branch_id,
        "name_ar": name_ar,
        "city_ar": city_ar,
        "address_ar": address_ar,
        "phone": phone,
        **_STANDARD_HOURS,
        "has_repair_center": has_repair_center,
        "services_ar": services_ar,
    }


BRANCHES = [
    _branch("BR-01", "فرع مدينة نصر", "القاهرة", "مدينة نصر، شارع عباس العقاد، القاهرة", "01000000001", True),
    _branch("BR-02", "فرع المعادي", "القاهرة", "المعادي، شارع 9، القاهرة", "01000000002", False),
    _branch("BR-03", "فرع المهندسين", "الجيزة", "المهندسين، شارع جامعة الدول العربية، الجيزة", "01000000003", True),
    _branch("BR-04", "فرع 6 أكتوبر", "الجيزة", "مدينة 6 أكتوبر، المحور المركزي، الجيزة", "01000000004", False),
    _branch("BR-05", "فرع سموحة", "الإسكندرية", "سموحة، شارع فوزي معاذ، الإسكندرية", "01000000005", True),
    _branch("BR-06", "فرع محطة الرمل", "الإسكندرية", "محطة الرمل، شارع صفية زغلول، الإسكندرية", "01000000006", False),
    _branch("BR-07", "فرع المنصورة", "الدقهلية", "المنصورة، شارع الجمهورية، الدقهلية", "01000000007", True),
    _branch("BR-08", "فرع طنطا", "الغربية", "طنطا، شارع سعيد، الغربية", "01000000008", False),
    _branch("BR-09", "فرع الزقازيق", "الشرقية", "الزقازيق، شارع الجيش، الشرقية", "01000000009", False),
    _branch("BR-10", "فرع أسيوط", "أسيوط", "أسيوط، شارع الثورة، أسيوط", "01000000010", True),
    _branch("BR-11", "فرع الأقصر", "الأقصر", "الأقصر، كورنيش النيل، الأقصر", "01000000011", False),
    _branch("BR-12", "فرع أسوان", "أسوان", "أسوان، شارع السد العالي، أسوان", "01000000012", False),
    _branch("BR-13", "فرع بورسعيد", "بورسعيد", "بورسعيد، شارع الجمهورية، بورسعيد", "01000000013", True),
]

assert len(BRANCHES) == len({b["id"] for b in BRANCHES}), "duplicate branch id"


# ==========================================
# Services
# ==========================================

SERVICES = [
    {"id": "SVC-01", "name_ar": "بيع أجهزة كمبيوتر ولابتوب", "category_ar": "مبيعات", "description_ar": "بيع كافة فئات أجهزة الكمبيوتر واللابتوب الجديدة.", "available_at": "all_branches", "price_note_ar": "حسب سعر المنتج"},
    {"id": "SVC-02", "name_ar": "تركيب وتجميع أجهزة كمبيوتر مخصصة", "category_ar": "تجميع", "description_ar": "تجميع جهاز كمبيوتر مكتبي بمواصفات يختارها العميل.", "available_at": "repair_center_branches", "price_note_ar": "حسب المكونات المختارة"},
    {"id": "SVC-03", "name_ar": "صيانة أجهزة اللابتوب", "category_ar": "صيانة", "description_ar": "فحص وإصلاح أعطال أجهزة اللابتوب.", "available_at": "repair_center_branches", "price_note_ar": "حسب تقييم الفني"},
    {"id": "SVC-04", "name_ar": "صيانة أجهزة الكمبيوتر المكتبي", "category_ar": "صيانة", "description_ar": "فحص وإصلاح أعطال أجهزة الكمبيوتر المكتبي.", "available_at": "repair_center_branches", "price_note_ar": "حسب تقييم الفني"},
    {"id": "SVC-05", "name_ar": "استبدال شاشات اللابتوب", "category_ar": "صيانة", "description_ar": "استبدال شاشة اللابتوب التالفة بشاشة أصلية متوافقة.", "available_at": "repair_center_branches", "price_note_ar": "حسب الموديل"},
    {"id": "SVC-06", "name_ar": "استبدال بطاريات اللابتوب", "category_ar": "صيانة", "description_ar": "استبدال بطارية اللابتوب المستهلكة ببطارية جديدة.", "available_at": "repair_center_branches", "price_note_ar": "حسب الموديل"},
    {"id": "SVC-07", "name_ar": "تنظيف داخلي للأجهزة", "category_ar": "صيانة", "description_ar": "تنظيف الأتربة الداخلية وتغيير المعجون الحراري.", "available_at": "repair_center_branches", "price_note_ar": "سعر ثابت"},
    {"id": "SVC-08", "name_ar": "تثبيت نظام التشغيل والتعريفات", "category_ar": "دعم فني", "description_ar": "تثبيت أو إعادة تثبيت Windows وتعريفات الجهاز.", "available_at": "all_branches", "price_note_ar": "سعر ثابت"},
    {"id": "SVC-09", "name_ar": "إزالة الفيروسات وبرامج التجسس", "category_ar": "دعم فني", "description_ar": "فحص الجهاز وإزالة البرامج الضارة.", "available_at": "all_branches", "price_note_ar": "سعر ثابت"},
    {"id": "SVC-10", "name_ar": "ترقية الرام", "category_ar": "صيانة", "description_ar": "إضافة أو استبدال ذاكرة الرام لتحسين الأداء.", "available_at": "repair_center_branches", "price_note_ar": "حسب سعر القطعة"},
    {"id": "SVC-11", "name_ar": "ترقية التخزين إلى SSD", "category_ar": "صيانة", "description_ar": "استبدال الهارد التقليدي بقرص SSD أسرع.", "available_at": "repair_center_branches", "price_note_ar": "حسب سعر القطعة"},
    {"id": "SVC-12", "name_ar": "نقل البيانات بين الأجهزة", "category_ar": "دعم فني", "description_ar": "نقل الملفات والبيانات من جهاز قديم إلى جهاز جديد.", "available_at": "all_branches", "price_note_ar": "سعر ثابت"},
    {"id": "SVC-13", "name_ar": "استرجاع البيانات المفقودة", "category_ar": "صيانة متقدمة", "description_ar": "محاولة استعادة الملفات المحذوفة أو التالفة من وسائط التخزين.", "available_at": "repair_center_branches", "price_note_ar": "حسب حالة الجهاز"},
    {"id": "SVC-14", "name_ar": "نسخ احتياطي للبيانات", "category_ar": "دعم فني", "description_ar": "إعداد نسخة احتياطية دورية لبيانات العميل.", "available_at": "all_branches", "price_note_ar": "سعر ثابت"},
    {"id": "SVC-15", "name_ar": "تركيب شبكات منزلية", "category_ar": "شبكات", "description_ar": "تجهيز وتوزيع شبكة واي فاي داخل المنزل.", "available_at": "repair_center_branches", "price_note_ar": "حسب حجم المنزل"},
    {"id": "SVC-16", "name_ar": "تركيب شبكات للشركات", "category_ar": "شبكات", "description_ar": "تصميم وتركيب شبكة داخلية لمقرات الشركات.", "available_at": "repair_center_branches", "price_note_ar": "عرض سعر مخصص"},
    {"id": "SVC-17", "name_ar": "الدعم الفني عن بُعد", "category_ar": "دعم فني", "description_ar": "حل المشاكل البرمجية البسيطة عن بعد عبر الإنترنت.", "available_at": "all_branches", "price_note_ar": "استشارة أولية مجانية"},
    {"id": "SVC-18", "name_ar": "الدعم الفني داخل الفرع", "category_ar": "دعم فني", "description_ar": "استقبال استفسارات ومشاكل الأجهزة داخل الفرع.", "available_at": "all_branches", "price_note_ar": "استشارة أولية مجانية"},
    {"id": "SVC-19", "name_ar": "شراء الضمان الممتد", "category_ar": "خدمة ما بعد البيع", "description_ar": "تمديد فترة ضمان المنتج بعد انتهاء الضمان الأساسي.", "available_at": "all_branches", "price_note_ar": "حسب فئة المنتج"},
    {"id": "SVC-20", "name_ar": "تدريب استخدام البرامج المكتبية", "category_ar": "تدريب", "description_ar": "جلسات تدريبية لاستخدام برامج Office الأساسية.", "available_at": "repair_center_branches", "price_note_ar": "سعر ثابت للجلسة"},
    {"id": "SVC-21", "name_ar": "استشارات شراء أجهزة للشركات", "category_ar": "استشارات", "description_ar": "مساعدة الشركات في اختيار الأجهزة المناسبة لاحتياجاتها.", "available_at": "all_branches", "price_note_ar": "مجاني"},
    {"id": "SVC-22", "name_ar": "عروض أسعار مخصصة للشركات", "category_ar": "مبيعات شركات", "description_ar": "إعداد عرض سعر رسمي لطلبات الشركات الكبيرة.", "available_at": "all_branches", "price_note_ar": "مجاني"},
    {"id": "SVC-23", "name_ar": "تجهيز أجهزة الألعاب المخصصة", "category_ar": "تجميع", "description_ar": "تجميع جهاز ألعاب بمواصفات ومكونات يختارها العميل.", "available_at": "repair_center_branches", "price_note_ar": "حسب المكونات المختارة"},
    {"id": "SVC-24", "name_ar": "تركيب برامج الحماية والأمان", "category_ar": "دعم فني", "description_ar": "تثبيت وإعداد برامج مكافحة الفيروسات وأدوات الحماية.", "available_at": "all_branches", "price_note_ar": "سعر ثابت"},
    {"id": "SVC-25", "name_ar": "توريد أجهزة للمدارس والجامعات", "category_ar": "مبيعات مؤسسات", "description_ar": "توريد أجهزة بأعداد كبيرة للمؤسسات التعليمية.", "available_at": "all_branches", "price_note_ar": "عرض سعر مخصص"},
    {"id": "SVC-26", "name_ar": "عقود صيانة سنوية للشركات", "category_ar": "عقود خدمة", "description_ar": "عقد صيانة دوري لأجهزة الشركة على مدار العام.", "available_at": "all_branches", "price_note_ar": "عرض سعر مخصص"},
    {"id": "SVC-27", "name_ar": "خدمة التوصيل السريع", "category_ar": "لوجستيات", "description_ar": "توصيل الطلبات العاجلة خلال مدة أقصر من المعتاد.", "available_at": "all_branches", "price_note_ar": "حسب المنطقة"},
    {"id": "SVC-28", "name_ar": "المساعدة في إعداد خطط التقسيط", "category_ar": "دعم مالي", "description_ar": "توضيح خيارات التقسيط المتاحة مع شركاء التمويل.", "available_at": "all_branches", "price_note_ar": "مجاني"},
    {"id": "SVC-29", "name_ar": "تقييم واستبدال الأجهزة المستعملة (تريد إن)", "category_ar": "خدمة ما بعد البيع", "description_ar": "تقييم جهاز قديم يعمل ومنح رصيد شراء مقابله.", "available_at": "repair_center_branches", "price_note_ar": "حسب تقييم الجهاز"},
    {"id": "SVC-30", "name_ar": "إعداد أجهزة الشركات دفعة واحدة", "category_ar": "خدمة شركات", "description_ar": "تجهيز وإعداد عدد كبير من الأجهزة دفعة واحدة لشركة.", "available_at": "repair_center_branches", "price_note_ar": "عرض سعر مخصص"},
]

assert len(SERVICES) == len({s["id"] for s in SERVICES}), "duplicate service id"


# ==========================================
# Offers / discounts
# ==========================================

OFFERS = [
    {"id": "OFF-01", "title_ar": "خصم الطلاب", "description_ar": "خصم للطلاب على فئات مختارة من اللابتوبات.", "discount_type": "percentage", "discount_value": 10, "applies_to_categories": ["LAP", "GLP"], "conditions_ar": "بشرط تقديم إثبات طالب ساري.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-02", "title_ar": "خصم الطلبات الكبيرة", "description_ar": "خصم على الطلبات ذات القيمة الكبيرة من أي فئة.", "discount_type": "percentage", "discount_value": 5, "applies_to_categories": "all", "conditions_ar": "قيمة الطلب أكبر من 50000 جنيه.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-03", "title_ar": "باقة العودة للمدارس", "description_ar": "لابتوب مع شنطة وماوس بسعر مخفض.", "discount_type": "fixed_amount", "discount_value": 1500, "applies_to_categories": ["LAP", "ACC"], "conditions_ar": "شراء الباقة كاملة خلال فترة العرض (أغسطس - سبتمبر).", "stackable": False, "status": "seasonal"},
    {"id": "OFF-04", "title_ar": "خصم الجمعة البيضاء", "description_ar": "خصم موسمي على جميع الفئات خلال أسبوع الجمعة البيضاء.", "discount_type": "percentage", "discount_value": 15, "applies_to_categories": "all", "conditions_ar": "خلال أسبوع الجمعة البيضاء فقط.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-05", "title_ar": "خصم الدفع كاش", "description_ar": "خصم عند سداد كامل قيمة الطلب نقدًا داخل الفرع.", "discount_type": "percentage", "discount_value": 3, "applies_to_categories": "all", "conditions_ar": "الدفع كاملاً كاش داخل الفرع.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-06", "title_ar": "خصم الشركات للكميات", "description_ar": "خصم للشركات عند شراء أجهزة بكميات كبيرة.", "discount_type": "percentage", "discount_value": 12, "applies_to_categories": ["LAP", "DSK", "MPC"], "conditions_ar": "طلب شركات موثق بأكثر من 10 أجهزة.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-07", "title_ar": "عرض تريد إن (Trade-In)", "description_ar": "رصيد شراء مقابل تسليم جهاز قديم يعمل.", "discount_type": "fixed_amount", "discount_value": None, "applies_to_categories": "all", "conditions_ar": "الجهاز القديم يعمل ويتم تقييمه في الفرع قبل احتساب الرصيد.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-08", "title_ar": "خصم موسم الألعاب", "description_ar": "خصم على لابتوبات الألعاب وكروت الشاشة.", "discount_type": "percentage", "discount_value": 8, "applies_to_categories": ["GLP", "CMP"], "conditions_ar": "خلال شهر نوفمبر فقط.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-09", "title_ar": "عرض تجميع الجهاز المخصص", "description_ar": "خصم على أسعار القطع عند تجميع جهاز كامل.", "discount_type": "percentage", "discount_value": 5, "applies_to_categories": ["CMP"], "conditions_ar": "تجميع جهاز كامل من 4 قطع فأكثر في نفس الطلب.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-10", "title_ar": "خصم أعضاء برنامج الولاء", "description_ar": "خصم دائم لأعضاء برنامج الولاء.", "discount_type": "percentage", "discount_value": 3, "applies_to_categories": "all", "conditions_ar": "عضوية برنامج الولاء فعالة.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-11", "title_ar": "عرض الشاشة المجانية مع Desktop Creator", "description_ar": "شاشة NovaView مجانية عند شراء أجهزة Desktop Creator.", "discount_type": "bundle", "discount_value": None, "applies_to_categories": ["DSK"], "conditions_ar": "شراء Desktop Creator 1 أو Desktop Creator 2 خلال فترة العرض.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-12", "title_ar": "خصم شهر رمضان", "description_ar": "خصم موسمي على جميع الفئات خلال شهر رمضان.", "discount_type": "percentage", "discount_value": 7, "applies_to_categories": "all", "conditions_ar": "خلال شهر رمضان فقط.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-13", "title_ar": "باقة المكتب المنزلي", "description_ar": "ديسكتوب مع شاشة وكيبورد وماوس بسعر مخفض.", "discount_type": "fixed_amount", "discount_value": 2000, "applies_to_categories": ["DSK", "MON", "KEY", "MSE"], "conditions_ar": "شراء عناصر الباقة الأربعة معًا في نفس الطلب.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-14", "title_ar": "خصم أول طلب", "description_ar": "خصم للعملاء الجدد على أول طلب لهم.", "discount_type": "percentage", "discount_value": 5, "applies_to_categories": "all", "conditions_ar": "أول طلب فقط لكل عميل جديد.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-15", "title_ar": "عرض الجملة للمدارس", "description_ar": "خصم على توريد الأجهزة للمؤسسات التعليمية.", "discount_type": "percentage", "discount_value": 15, "applies_to_categories": ["LAP", "DSK", "TAB"], "conditions_ar": "توريد أكثر من 20 جهازًا لمؤسسة تعليمية واحدة.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-16", "title_ar": "خصم شراء الضمان الممتد المبكر", "description_ar": "خصم ثابت عند شراء الضمان الممتد سريعًا بعد الشراء.", "discount_type": "fixed_amount", "discount_value": 100, "applies_to_categories": "all", "conditions_ar": "الشراء خلال 7 أيام من تاريخ شراء الجهاز.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-17", "title_ar": "عرض الجيمنج الكامل", "description_ar": "لابتوب ألعاب مع سماعة وماوس ألعاب بسعر مخفض.", "discount_type": "fixed_amount", "discount_value": 3000, "applies_to_categories": ["GLP", "AUD", "MSE"], "conditions_ar": "شراء العناصر الثلاثة معًا خلال فترة العرض.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-18", "title_ar": "خصم تجديد تراخيص البرامج", "description_ar": "خصم عند تجديد ترخيص برنامج قائم قبل انتهائه.", "discount_type": "percentage", "discount_value": 10, "applies_to_categories": ["SFT"], "conditions_ar": "تجديد ترخيص قائم قبل تاريخ انتهائه.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-19", "title_ar": "عرض الجهاز اللوحي للطلاب", "description_ar": "خصم للطلاب على فئة الأجهزة اللوحية.", "discount_type": "percentage", "discount_value": 8, "applies_to_categories": ["TAB"], "conditions_ar": "بشرط تقديم إثبات طالب ساري.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-20", "title_ar": "خصم أجهزة الشبكات للشركات", "description_ar": "خصم للشركات عند شراء معدات شبكات بكميات.", "discount_type": "percentage", "discount_value": 10, "applies_to_categories": ["NET"], "conditions_ar": "طلب شركات بأكثر من 3 قطع في نفس الطلب.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-21", "title_ar": "عرض عيد الأم", "description_ar": "خصم موسمي على الأجهزة اللوحية والصوتيات والكاميرات.", "discount_type": "percentage", "discount_value": 10, "applies_to_categories": ["TAB", "AUD", "CAM"], "conditions_ar": "خلال أسبوع عيد الأم فقط.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-22", "title_ar": "عرض الشحن المجاني المخفض", "description_ar": "خفض حد الشحن المجاني مؤقتًا خلال فترة العرض.", "discount_type": "fixed_amount", "discount_value": None, "applies_to_categories": "all", "conditions_ar": "يسري خلال فترة العرض فقط على الطلبات فوق 3000 جنيه بدلًا من 5000 جنيه.", "stackable": False, "status": "seasonal"},
    {"id": "OFF-23", "title_ar": "عرض تجديد الأجهزة القديمة للشركات", "description_ar": "خصم إضافي للشركات عند استبدال أجهزة قديمة بأخرى جديدة.", "discount_type": "percentage", "discount_value": 10, "applies_to_categories": ["LAP", "DSK"], "conditions_ar": "تسليم 5 أجهزة قديمة فأكثر ضمن برنامج تريد إن للشركات.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-24", "title_ar": "خصم منتجات الكمية المحدودة", "description_ar": "خصم إضافي على المنتجات المتبقية بكمية محدودة.", "discount_type": "percentage", "discount_value": 5, "applies_to_categories": "all", "conditions_ar": "يسري فقط على المنتجات التي حالتها كمية محدودة.", "stackable": False, "status": "ongoing"},
    {"id": "OFF-25", "title_ar": "باقة المصممين الاحترافية", "description_ar": "جهاز Desktop Creator مع شاشة 4K بسعر مخفض.", "discount_type": "fixed_amount", "discount_value": 2500, "applies_to_categories": ["DSK", "MON"], "conditions_ar": "شراء جهاز من فئة Desktop Creator مع شاشة من فئة 4K معًا.", "stackable": False, "status": "ongoing"},
]

assert len(OFFERS) == len({o["id"] for o in OFFERS}), "duplicate offer id"


# ==========================================
# Policy documents (Markdown)
# ==========================================

RETURN_POLICY_MD = """# سياسة الاسترجاع

يحق للعميل استرجاع أي منتج خلال 14 يومًا من تاريخ استلامه، بشرط أن يكون المنتج بحالته الأصلية وغير مستخدم بشكل يخالف شروط الاسترجاع.

## الشروط العامة

يجب تقديم فاتورة الشراء الأصلية أو إيصال الطلب عند طلب الاسترجاع.

يجب أن يكون المنتج في عبوته الأصلية مع جميع الملحقات والهدايا المرفقة إن وجدت.

لا يمكن استرجاع المنتجات التي تحتوي على أضرار ناتجة عن سوء الاستخدام أو كسر أو تلف بالسوائل.

## المنتجات غير القابلة للاسترجاع

تراخيص البرامج الرقمية بعد التفعيل غير قابلة للاسترجاع.

المنتجات الاستهلاكية التي تم فتح عبوتها مثل الكابلات المقطوعة حسب الطلب غير قابلة للاسترجاع.

## طريقة الاسترجاع

يمكن تقديم طلب الاسترجاع من خلال زيارة أقرب فرع، أو التواصل مع خدمة العملاء لترتيب استلام المنتج من العنوان.

## مدة استرداد المبلغ

بعد فحص المنتج والموافقة على الاسترجاع، يتم استرداد المبلغ خلال 3 إلى 7 أيام عمل بنفس وسيلة الدفع المستخدمة عند الشراء، أو تحويل بنكي في حالة الدفع عند الاستلام.

مصاريف الشحن الأصلية غير قابلة للاسترداد إلا في حالة استلام منتج تالف أو غير مطابق للطلب.
"""

EXCHANGE_POLICY_MD = """# سياسة الاستبدال

يمكن استبدال المنتج خلال 14 يومًا من تاريخ الشراء في حالة وجود عيب مصنعي أو إذا كان المنتج غير مطابق للطلب.

في حالة الاستبدال بسبب تغيير رأي العميل، يجب أن يكون المنتج بحالته الأصلية دون استخدام، وقد تُطبق شروط إضافية حسب حالة المنتج وفئته.

## استبدال بسبب عيب مصنعي

عند اكتشاف عيب مصنعي، يتم استبدال المنتج بنفس الموديل مجانًا. في حالة عدم توفر نفس الموديل، يمكن للعميل اختيار منتج بديل بفارق السعر إن وجد.

## استبدال بسبب تغيير المواصفات

يمكن استبدال المنتج بموديل آخر من نفس الفئة، مع دفع أو استرداد فارق السعر حسب الحالة.

## المدة الزمنية لمعالجة طلب الاستبدال

يتم معالجة طلبات الاستبدال خلال 3 إلى 5 أيام عمل من استلام المنتج في الفرع أو مركز الصيانة.
"""

SHIPPING_POLICY_MD = """# سياسة الشحن والتوصيل

الشحن داخل القاهرة والجيزة يستغرق من يوم إلى يومين عمل.

الشحن إلى باقي محافظات مصر يستغرق من 2 إلى 5 أيام عمل حسب المحافظة.

الطلبات التي يتم تأكيدها بعد الساعة 6 مساءً قد يتم تجهيزها في يوم العمل التالي.

## تكلفة الشحن

الشحن مجاني للطلبات التي تزيد قيمتها عن 5000 جنيه.

الطلبات الأقل من 5000 جنيه تخضع لرسوم شحن تختلف حسب المحافظة، ويمكن معرفة قيمة رسوم الشحن عند إتمام الطلب.

## تتبع الطلب

يمكن للعميل متابعة حالة الطلب باستخدام رقم الطلب من خلال التواصل مع خدمة العملاء أو زيارة الفرع الأقرب.

## الشحن الدولي

لا تقدم NovaTech حاليًا خدمة الشحن خارج جمهورية مصر العربية.

## استلام الطلب من الفرع

يمكن للعميل اختيار استلام الطلب من أقرب فرع بدلاً من التوصيل، وفي هذه الحالة لا تُطبق رسوم شحن.
"""

WARRANTY_POLICY_MD = """# سياسة الضمان

تحصل معظم الأجهزة الجديدة على ضمان الشركة المصنعة يبدأ من تاريخ الشراء، وتختلف مدة الضمان حسب فئة المنتج كما هو موضح في بيانات كل منتج.

الفئة العامة لأجهزة الكمبيوتر واللابتوب والمكونات تحصل على ضمان لمدة 12 شهرًا ضد عيوب التصنيع.

أجهزة التخزين (SSD وNVMe) تحصل على ضمان ممتد يصل إلى 24 شهرًا.

الكابلات والإكسسوارات البسيطة تحصل على ضمان 6 أشهر.

تراخيص البرامج لا تخضع لضمان الأجهزة، وإنما لشروط الترخيص الخاصة بكل برنامج، والمذكورة عند الشراء.

## ما لا يغطيه الضمان

الضمان لا يغطي الكسر أو التلف الناتج عن السوائل أو سوء الاستخدام أو التعديل غير المصرح به على الجهاز.

الضمان لا يغطي البطاريات الاستهلاكية بعد مرور 6 أشهر من الاستخدام العادي إذا كان الانخفاض في الأداء ضمن الحدود الطبيعية.

## المطالبة بالضمان

يمكن المطالبة بالضمان من خلال زيارة أي فرع يحتوي على مركز صيانة، مع إحضار فاتورة الشراء أو بطاقة الضمان.

## الضمان الممتد

يمكن شراء خدمة الضمان الممتد لبعض فئات المنتجات خلال 30 يومًا من تاريخ الشراء، وتفاصيل الأسعار متاحة عند الشراء أو من خلال خدمة العملاء.
"""

PAYMENT_METHODS_MD = """# طرق الدفع

تتيح NovaTech عدة طرق للدفع لراحة العملاء.

## الدفع عند الاستلام

متاح في معظم المحافظات، ويُستثنى من هذه الخدمة بعض المناطق النائية التي يتم تحديدها عند إتمام الطلب.

## البطاقات البنكية

يمكن الدفع باستخدام بطاقات Visa وMastercard عبر الموقع الإلكتروني أو داخل الفروع.

## المحافظ الإلكترونية

يمكن الدفع من خلال المحافظ الإلكترونية المدعومة مثل فودافون كاش وأورنج موني وإتصالات كاش.

## التحويل البنكي

متاح للطلبات الكبيرة وطلبات الشركات، ويتم تأكيد الطلب بعد تأكيد التحويل.

## الدفع بالتقسيط

تتوفر خدمة الدفع بالتقسيط عبر شركاء التمويل المعتمدين لبعض فئات المنتجات، وتختلف مدة التقسيط وشروط الموافقة حسب شركة التمويل.

بعض المنتجات مرتفعة السعر مثل أجهزة سطح المكتب المخصصة قد تتطلب دفعة مقدمة قبل التجهيز.

## فاتورة ضريبية للشركات

يمكن للشركات طلب فاتورة ضريبية رسمية عند الشراء من خلال تقديم البيانات الضريبية عند إتمام الطلب.
"""

CANCELLATION_POLICY_MD = """# سياسة إلغاء الطلب

يمكن إلغاء الطلب مجانًا في أي وقت قبل بدء عملية الشحن.

بعد شحن الطلب، يجب التواصل مع خدمة العملاء لمعرفة إمكانية الإلغاء، وقد تُخصم تكلفة الشحن في حالة الموافقة على الإلغاء بعد الشحن.

## إلغاء طلبات الدفع المسبق

في حالة إلغاء طلب تم دفعه مسبقًا قبل الشحن، يتم استرداد كامل المبلغ خلال 3 إلى 7 أيام عمل.

## إلغاء طلبات الشركات

طلبات الشركات ذات الكميات الكبيرة أو الطلبات المخصصة (مثل تجميع أجهزة بمواصفات خاصة) قد تخضع لشروط إلغاء مختلفة يتم توضيحها عند تأكيد الطلب.

## حالات الطلب

حالات الطلب المتاحة للمتابعة هي: قيد المراجعة، تم التأكيد، قيد التجهيز، تم الشحن، تم التسليم، أو تم الإلغاء.
"""

DISCOUNTS_OVERVIEW_MD = """# سياسة الخصومات والعروض

تقدم NovaTech مجموعة من العروض والخصومات الموسمية والدائمة على فئات مختلفة من المنتجات والخدمات.

## القاعدة العامة

لا يمكن الجمع بين أكثر من عرض أو خصم على نفس الطلب، ويتم تطبيق العرض الأعلى قيمة للعميل ما لم يُذكر خلاف ذلك صراحةً في تفاصيل العرض.

## خصم الطلاب

يحصل الطلاب على خصم على فئات محددة من الأجهزة بشرط تقديم إثبات طالب ساري مثل الكارنيه الجامعي.

## خصومات الكمية والطلبات الكبيرة

تُقدَّم خصومات خاصة للشركات والمؤسسات التعليمية عند شراء كميات كبيرة، ويتم تحديد نسبة الخصم حسب حجم الطلب.

## العروض الموسمية

تُطلق NovaTech عروضًا موسمية مثل خصومات الجمعة البيضاء وموسم العودة للمدارس ورمضان، ولكل عرض مدة سريان محددة تُعلن عنها الشركة.

## صلاحية العروض

جميع العروض سارية خلال الفترة المحددة لكل عرض فقط، ولا تُطبق تلقائيًا بعد انتهاء تاريخ الصلاحية.
"""

BUSINESS_HOURS_MD = """# مواعيد العمل

مواعيد العمل العامة لجميع الفروع من السبت إلى الخميس، من الساعة 10 صباحًا حتى الساعة 8 مساءً.

يوم الجمعة إجازة رسمية لجميع الفروع.

## خدمة العملاء

خط خدمة العملاء متاح يوميًا من الساعة 11 صباحًا حتى الساعة 7 مساءً ما عدا يوم الجمعة.

## المواعيد في المناسبات والأعياد

قد تختلف مواعيد العمل خلال شهر رمضان والأعياد الرسمية، ويتم الإعلان عن أي تغيير في المواعيد من خلال قنوات التواصل الرسمية للشركة قبل بداية المناسبة بوقت كافٍ.

## الطلبات الإلكترونية

يمكن تقديم الطلبات عبر صفحة الشركة على ماسنجر في أي وقت، ويتم الرد عليها ومعالجتها خلال مواعيد عمل خدمة العملاء.
"""

CUSTOMER_SUPPORT_MD = """# خدمة الدعم الفني ودعم العملاء

يمكن للعميل التواصل مع خدمة العملاء للاستفسار عن المنتجات أو الطلبات أو المشاكل الفنية.

## قنوات التواصل

يمكن التواصل عبر صفحة NovaTech على ماسنجر، أو الاتصال المباشر بخط خدمة العملاء، أو البريد الإلكتروني، أو زيارة أقرب فرع.

## الدعم الفني للأجهزة

يساعد فريق الدعم الفني في حل مشاكل تشغيل الجهاز، وتثبيت التعريفات، ومشاكل نظام التشغيل Windows، ومشاكل الاتصال بالشبكة، والإرشادات الأساسية لاستخدام الجهاز.

الاستشارة الفنية الأولية عبر الهاتف أو ماسنجر مجانية، بينما تخضع أعمال الصيانة الفعلية داخل مراكز الصيانة لتقييم فني وتكلفة تُحدد حسب نوع العطل.

## زمن الاستجابة

يسعى فريق الدعم للرد على استفسارات العملاء عبر ماسنجر خلال دقائق خلال مواعيد العمل الرسمية، وخلال يوم عمل واحد كحد أقصى خارج هذه المواعيد.

## الشكاوى

يمكن تقديم أي شكوى من خلال خدمة العملاء أو زيارة الفرع، ويتم التعامل مع الشكاوى ومتابعتها حتى الوصول لحل مناسب للعميل.
"""


# ==========================================
# FAQ (Markdown, one blank-line-separated Q&A per chunk)
# ==========================================

_FAQ_PAIRS = [
    ("كيف أعرف سعر منتج معين؟", "يمكنك سؤال المساعد مباشرة باسم المنتج، أو التواصل مع خدمة العملاء، أو زيارة أقرب فرع."),
    ("كيف أطلب منتج أونلاين؟", "يمكنك تأكيد الطلب من خلال محادثة ماسنجر مع الفريق، وسيتم تجهيز الطلب بعد تأكيد البيانات وطريقة الدفع."),
    ("هل يوجد تطبيق موبايل لـNovaTech؟", "لا يوجد حاليًا تطبيق موبايل، ويمكن التسوق من خلال صفحة ماسنجر أو زيارة الفروع."),
    ("هل يمكن الشراء بدون إنشاء حساب؟", "نعم، يمكن إتمام الطلب كضيف من خلال ماسنجر أو داخل الفرع دون الحاجة لإنشاء حساب."),
    ("كيف أتابع حالة طلبي؟", "يمكن متابعة حالة الطلب باستخدام رقم الطلب من خلال التواصل مع خدمة العملاء."),
    ("ما هي حالات الطلب المختلفة؟", "قيد المراجعة، تم التأكيد، قيد التجهيز، تم الشحن، تم التسليم، أو تم الإلغاء."),
    ("هل الأسعار المعروضة شاملة الضريبة؟", "نعم، جميع الأسعار المعروضة شاملة لضريبة القيمة المضافة."),
    ("هل يمكن الحصول على فاتورة ضريبية؟", "نعم، يمكن للشركات طلب فاتورة ضريبية رسمية عند الشراء بتقديم البيانات الضريبية."),
    ("كم تستغرق مدة التوصيل؟", "من يوم إلى يومين داخل القاهرة والجيزة، ومن 2 إلى 5 أيام عمل لباقي المحافظات."),
    ("هل الشحن مجاني؟", "الشحن مجاني للطلبات التي تزيد قيمتها عن 5000 جنيه، وما دون ذلك تُطبق رسوم شحن حسب المحافظة."),
    ("هل يوجد شحن دولي؟", "لا، الشحن متاح داخل جمهورية مصر العربية فقط حاليًا."),
    ("هل يمكن استلام الطلب من الفرع بدلاً من التوصيل؟", "نعم، يمكن اختيار الاستلام من أقرب فرع دون رسوم شحن."),
    ("ما هي مدة سياسة الاسترجاع؟", "يمكن استرجاع المنتج خلال 14 يومًا من تاريخ الاستلام بحالته الأصلية."),
    ("هل يمكن استرجاع البرامج بعد التفعيل؟", "لا، تراخيص البرامج الرقمية غير قابلة للاسترجاع بعد التفعيل."),
    ("كم يستغرق استرداد المبلغ بعد الاسترجاع؟", "من 3 إلى 7 أيام عمل بنفس وسيلة الدفع الأصلية."),
    ("هل يمكن استبدال المنتج بموديل آخر؟", "نعم، يمكن استبدال المنتج بموديل آخر من نفس الفئة مع دفع أو استرداد فارق السعر."),
    ("ماذا لو وصل المنتج تالفًا؟", "يتم استبدال المنتج التالف فورًا مجانًا، ويُرجى التواصل مع خدمة العملاء بمجرد الاستلام مع صور للتلف."),
    ("ماذا لو استلمت منتج مختلف عن طلبي؟", "يُرجى التواصل الفوري مع خدمة العملاء لترتيب استبدال المنتج الصحيح دون أي تكلفة إضافية."),
    ("ما هي مدة الضمان على اللابتوبات؟", "12 شهرًا ضد عيوب التصنيع من تاريخ الشراء."),
    ("هل الضمان يغطي كسر الشاشة؟", "لا، الضمان لا يغطي الكسر أو التلف الناتج عن سوء الاستخدام."),
    ("كيف أطالب بالضمان؟", "بزيارة أي فرع يحتوي مركز صيانة مع إحضار فاتورة الشراء أو بطاقة الضمان."),
    ("هل يمكن شراء ضمان ممتد؟", "نعم، يمكن شراء خدمة الضمان الممتد خلال 30 يومًا من تاريخ الشراء لبعض الفئات."),
    ("ما هي مدة ضمان أجهزة SSD؟", "تحصل أجهزة SSD وNVMe على ضمان ممتد يصل إلى 24 شهرًا."),
    ("ما هي طرق الدفع المتاحة؟", "الدفع عند الاستلام، بطاقات Visa وMastercard، المحافظ الإلكترونية، والتحويل البنكي."),
    ("هل يوجد نظام تقسيط؟", "نعم، يتوفر الدفع بالتقسيط عبر شركاء التمويل المعتمدين لبعض المنتجات."),
    ("هل الدفع عند الاستلام متاح في كل المحافظات؟", "متاح في معظم المحافظات باستثناء بعض المناطق النائية التي تُحدد عند إتمام الطلب."),
    ("هل يمكن إلغاء الطلب بعد تأكيده؟", "نعم، يمكن إلغاء الطلب مجانًا قبل بدء الشحن."),
    ("ماذا لو أردت الإلغاء بعد الشحن؟", "يجب التواصل مع خدمة العملاء، وقد تُخصم تكلفة الشحن في حالة الموافقة على الإلغاء."),
    ("هل يوجد خصم للطلاب؟", "نعم، يوجد خصم على فئات محددة بشرط تقديم إثبات طالب ساري."),
    ("هل يمكن الجمع بين أكثر من عرض؟", "لا، لا يمكن الجمع بين أكثر من عرض أو خصم على نفس الطلب."),
    ("هل توجد خصومات للشركات عند شراء كميات كبيرة؟", "نعم، تُقدَّم خصومات خاصة للشركات والمؤسسات التعليمية حسب حجم الطلب."),
    ("ما هي مواعيد عمل الفروع؟", "من السبت إلى الخميس من 10 صباحًا حتى 8 مساءً، ويوم الجمعة إجازة."),
    ("هل مواعيد العمل تتغير في رمضان؟", "قد تختلف المواعيد خلال رمضان والأعياد، ويُعلن عن أي تغيير مسبقًا عبر قنوات التواصل الرسمية."),
    ("كيف أتواصل مع خدمة العملاء؟", "عبر ماسنجر، أو الاتصال المباشر، أو البريد الإلكتروني، أو زيارة أقرب فرع."),
    ("هل الاستشارة الفنية مجانية؟", "نعم، الاستشارة الفنية الأولية عبر الهاتف أو ماسنجر مجانية."),
    ("هل الصيانة مجانية؟", "أعمال الصيانة الفعلية تخضع لتقييم فني وتكلفة تُحدد حسب نوع العطل، ما لم تكن مشمولة بالضمان."),
    ("هل يمكن إحضار الجهاز للصيانة في أي فرع؟", "يمكن إحضار الجهاز لأي فرع يحتوي على مركز صيانة."),
    ("كم تستغرق مدة إصلاح الجهاز؟", "تختلف حسب نوع العطل، ويتم إبلاغ العميل بالمدة المتوقعة عند تسليم الجهاز للفحص."),
    ("هل يوجد نسخ احتياطي للبيانات قبل الصيانة؟", "يُنصح العميل بعمل نسخة احتياطية لبياناته قبل تسليم الجهاز، وتتوفر خدمة النسخ الاحتياطي كخدمة إضافية."),
    ("هل تبيع NovaTech أجهزة مستعملة أو مجددة؟", "لا، تبيع NovaTech أجهزة جديدة فقط حاليًا."),
    ("هل يوجد برنامج استبدال الأجهزة القديمة (تريد إن)؟", "نعم، تتوفر خدمة تقييم واستبدال الأجهزة المستعملة مقابل رصيد شراء، ويمكن الاستفسار عن التفاصيل من خدمة العملاء."),
    ("هل يمكن تجميع جهاز كمبيوتر بمواصفات مخصصة؟", "نعم، تقدم NovaTech خدمة تجميع أجهزة كمبيوتر مخصصة حسب طلب العميل ومكوناتها."),
    ("هل يمكن الحصول على عرض سعر للشركات؟", "نعم، يمكن طلب عرض سعر مخصص للشركات من خلال التواصل مع خدمة العملاء."),
    ("هل توجد خدمة توريد لمدارس وجامعات؟", "نعم، تقدم NovaTech توريد أجهزة للمؤسسات التعليمية بشروط خاصة."),
    ("هل توجد عقود صيانة سنوية للشركات؟", "نعم، تتوفر عقود صيانة سنوية للشركات حسب عدد الأجهزة واحتياجات العميل."),
    ("كيف أعرف إذا كان منتج معين متوفر؟", "يمكن السؤال المباشر عن المنتج، وسيتم إخبارك بحالة التوفر الحالية."),
    ("ماذا يعني كمية محدودة؟", "يعني أن المخزون المتاح من هذا المنتج محدود وقد ينفد قريبًا."),
    ("هل يمكن حجز منتج غير متوفر حاليًا؟", "يمكن التواصل مع خدمة العملاء لمعرفة الموعد المتوقع لتوفر المنتج مجددًا."),
    ("هل الفروع كلها تقدم نفس الخدمات؟", "تقدم معظم الفروع نفس الخدمات الأساسية، وبعض الفروع الكبرى فقط تحتوي على مراكز صيانة متكاملة."),
    ("كيف أعرف أقرب فرع لي؟", "يمكنك سؤال المساعد عن اسم المدينة أو المنطقة، وسيتم إخبارك بأقرب فرع وعنوانه."),
    ("هل يمكن الدفع بعملات أجنبية؟", "لا، جميع المعاملات تتم بالجنيه المصري فقط."),
    ("هل يوجد حد أدنى لقيمة الطلب؟", "لا يوجد حد أدنى لقيمة الطلب للشراء من الفروع أو أونلاين."),
    ("هل يمكن تغيير عنوان التوصيل بعد تأكيد الطلب؟", "يمكن التواصل مع خدمة العملاء لتعديل العنوان قبل بدء عملية الشحن."),
    ("هل يمكن طلب أكثر من منتج في نفس الطلب؟", "نعم، يمكن إضافة أكثر من منتج في نفس الطلب قبل التأكيد."),
    ("هل تقدم NovaTech ضمان استرداد فرق السعر عند انخفاضه لاحقًا؟", "لا يوجد حاليًا برنامج ضمان استرداد فرق السعر."),
    ("هل يوجد برنامج ولاء للعملاء؟", "نعم، يحصل العملاء المتكررون على عروض وأولوية إشعار بالمنتجات الجديدة والخصومات."),
    ("كيف أعرف مواصفات منتج معين بالتفصيل؟", "يمكنك سؤال المساعد باسم المنتج وسيتم عرض كل المواصفات المتاحة."),
    ("هل يمكن مقارنة منتجين قبل الشراء؟", "نعم، يمكنك سؤال المساعد عن الفروقات بين منتجين لمساعدتك في اتخاذ القرار."),
    ("هل الدعم الفني يعمل عن بُعد؟", "نعم، يمكن الحصول على دعم فني عن بُعد لبعض المشاكل البرمجية البسيطة عبر مكالمة أو محادثة."),
    ("ما هي لغات الدعم المتاحة؟", "يقدم فريق الدعم المساعدة باللغتين العربية والإنجليزية."),
]


def _build_faq_markdown() -> str:

    blocks = ["# الأسئلة الشائعة"]

    for question, answer in _FAQ_PAIRS:
        blocks.append(f"س: {question}\nج: {answer}")

    return "\n\n".join(blocks) + "\n"


FAQ_MD = _build_faq_markdown()


# ==========================================
# Writers
# ==========================================

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:

    products = assemble_products()

    counts_by_category: dict[str, int] = {}
    for product in products:
        counts_by_category[product["category_id"]] = (
            counts_by_category.get(product["category_id"], 0) + 1
        )

    categories = [
        {**category, "product_count": counts_by_category.get(category["id"], 0)}
        for category in CATEGORIES
    ]

    _write_json(KB_DIR / "company" / "company_info.json", COMPANY_INFO)
    _write_json(KB_DIR / "catalog" / "categories.json", categories)
    _write_json(KB_DIR / "catalog" / "products.json", products)
    _write_json(KB_DIR / "branches" / "branches.json", BRANCHES)
    _write_json(KB_DIR / "services" / "services.json", SERVICES)
    _write_json(KB_DIR / "offers" / "offers.json", OFFERS)

    _write_text(KB_DIR / "policies" / "return_policy.md", RETURN_POLICY_MD)
    _write_text(KB_DIR / "policies" / "exchange_policy.md", EXCHANGE_POLICY_MD)
    _write_text(KB_DIR / "policies" / "shipping_policy.md", SHIPPING_POLICY_MD)
    _write_text(KB_DIR / "policies" / "warranty_policy.md", WARRANTY_POLICY_MD)
    _write_text(KB_DIR / "policies" / "payment_methods.md", PAYMENT_METHODS_MD)
    _write_text(KB_DIR / "policies" / "cancellation_policy.md", CANCELLATION_POLICY_MD)
    _write_text(KB_DIR / "policies" / "discounts_and_offers.md", DISCOUNTS_OVERVIEW_MD)
    _write_text(KB_DIR / "policies" / "business_hours.md", BUSINESS_HOURS_MD)
    _write_text(KB_DIR / "policies" / "customer_support.md", CUSTOMER_SUPPORT_MD)

    _write_text(KB_DIR / "faq" / "faq.md", FAQ_MD)

    print(f"Categories: {len(categories)}")
    print(f"Products:   {len(products)}")
    print(f"Branches:   {len(BRANCHES)}")
    print(f"Services:   {len(SERVICES)}")
    print(f"Offers:     {len(OFFERS)}")
    print(f"FAQ pairs:  {len(_FAQ_PAIRS)}")
    print(f"Policy docs: 9")


if __name__ == "__main__":
    main()
