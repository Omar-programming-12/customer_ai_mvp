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

from groq import Groq, GroqError

from app.config import GROQ_API_KEY
from app.ai.router import route_message, Route
from app.ai import tools


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


def _generate_with_tools(prompt: str) -> str | None:

    messages = [{"role": "user", "content": prompt}]

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

            print("Tool call:", tool_call.function.name, tool_call.function.arguments, "->", result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    # Tool rounds exhausted but the model still wants to call one - force a
    # plain-text answer from whatever tool results were already gathered.
    final_response = groq_client.chat.completions.create(
        model=_GROQ_MODEL,
        messages=messages,
    )

    return final_response.choices[0].message.content


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
        if decision.route in _ROUTES_WITH_TOOLS:
            reply = _generate_with_tools(prompt)
        else:
            response = groq_client.chat.completions.create(
                model=_GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            reply = response.choices[0].message.content

    except GroqError as error:

        print("Groq generation error:", error)

        return _FALLBACK_REPLY

    if not reply:
        return _FALLBACK_REPLY

    return reply.strip()
