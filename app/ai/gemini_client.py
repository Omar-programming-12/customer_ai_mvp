"""Generation layer: builds the route-specific prompt and gets the reply.

Despite the module name (kept as-is so app/services/message_processor.py's
import doesn't need to change), text generation runs on Groq
(openai/gpt-oss-120b), not Gemini. Gemini is still used elsewhere in
app/ai/ for embeddings only (see app/ai/embeddings.py, app/ai/rag.py) -
that part is untouched.

For the two company routes, Groq is given the structured-data tools in
app/ai/tools.py (product/branch/service/offer lookups) alongside the usual
RAG context, and decides for itself whether a question needs an exact
structured fact or is answerable from the semantic context already
provided - see _generate_with_tools. small_talk never gets tools (nothing
to look up); out_of_scope never reaches Groq at all.
"""

import json
import logging

from groq import Groq, GroqError

from app.config import GROQ_API_KEY
from app.ai.router import route_message, Route
from app.ai import tools


logger = logging.getLogger(__name__)

groq_client = Groq(
    api_key=GROQ_API_KEY
)

_GROQ_MODEL = "openai/gpt-oss-120b"

# Caps the number of tool-call round-trips per customer message, so a
# model that keeps requesting tools can never loop indefinitely. Two is
# enough for anything in this app's scope (e.g. search_products then
# get_product_details to confirm one exact match) - if the model still
# wants a tool after that, the final call below forces a plain-text
# answer from whatever it has already gathered.
_MAX_TOOL_ROUNDS = 2


# out_of_scope is answered directly, without a generation call: retrieval found
# no meaningful signal at all, so there is nothing genuine to generate from,
# and a fixed reply can't drift into treating the question as a company
# question it has no answer for.
_OUT_OF_SCOPE_REPLY = "أنا هنا للمساعدة في استفسارات NovaTech فقط 🙂"

# unsupported_category is also answered directly, without RAG or a
# generation call: the router already found a deterministic, explicit
# mention of something we don't carry (decision.context holds its Arabic
# label) - there's nothing for retrieval or the model to add, and letting
# either run risks exactly the bug this route exists to prevent (a noisy
# semantic match surfacing an unrelated product instead of a clear "not
# available").
_UNSUPPORTED_CATEGORY_REPLY_TEMPLATE = "عذرًا، لا نوفر حاليًا {label} في NovaTech 🙂"

_FALLBACK_REPLY = "عذرًا، لم أتمكن من إنشاء الرد حاليًا."


_TOOL_USAGE_RULES = """
- لديك أدوات (tools) تجلب بيانات دقيقة ومباشرة من قاعدة بيانات الشركة: أسعار
  ومواصفات المنتجات، بيانات الفروع، الخدمات، والعروض الحالية.
- إذا كان سؤال العميل عن سعر/مواصفات منتج، توصية منتج، فرع محدد، خدمة، أو
  عرض حالي - استخدم الأداة المناسبة للحصول على البيانات الدقيقة، بدل تخمين
  الإجابة من الـContext وحده.
- إذا أرجعت الأداة نتيجة فارغة (لا يوجد منتج/فرع/عرض مطابق)، فهذا يعني أن
  هذا الصنف غير متوفر لدى الشركة فعليًا - قل ذلك بوضوح، ولا تخترع بديلاً
  غير موجود في نتيجة الأداة أو في الـContext.
- إذا كان الـContext الحالي غير كافٍ للإجابة عن سؤال عام/سياسة، ورأيت أن
  صياغة العميل قد لا تكون تطابقت جيدًا (مثلاً كلمة عامية أو مكتوبة بحروف
  لاتينية)، استخدم search_knowledge_base بصياغة أوضح قبل أن تقول إن
  المعلومة غير متوفرة.
"""

_COMPANY_CONFIDENT_PROMPT = """
أنت مساعد خدمة عملاء لشركة NovaTech.

Route الحالي: company_confident.
الـContext التالي موثوق ومرتبط بسؤال العميل بشكل مؤكد.

القواعد:

- جاوب من الـContext فقط إن لم تحتج أداة، ولا تخترع أي معلومة غير موجودة فيه.
""" + _TOOL_USAGE_RULES + """
- اجعل الرد قصيرًا وواضحًا ومناسبًا لـMessenger.
- لا تذكر أنك تستخدم RAG أو Context أو أداة أو نموذج ذكاء اصطناعي أو كلمة route.

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
""" + _TOOL_USAGE_RULES + """
- إذا لم تُرجع أي أداة نتيجة واضحة، ولم يكن الـContext كافيًا للإجابة، قل حرفيًا:
"لا توجد معلومات كافية في بيانات الشركة."
- لا تخترع أي معلومة غير موجودة في نتيجة أداة أو في الـContext.
- اجعل الرد قصيرًا وواضحًا ومناسبًا لـMessenger.
- لا تذكر أنك تستخدم RAG أو Context أو أداة أو نموذج ذكاء اصطناعي أو كلمة route.

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

# Only the two company routes get structured-data tools - small_talk has
# nothing to look up, and out_of_scope never reaches Groq at all.
_ROUTES_WITH_TOOLS = {Route.COMPANY_CONFIDENT, Route.COMPANY_LOW_CONFIDENCE}


def _execute_tool_call(tool_call) -> dict:

    function_name = tool_call.function.name

    try:
        arguments = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        arguments = {}

    handler = tools.TOOL_FUNCTIONS.get(function_name)

    if handler is None:
        return {"error": f"unknown tool: {function_name}"}

    try:
        return handler(**arguments)
    except TypeError as error:
        return {"error": f"invalid arguments for {function_name}: {error}"}
    except Exception:
        # Any other failure inside a tool (a malformed knowledge_base
        # entry, an unexpected data shape, ...) should come back to the
        # model as a normal tool result it can react to - e.g. by telling
        # the customer the lookup failed - rather than bubbling up and
        # taking down the whole reply with the generic fallback message.
        logger.exception("Tool %s raised an unexpected error", function_name)
        return {"error": f"{function_name} failed unexpectedly"}


def _generate_with_tools(prompt: str, history: list[dict]) -> str | None:

    messages = [*history, {"role": "user", "content": prompt}]

    for _ in range(_MAX_TOOL_ROUNDS):

        response = groq_client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=messages,
            tools=tools.TOOL_SPECS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ],
        })

        for tool_call in message.tool_calls:

            result = _execute_tool_call(tool_call)

            logger.info(
                "Tool call: %s(%s) -> %s",
                tool_call.function.name,
                tool_call.function.arguments,
                result,
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    # Tool rounds exhausted but the model still wants to call one more -
    # force a plain-text answer from whatever tool results were already
    # gathered. Omitting `tools` here is NOT enough to stop it: the
    # conversation history still shows a tool-calling pattern (assistant
    # tool_calls -> tool result, twice), and the model can still emit a
    # tool_call in its output regardless of what this request declares.
    # Groq then rejects the whole request with 400 "Tool choice is none,
    # but model called a tool" - a real, reproduced failure, not a
    # hypothetical one. Explicitly passing tool_choice="none" (with the
    # schema still attached so the choice is meaningful) is what actually
    # constrains the model server-side to text-only output.
    final_response = groq_client.chat.completions.create(
        model=_GROQ_MODEL,
        messages=messages,
        tools=tools.TOOL_SPECS,
        tool_choice="none",
    )

    return final_response.choices[0].message.content


def generate_ai_reply(
    customer_message: str,
    history: list[dict] | None = None,
) -> str | None:
    """Returns None for Route.MEANINGLESS specifically - a signal to the
    caller (app.services.message_processor) to send nothing back at all,
    not even a fixed reply. Every other route always returns a string."""

    decision = route_message(customer_message)

    logger.info("Route: %s", decision.route.value)

    if decision.route == Route.MEANINGLESS:
        return None

    if decision.route == Route.OUT_OF_SCOPE:
        return _OUT_OF_SCOPE_REPLY

    if decision.route == Route.UNSUPPORTED_CATEGORY:
        return _UNSUPPORTED_CATEGORY_REPLY_TEMPLATE.format(label=decision.context)

    history = history or []

    prompt = _PROMPTS[decision.route].format(
        context=decision.context or "",
        customer_message=customer_message,
    )

    try:
        if decision.route in _ROUTES_WITH_TOOLS:
            reply = _generate_with_tools(prompt, history)
        else:
            response = groq_client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=[
                    *history,
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            reply = response.choices[0].message.content

    except GroqError:

        logger.exception("Groq generation error")

        return _FALLBACK_REPLY

    if not reply:
        return _FALLBACK_REPLY

    return reply.strip()
