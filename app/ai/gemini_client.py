from google import genai

from app.config import GEMINI_API_KEY
from app.ai.rag import (
    company_chunks,
    company_bm25_index,
    company_embeddings,
    search_company
)


gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_ai_reply(
    customer_message: str
) -> str:

    results = search_company(
        question=customer_message,
        chunks=company_chunks,
        chunk_embeddings=company_embeddings,
        bm25_index=company_bm25_index,
        top_k=3
    )

    print("Retrieved results:")
    print(results)

    if results:
        context = "\n\n".join(
            result["chunk"]
            for result in results
        )
    else:
        context = "لا توجد معلومات مرتبطة بالسؤال."


    prompt = f"""
أنت مساعد خدمة عملاء لشركة NovaTech.

استخدم Context فقط للإجابة عن أسئلة الشركة.

القواعد:

- لا تخترع أي معلومات.
- إذا كانت المعلومة غير موجودة في Context، قل:
"لا توجد معلومات كافية في بيانات الشركة."
- إذا كانت الرسالة مجرد تحية أو شكر أو مجاملة،
  رد بشكل طبيعي ومختصر.
- اجعل الرد قصيرًا وواضحًا ومناسبًا لـMessenger.
- لا تذكر أنك تستخدم RAG أو Context أو نموذج ذكاء اصطناعي.

Context:
{context}

رسالة العميل:
{customer_message}
"""


    response = gemini_client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    if not response.text:
        return (
            "عذرًا، لم أتمكن من إنشاء الرد حاليًا."
        )

    return response.text.strip()
