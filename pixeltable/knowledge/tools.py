"""Knowledge-substrate @pxt.query tools (Amendment 07).

Pre-flight query layer enforced by `.claude/rules/anti-amnesia.md`. Every
SKILL.md write, every migration that adds an external service, every plan
doc, every architectural decision, and every implementation code path must
first call one of these tools and accept results above the 0.7 similarity
threshold.

Below-threshold results = knowledge gap = run the harvest pipeline before
writing.

NOTE: This file MUST NOT import the Anthropic SDK. Forbidden by cardinal
rule (cf. AGENTS.md). The tools below talk to Pixeltable only; any LLM
synthesis happens in the agent layer that consumes these tools.
"""
from __future__ import annotations

import pixeltable as pxt


# ---------- Amendment 07 tools (tutorials + research + skills) ----------

@pxt.query
def search_tutorials(query_text: str, tool_name: str | None = None):
    """Semantic search across video tutorial transcriptions.

    Pre-flight call BEFORE writing any SKILL.md or implementation code for
    a tool that has tutorial coverage in lattice/knowledge/tutorials.

    Returns the top-K matching sentences with: source_url, title, channel,
    similarity score. Caller filters by tool_name if known.
    """
    sentences = pxt.get_table("lattice/knowledge/tutorial_sentences")
    sim = sentences.text.similarity(query_text)
    q = sentences.select(
        text=sentences.text,
        source_url=sentences.source_url,
        title=sentences.title,
        channel=sentences.channel,
        tool_name=sentences.tool_name,
        similarity=sim,
    ).order_by(sim, asc=False)
    if tool_name is not None:
        q = q.where(sentences.tool_name == tool_name)
    return q.limit(10)


@pxt.query
def search_research(query_text: str, tool_name: str | None = None):
    """Semantic search across research-doc chunks.

    Pre-flight call BEFORE writing any plan, architectural decision doc,
    or migration that touches an external surface covered by
    lattice/knowledge/research_chunks.
    """
    chunks = pxt.get_table("lattice/knowledge/research_chunks")
    sim = chunks.text.similarity(query_text)
    q = chunks.select(
        text=chunks.text,
        source_path=chunks.source_path,
        doc_type=chunks.doc_type,
        tool_name=chunks.tool_name,
        similarity=sim,
    ).order_by(sim, asc=False)
    if tool_name is not None:
        q = q.where(chunks.tool_name == tool_name)
    return q.limit(10)


@pxt.query
def get_skill_for_tool(tool_name: str):
    """Return any registered SKILL.md content for a tool name.

    Use this BEFORE writing a new SKILL.md for an external tool — there
    may already be a generated one from the harvest pipeline.
    """
    skills = pxt.get_table("lattice/knowledge/skills_registry")
    return skills.select(
        skill_name=skills.skill_name,
        tool_name=skills.tool_name,
        skill_content=skills.skill_content,
        committed_path=skills.committed_path,
        generated_at=skills.generated_at,
    ).where(skills.tool_name == tool_name).order_by(skills.generated_at, asc=False).limit(5)
