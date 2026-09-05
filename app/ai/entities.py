"""Deterministic entity anchoring for retrieval.

Semantic/keyword search is probabilistic: a question that clearly names a
known entity (today: a branch or its city) can still lose to an unrelated
chunk that happens to score higher by embedding noise. For the small, fixed
set of entities we already know about from the knowledge base, we don't need
to guess - a plain text match is exact and free (no API call).

This module only builds anchors for branches for now. To extend it to
another entity type later (e.g. products), add a `build_x_anchors()`
function following the same shape (list of {"type", "label", "chunk_index",
"aliases"} dicts, matched against the exact chunk text the renderer in
knowledge_base.py produces) and merge it into rag.py's anchor list - nothing
in `find_anchor_matches` is branch-specific.
"""

import re

from app.ai.knowledge_base import load_branches, render_branch
from app.ai.normalize import normalize_text


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
