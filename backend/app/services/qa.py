"""
qa.py

The core question-answering pipeline (spec section 6):

    Question
      -> retrieve relevant chunks (app/services/retrieval.py)
      -> relevance threshold (Anti-Hallucination Layer 1)
           -> nothing relevant enough? -> "not enough information", no LLM call
      -> build grounded context from the relevant chunks
      -> LLM answers using ONLY that context (Layer 2's strict system prompt)
      -> return answer + sources

Deliberately NOT implemented here: Phase 6's Layer 3 (checking the
generated answer is actually supported by the context before returning
it). This phase relies on retrieval filtering (Layer 1) plus the LLM
following strict grounding instructions (Layer 2) — which, per the
threshold-calibration note in app/config.py, isn't foolproof on its own
for a lexical embedding provider. That gap is exactly what Phase 6 closes.
"""

import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.services.llm import get_llm_provider
from app.services.retrieval import search

NOT_ENOUGH_INFO = "The provided data does not contain sufficient information to answer this question."

# Spec section 7, Layer 2 — the strict grounding instructions, verbatim
# in spirit. Every word here is doing a job: "ONLY" and "Do not use
# general knowledge" rule out the model falling back on its training
# data; "Do not infer missing facts" rules out plausible-sounding
# extrapolation from a topically-related-but-not-answering chunk (exactly
# the "Rahul's CGPA" vs "Rahul's father's name" trap noted in config.py).
SYSTEM_PROMPT_TEMPLATE = """You are a data-grounded question answering system.

You may ONLY use the information contained in the provided CONTEXT.

Do not use general knowledge.
Do not infer missing facts.
Do not invent facts.
Do not guess.

If the answer is not supported by the CONTEXT, respond with EXACTLY this sentence and nothing else:
"{not_enough_info}"

Every factual claim in your answer must be directly supported by the provided context.{style_instruction}"""

STYLE_INSTRUCTIONS = {
    "short": "\n\nKeep your answer to one sentence.",
    "detailed": "",
    "bullet_points": "\n\nFormat your answer as bullet points.",
    "simple": "\n\nExplain your answer simply, as if to someone new to the topic.",
}


def _build_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into the CONTEXT block the LLM sees, each
    one labeled with its source so the model (and, if you read the raw
    prompt, a human) can tell which chunk is which.
    """
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        location = ""
        if chunk["page_number"] is not None:
            location = f", page {chunk['page_number']}"
        elif chunk["row_number"] is not None:
            location = f", row {chunk['row_number']}"
        parts.append(f"[Source {i}: {chunk['filename']}{location}]\n{chunk['text']}")
    return "\n\n".join(parts)


def answer_question(
    db: Session,
    user_id: uuid.UUID,
    question: str,
    document_id: uuid.UUID | None = None,
    collection_id: uuid.UUID | None = None,
    answer_style: str = "detailed",
) -> dict:
    """
    Runs the full grounded QA pipeline and returns:
        {"answer": str, "supported": bool, "sources": list[dict]}

    `supported` is False only for the "not enough information" case
    (Layer 1 filtered out everything). Once the LLM does respond, we
    trust its own judgment about whether it could answer — Phase 6 adds
    an independent check on top rather than replacing this.
    """
    chunks = search(db, user_id=user_id, query=question, top_k=settings.TOP_K, document_id=document_id, collection_id=collection_id)

    # Anti-Hallucination Layer 1: if nothing retrieved clears the
    # relevance bar, don't even ask the LLM — there's nothing for it to
    # ground an answer in.
    relevant_chunks = [c for c in chunks if c["similarity"] >= settings.SIMILARITY_THRESHOLD]
    if not relevant_chunks:
        return {"answer": NOT_ENOUGH_INFO, "supported": False, "sources": []}

    context = _build_context(relevant_chunks)
    style_instruction = STYLE_INSTRUCTIONS.get(answer_style, "")
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(not_enough_info=NOT_ENOUGH_INFO, style_instruction=style_instruction)
    user_message = f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"

    provider = get_llm_provider()
    answer_text = provider.generate(system_prompt, user_message)

    # The model was instructed to reply with exactly this sentence when
    # it can't answer — detect that and report supported=False with no
    # sources, rather than citing chunks that didn't actually help.
    if answer_text.strip().strip('"') == NOT_ENOUGH_INFO:
        return {"answer": NOT_ENOUGH_INFO, "supported": False, "sources": []}

    sources = [
        {
            "document_id": c["document_id"],
            "filename": c["filename"],
            "page_number": c["page_number"],
            "row_number": c["row_number"],
            "text": c["text"],
        }
        for c in relevant_chunks
    ]
    return {"answer": answer_text, "supported": True, "sources": sources}
