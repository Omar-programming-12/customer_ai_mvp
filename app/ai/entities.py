"""Deterministic entity anchoring for retrieval.

Semantic/keyword search is probabilistic: a question that clearly names a
known entity (today: a branch or its city) can still lose to an unrelated
chunk that happens to score higher by embedding noise. For the small, fixed
set of entities we already know about from the knowledge base, we don't need
to guess - a plain text match is exact and free (no API call).

This module builds two different kinds of signal:

- Branch anchors (build_branch_anchors / find_anchor_matches): point at one
  specific chunk, and are strong enough to force that chunk to the front of
  retrieval and mark the route "confident". To extend this to another
  entity type later (e.g. products), add a `build_x_anchors()` function
  following the same shape (list of {"type", "label", "chunk_index",
  "aliases"} dicts, matched against the exact chunk text the renderer in
  knowledge_base.py produces) and merge it into rag.py's anchor list -
  nothing in `find_anchor_matches` is branch-specific.

- The category/domain vocabulary (build_category_vocabulary /
  is_company_domain_query) answers a different, weaker question: "is this
  message about our product/service domain at all?" - independent of
  whether any specific chunk scored well. It never points at a chunk and
  never forces or boosts retrieval; it only tells the router that a
  question with no confident chunk match still isn't out_of_scope, because
  it names something we clearly sell/service.
"""

import re

from app.ai.knowledge_base import (
    load_branches,
    load_categories,
    load_company_info,
    load_services,
    render_branch,
)
from app.ai.normalize import normalize_text, tokenize


def _branch_aliases(branch: dict) -> set[str]:

    aliases = {normalize_text(branch["city_ar"])}

    branch_name = normalize_text(branch["name_ar"])
    aliases.add(branch_name)

    if branch_name.startswith("فرع "):
        aliases.add(branch_name[len("فرع "):])

    return {alias for alias in aliases if alias}


def build_branch_anchors(chunks: list[str]) -> list[dict]:
    """One anchor per branch, pointing at the exact chunk `render_branch`
    produced for it - not a recomputed index - so it stays correct
    regardless of where load_all_chunks() places branches in the list."""

    anchors = []

    for branch in load_branches():

        chunk_text = render_branch(branch)

        try:
            chunk_index = chunks.index(chunk_text)
        except ValueError:
            # knowledge_base/ changed since this chunk list was built.
            # Skip rather than anchor to the wrong chunk or crash the app -
            # the (unanchored) semantic/keyword search still runs normally.
            continue

        anchors.append({
            "type": "branch",
            "label": branch["name_ar"],
            "chunk_index": chunk_index,
            "aliases": _branch_aliases(branch),
        })

    return anchors


def find_anchor_matches(question: str, anchors: list[dict]) -> list[dict]:
    """Anchors whose alias appears as a whole word/phrase in the question.

    Plain substring/word-boundary match on normalized text - no embeddings
    involved, so a known entity is never missed due to embedding noise."""

    normalized_question = normalize_text(question)

    matches = []

    for anchor in anchors:
        for alias in anchor["aliases"]:

            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

            if re.search(pattern, normalized_question):
                matches.append(anchor)
                break

    return matches


# ==========================================
# Category / domain vocabulary (topic-level signal, no chunk pointer)
# ==========================================

# A couple of category/service labels are themselves generic connector
# words once tokenized out of context (e.g. "بعد" from "خدمة ما بعد
# البيع") and carry no domain-specific meaning on their own - drop them so
# they don't turn into false-positive domain signals.
_CATEGORY_VOCAB_DENYLIST = {"بعد"}

# The knowledge base only ever writes these in plural/compound form
# ("أجهزة", never "جهاز"), so a customer using the singular would otherwise
# get no domain match at all. Extend this only when another such gap is
# found in practice - it is not meant to grow into a general synonym list.
# "لاب" (colloquial short for "لابتوب") was added after "رشحلي لاب
# للبرمجة" measured at 0.698 semantic similarity - just under the 0.70
# supportive threshold, with zero keyword overlap - a real, observed gap,
# not a speculative one.
_CATEGORY_VOCAB_EXTRA_SYNONYMS = {"جهاز", "لابتوب", "لاب"}


def build_category_vocabulary() -> set[str]:
    """Domain vocabulary derived from the knowledge base's own category and
    service labels (categories.json, services.json's category_ar, and
    company_info.json's industry_ar) - not a hardcoded topic list. Only
    short, clean label fields are used (not full free-text names/
    descriptions), since tokenizing full sentences pulls in generic
    connector words with no topical specificity of their own."""

    vocabulary: set[str] = set()

    for category in load_categories():
        vocabulary.update(tokenize(category["name_ar"]))
        vocabulary.update(tokenize(category["name_en"]))

    service_categories = {service["category_ar"] for service in load_services()}

    for category_ar in service_categories:
        vocabulary.update(tokenize(category_ar))

    vocabulary.update(tokenize(load_company_info()["industry_ar"]))

    vocabulary -= _CATEGORY_VOCAB_DENYLIST
    vocabulary |= _CATEGORY_VOCAB_EXTRA_SYNONYMS

    return vocabulary


def is_company_domain_query(question: str, vocabulary: set[str]) -> bool:
    """True if the question shares at least one token with the domain
    vocabulary - a cheap, deterministic "is this about us at all" check,
    independent of chunk-level retrieval confidence."""

    return bool(set(tokenize(question)) & vocabulary)
