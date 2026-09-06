"""Routing layer: decides how a customer message should be handled before
any Gemini generation call, without adding an extra Gemini call to do it.

Every message resolves to exactly one route:

- meaningless:
    No letters or digits at all after normalization - pure punctuation,
    whitespace, or repeated symbols ("؟؟", "...", "   "). Checked first,
    before everything else, purely locally: no reply is sent at all (see
    app.ai.gemini_client.generate_ai_reply / app.services.
    message_processor), and no RAG/BM25/embedding/Groq call happens.
    Deliberately narrower than "tokenize() found nothing": a message that
    IS just a stopword (e.g. "كام؟") still has real letters and a
    plausible, if underspecified, intent - only a complete absence of any
    letter/digit is treated as non-actionable.
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
- unsupported_category:
    The question explicitly names a product category we're known NOT to
    carry (mobile phones, cameras - see
    knowledge_base/catalog/unsupported_categories.json). Checked first,
    before any retrieval: a clear mention here is deterministic evidence
    that overrides whatever RAG/semantic noise might otherwise suggest -
    e.g. "موبايل في حدود 7000" used to surface an unrelated tablet purely
    because it scored well by embedding coincidence. context carries the
    category's Arabic label for the reply.
- out_of_scope:
    Retrieval found no meaningful signal at all, AND the question doesn't
    even share a word with the company's product/service domain - it isn't
    about anything in the knowledge base (a general-knowledge question, a
    joke request, etc). A question that names something we clearly sell or
    service (e.g. "اقترحلي جهاز للبرمجة") but didn't match any specific
    chunk well is routed company_low_confidence instead - it's on-topic,
    just not confidently answerable, which is a different thing from not
    being about us at all (see app/ai/entities.py's category vocabulary).

A message that opens with a greeting but also asks something concrete
(e.g. "صباح الخير، بكام Gaming X؟") is NOT small_talk: only a message that
is *entirely* greeting/thanks/farewell content skips retrieval.

If the first attempt finds nothing at all (confidence "none" and no
domain-vocabulary match), one more attempt runs against a best-effort
Franco-Arabic transliteration of the message (see
app.ai.normalize.transliterate_franco_arabic) before settling on
out_of_scope - a customer writing Arabic in Latin letters/digits (e.g.
"3andko far3 f tanta?") would otherwise never match anything, since
neither the embeddings, the domain vocabulary, nor the entity anchors
have Latin-script text to compare against. This retry never overrides a
result the original text already found, so it can't regress an
already-working case - it only ever helps a case that would otherwise be
a flat rejection.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum

from app.ai import rag, entities
from app.ai.normalize import normalize_text, tokenize, transliterate_franco_arabic


logger = logging.getLogger(__name__)


class Route(str, Enum):
    MEANINGLESS = "meaningless"
    SMALL_TALK = "small_talk"
    COMPANY_CONFIDENT = "company_confident"
    COMPANY_LOW_CONFIDENCE = "company_low_confidence"
    UNSUPPORTED_CATEGORY = "unsupported_category"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass
class RouteDecision:
    route: Route
    context: str | None = None


_WORD_CHAR_PATTERN = re.compile(r"\w", re.UNICODE)


def is_meaningless(message: str) -> bool:
    """True if the message has no letters or digits at all, once
    normalized - pure punctuation, whitespace, or repeated symbols. Not
    the same check as "tokenize() is empty": tokenize() also drops
    stopwords, which would wrongly catch a real (if terse) question like
    "كام؟" - this only fires when there is no actual word content to
    react to in the first place."""

    return not _WORD_CHAR_PATTERN.search(normalize_text(message))


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


def _retrieve(message: str):
    """One retrieval attempt: RAG search plus the domain-vocabulary check,
    both against the same text. Factored out so route_message can run it
    twice - once for the original message, once for its Franco-Arabic
    transliteration - without duplicating the two calls."""

    result = rag.search_company(
        question=message,
        chunks=rag.company_chunks,
        chunk_embeddings=rag.company_embeddings,
        bm25_index=rag.company_bm25_index,
        entity_anchors=rag.company_entity_anchors,
    )

    domain_match = entities.is_company_domain_query(message, rag.company_category_vocabulary)

    return result, domain_match


def route_message(message: str) -> RouteDecision:

    if is_meaningless(message):
        return RouteDecision(route=Route.MEANINGLESS)

    if is_small_talk(message):
        return RouteDecision(route=Route.SMALL_TALK)

    # Checked before any retrieval: a clear, explicit mention of a known-
    # unsupported category is deterministic evidence that must win over
    # whatever a noisy embedding score might otherwise suggest (an
    # unrelated tablet/laptop scoring well for "موبايل..." by coincidence).
    # No RAG/embedding call happens on this path at all.
    unsupported = entities.find_unsupported_category(
        message, rag.company_unsupported_category_anchors
    )

    if unsupported:
        return RouteDecision(route=Route.UNSUPPORTED_CATEGORY, context=unsupported["label"])

    result, domain_match = _retrieve(message)

    if result.confidence == "none" and not domain_match:

        transliterated = transliterate_franco_arabic(message)

        if transliterated != message:

            fallback_result, fallback_domain_match = _retrieve(transliterated)

            if fallback_result.confidence != "none" or fallback_domain_match:

                logger.info(
                    "Franco-Arabic fallback matched: %r -> %r",
                    message, transliterated,
                )

                result, domain_match = fallback_result, fallback_domain_match

    if result.confidence == "none":

        # No chunk was confident enough on its own, but the question still
        # names something in our product/service domain (e.g. "جهاز",
        # "جيمنج") - that's a company question we can't pin down precisely,
        # not an out-of-scope one. Surface the best-available chunks as
        # loose context; the low_confidence prompt already only uses them
        # if they clearly answer the question, and says so otherwise.
        if domain_match:
            return RouteDecision(
                route=Route.COMPANY_LOW_CONFIDENCE,
                context="\n\n".join(result.weak_chunks)
            )

        return RouteDecision(route=Route.OUT_OF_SCOPE)

    context = "\n\n".join(result.chunks)

    if result.confidence == "confident":
        return RouteDecision(route=Route.COMPANY_CONFIDENT, context=context)

    return RouteDecision(route=Route.COMPANY_LOW_CONFIDENCE, context=context)
