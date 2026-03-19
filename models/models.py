from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Literal


@dataclass
class Utterance:
    speaker: Literal["you", "them"]
    text: str
    timestamp: datetime
    id: UUID = field(default_factory=uuid4)


@dataclass
class ConversationState:
    topic: str = ""
    summary: str = ""
    open_questions: list[str] = field(default_factory=list)
    tensions: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)


@dataclass
class SuggestionTrigger:
    kind: Literal["explicit_question", "decision_point", "disagreement", "assumption", "domain"]
    confidence: float


@dataclass
class SuggestionEvidence:
    text: str
    source_file: str
    header_context: str
    relevance_score: float


@dataclass
class SuggestionDecision:
    relevance: float
    helpfulness: float
    novelty: float
    timing: float
    surfaced: bool


@dataclass
class Suggestion:
    headline: str
    coaching: str
    text: str
    trigger: SuggestionTrigger
    evidence: list[SuggestionEvidence]
    decision: SuggestionDecision
    feedback: Literal["positive", "negative"] | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class SessionIndex:
    id: UUID
    timestamp: datetime
    utterance_count: int
    title: str


@dataclass
class MeetingTemplate:
    name: str
    system_prompt: str
    id: UUID = field(default_factory=uuid4)
