"""Generation layer: builds the route-specific prompt and gets the reply.

Despite the module name (kept as-is so app/services/message_processor.py's
import doesn't need to change), text generation runs on Groq
(llama-3.3-70b-versatile), not Gemini. Gemini is still used elsewhere in
app/ai/ for embeddings only (see app/ai/embeddings.py, app/ai/rag.py) -
that part is untouched.
"""

from groq import Groq, GroqError

from app.config import GROQ_API_KEY
from app.ai.router import route_message, Route


groq_client = Groq(
    api_key=GROQ_API_KEY
)

_GROQ_MODEL = "llama-3.3-70b-versatile"


# out_of_scope is answered directly, without a generation call: retrieval found
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

    try:
        response = groq_client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    except GroqError as error:

        print("Groq generation error:", error)

        return _FALLBACK_REPLY

    reply = response.choices[0].message.content

    if not reply:
        return _FALLBACK_REPLY

    return reply.strip()
