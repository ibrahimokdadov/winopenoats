import asyncio
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Callable
from models.models import (
    Utterance, Suggestion, SuggestionTrigger, SuggestionEvidence,
    SuggestionDecision, ConversationState,
)
from intelligence.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 90
MIN_WORDS = 8
MIN_CHARS = 30
RELEVANCE_THRESHOLD = 0.72

QUESTION_PATTERNS = re.compile(r'\b(what|how|why|when|where|who|which|could you|can you)\b|\?', re.IGNORECASE)
DECISION_PATTERNS = re.compile(r'\b(should we|which option|decide|go with|choose|pick)\b', re.IGNORECASE)
DISAGREEMENT_PATTERNS = re.compile(r'\b(but|however|disagree|not sure|concern|issue)\b', re.IGNORECASE)
ASSUMPTION_PATTERNS = re.compile(r'\b(i think|i assume|what if|maybe|perhaps)\b', re.IGNORECASE)
DOMAIN_PATTERNS = re.compile(r'\b(customer|mvp|pricing|retention|churn|revenue|metric|kpi)\b', re.IGNORECASE)


def detect_trigger(utterance: Utterance) -> SuggestionTrigger | None:
    text = utterance.text
    if QUESTION_PATTERNS.search(text):
        return SuggestionTrigger(kind="explicit_question", confidence=0.9)
    if DECISION_PATTERNS.search(text):
        return SuggestionTrigger(kind="decision_point", confidence=0.85)
    if DISAGREEMENT_PATTERNS.search(text):
        return SuggestionTrigger(kind="disagreement", confidence=0.8)
    if ASSUMPTION_PATTERNS.search(text):
        return SuggestionTrigger(kind="assumption", confidence=0.75)
    if DOMAIN_PATTERNS.search(text):
        return SuggestionTrigger(kind="domain", confidence=0.7)
    return None


def pre_filter(utterance: Utterance, last_suggestion_time: datetime | None) -> bool:
    text = utterance.text.strip()
    if len(text.split()) < MIN_WORDS or len(text) < MIN_CHARS:
        return False
    if last_suggestion_time:
        elapsed = (datetime.now(timezone.utc) - last_suggestion_time).total_seconds()
        if elapsed < COOLDOWN_SECONDS:
            return False
    return True


class SuggestionEngine:
    def __init__(self, kb: KnowledgeBase, llm_complete, on_suggestion: Callable[[Suggestion], None]):
        self._kb = kb
        self._llm = llm_complete
        self._on_suggestion = on_suggestion
        self._state = ConversationState()
        self._last_suggestion: datetime | None = None
        self._recent: list[Utterance] = []

    async def on_utterance(self, utterance: Utterance) -> None:
        self._recent.append(utterance)
        if len(self._recent) > 20:
            self._recent.pop(0)

        trigger = detect_trigger(utterance)
        if not trigger:
            return
        if not pre_filter(utterance, self._last_suggestion):
            return

        try:
            await self._run_pipeline(utterance, trigger)
        except Exception as e:
            logger.warning("Suggestion pipeline error: %s", e)

    async def _run_pipeline(self, utterance: Utterance, trigger: SuggestionTrigger) -> None:
        context = "\n".join(f"{u.speaker}: {u.text}" for u in self._recent[-6:])
        state_prompt = [
            {"role": "system", "content": "Update the conversation state as JSON: {topic, summary, open_questions, tensions, decisions, goals}."},
            {"role": "user", "content": f"Transcript:\n{context}\n\nCurrent state: {json.dumps(self._state.__dict__)}"},
        ]
        try:
            raw = await self._llm(state_prompt)
            new_state = json.loads(raw)
            for k, v in new_state.items():
                if hasattr(self._state, k):
                    setattr(self._state, k, v)
        except (json.JSONDecodeError, Exception):
            pass

        queries = [utterance.text, self._state.topic]
        results = []
        for q in queries:
            if q:
                results.extend(await self._kb.search(q, top_k=5))
        if not results:
            return

        evidence_text = "\n".join(f"[{r.source_file}] {r.text}" for r in results[:3])
        gate_prompt = [
            {"role": "system", "content": (
                "You are a meeting assistant. Given the utterance and evidence, decide whether to surface a suggestion. "
                "Respond as JSON: {relevance, helpfulness, novelty, timing, surfaced, headline, coaching, text}. "
                "All scores 0.0–1.0. Only set surfaced=true if relevance >= 0.72 AND the suggestion is genuinely helpful."
            )},
            {"role": "user", "content": f"Utterance: {utterance.text}\n\nEvidence:\n{evidence_text}"},
        ]
        try:
            raw = await self._llm(gate_prompt)
            data = json.loads(raw)
        except (json.JSONDecodeError, Exception):
            return

        decision = SuggestionDecision(
            relevance=data.get("relevance", 0),
            helpfulness=data.get("helpfulness", 0),
            novelty=data.get("novelty", 0),
            timing=data.get("timing", 0),
            surfaced=data.get("surfaced", False),
        )
        if not decision.surfaced:
            return

        suggestion = Suggestion(
            headline=data.get("headline", ""),
            coaching=data.get("coaching", ""),
            text=data.get("text", ""),
            trigger=trigger,
            evidence=[SuggestionEvidence(r.text, r.source_file, r.header_context, r.relevance_score) for r in results[:3]],
            decision=decision,
        )
        self._last_suggestion = datetime.now(timezone.utc)
        self._on_suggestion(suggestion)
