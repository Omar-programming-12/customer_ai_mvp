"""Routing layer: decides how a customer message should be handled before
any Gemini generation call, without adding an extra Gemini call to do it.

Every message resolves to exactly one route:

- small_talk:
    Greeting / thanks / farewell, nothing else in the message. Detected
    locally (regex over normalized text) - no embedding call, no BM25, no
    retrieval at all.
- company_confident:
    Retrieval found a chunk that is either a deterministic entity anchor
    (a known branch/city named in the question) or cleared the confident
    embedding-similarity bar on its own.
- company_low_confidence:
    Retrieval found some relevant signal, but nothing strong enough to
    trust as a definite answer by itself.
- out_of_scope:
    Retrieval found no meaningful signal at all - the question isn't about
    anything in the knowledge base (a general-knowledge question, a joke
    request, etc).

A message that opens with a greeting but also asks something concrete
(e.g. "صباح الخير، بكام Gaming X؟") is NOT small_talk: only a message that
is *entirely* greeting/thanks/farewell content skips retrieval.
"""

import re
from dataclasses import dataclass
from enum import Enum

from app.ai import rag
from app.ai.normalize import normalize_text, tokenize


class Route(str, Enum):
    SMALL_TALK = "small_talk"
    COMPANY_CONFIDENT = "company_confident"
    COMPANY_LOW_CONFIDENCE = "company_low_confidence"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass
class RouteDecision:
    route: Route
    context: str | None = None


# Small-talk phrases only: greetings, thanks, farewells, simple pleasantries.
# Deliberately narrow - a request like "احكيلي نكتة" (tell me a joke) is not
# a greeting/thanks/compliment, so it falls through to retrieval and (having
# no signal there) resolves to out_of_scope instead of small_talk.
_SMALL_TALK_PHRASES = [
    r"السلام عليكم", r"وعليكم السلام",
    r"صباح الخير", r"صباح النور",
    r"مساء الخير", r"مساء النور",
    r"اهلا(?: وسهلا)?", r"أهلا(?: وسهلا)?", r"يا هلا", r"هاي", r"هلا",
    r"ازيك", r"إزيك", r"عامل ايه", r"عامل إيه", r"اخبارك ايه", r"كيف حالك",
    r"شكرا(?: جزيلا)?", r"متشكرين?", r"تسلم(?:و[ا])?", r"يعطيك العافيه",
    r"مع السلامه", r"باي", r"تصبح على خير", r"نهارك سعيد",
]

_SMALL_TALK_PATTERN = re.compile(
    "|".join(f"(?:{phrase})" for phrase in _SMALL_TALK_PHRASES)
)


def is_small_talk(message: str) -> bool:

    normalized = normalize_text(message)

    if not _SMALL_TALK_PATTERN.search(normalized):
        return False

    # Strip every matched greeting/thanks/farewell phrase; if nothing
    # meaningful is left, the message was pure small talk. If a product,
    # question word, or anything else remains, it's a company query that
    # merely opens with a greeting.
    remainder = _SMALL_TALK_PATTERN.sub(" ", normalized)

    return len(tokenize(remainder)) == 0


def route_message(message: str) -> RouteDecision:

    if is_small_talk(message):
        return RouteDecision(route=Route.SMALL_TALK)

    result = rag.search_company(
        question=message,
        chunks=rag.company_chunks,
        chunk_embeddings=rag.company_embeddings,
        bm25_index=rag.company_bm25_index,
        entity_anchors=rag.company_entity_anchors,
    )

    if result.confidence == "none":
        return RouteDecision(route=Route.OUT_OF_SCOPE)

    context = "\n\n".join(result.chunks)

    if result.confidence == "confident":
        return RouteDecision(route=Route.COMPANY_CONFIDENT, context=context)

    return RouteDecision(route=Route.COMPANY_LOW_CONFIDENCE, context=context)
