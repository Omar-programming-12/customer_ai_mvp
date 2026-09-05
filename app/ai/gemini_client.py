from google import genai

from app.config import GEMINI_API_KEY
from app.ai.router import route_message, Route


gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# out_of_scope is answered directly, without a Gemini call: retrieval found
# no meaningful signal at all, so there is nothing genuine to generate from,
# and a fixed reply can't drift into treating the question as a company
# question it has no answer for.
_OUT_OF_SCOPE_REPLY = "أنا هنا للمساعدة في استفسارات NovaTech فقط 🙂"

_FALLBACK_REPLY = "عذرًا، لم أتمكن من إنشاء الرد حاليًا."


_COMPANY_CONFIDENT_PROMPT = """
أنت مساعد خدمة عملاء لشركة NovaTech.

Route الحالي: company_confident.
الـContext التالي موثوق ومرتبط بسؤال العميل بشكل مؤكد.

القواعد:

- جاوب من الـContext فقط، ولا تخترع أي معلومة غير موجودة فيه.
- اجعل الرد قصيرًا وواضحًا ومناسبًا لـMessenger.
- لا تذكر أنك تستخدم RAG أو Context أو نموذج ذكاء اصطناعي أو كلمة route.

Context:
{context}

رسالة العميل:
{customer_message}
"""

_COMPANY_LOW_CONFIDENCE_PROMPT = """
أنت مساعد خدمة عملاء لشركة NovaTech.

Route الحالي: company_low_confidence.
الـContext التالي قد يكون مرتبطًا بسؤال العميل، لكنه غير مؤكد.

القواعد:

- استخدم الـContext فقط إذا كان يجيب عن سؤال العميل بوضوح تام.
- إذا لم يكن الـContext كافيًا أو واضحًا للإجابة، قل حرفيًا:
"لا توجد معلومات كافية في بيانات الشركة."
- لا تخترع أي معلومة غير موجودة في الـContext.
- اجعل الرد قصيرًا وواضحًا ومناسبًا لـMessenger.
- لا تذكر أنك تستخدم RAG أو Context أو نموذج ذكاء اصطناعي أو كلمة route.

Context:
{context}

رسالة العميل:
{customer_message}
"""

_SMALL_TALK_PROMPT = """
أنت مساعد خدمة عملاء لشركة NovaTech.

Route الحالي: small_talk.
رسالة العميل مجرد تحية أو شكر أو مجاملة، وليست سؤالًا عن الشركة.

القواعد:

- رد بشكل طبيعي وودود ومختصر يناسب محادثة Messenger.
- لا تقدم أي معلومات عن الشركة ما لم يُطلب ذلك صراحة.
- لا تذكر أنك تستخدم نموذج ذكاء اصطناعي أو كلمة route.

رسالة العميل:
{customer_message}
"""

_PROMPTS = {
    Route.COMPANY_CONFIDENT: _COMPANY_CONFIDENT_PROMPT,
    Route.COMPANY_LOW_CONFIDENCE: _COMPANY_LOW_CONFIDENCE_PROMPT,
    Route.SMALL_TALK: _SMALL_TALK_PROMPT,
}


def generate_ai_reply(
    customer_message: str
) -> str:

    decision = route_message(customer_message)

    print("Route:", decision.route.value)

    if decision.route == Route.OUT_OF_SCOPE:
        return _OUT_OF_SCOPE_REPLY

    prompt = _PROMPTS[decision.route].format(
        context=decision.context or "",
        customer_message=customer_message,
    )

    response = gemini_client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    if not response.text:
        return _FALLBACK_REPLY

    return response.text.strip()
