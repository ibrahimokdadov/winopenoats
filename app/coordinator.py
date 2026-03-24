import asyncio
import logging
from PySide6.QtCore import QObject, Signal
from app.settings import AppSettings
from audio.mic_capture import MicCapture
from audio.system_capture import SystemCapture
from transcription.engine import TranscriptionEngine
from intelligence.suggestion_engine import SuggestionEngine
from intelligence.notes_engine import NotesEngine
from intelligence.knowledge_base import KnowledgeBase
from storage.session_store import SessionStore
from storage.transcript_store import TranscriptStore
from models.models import Utterance, Suggestion, SessionIndex

logger = logging.getLogger(__name__)


class AppCoordinator(QObject):
    session_started = Signal()
    session_ended = Signal(object)           # SessionIndex
    system_audio_unavailable = Signal()
    toast_requested = Signal(str, str)       # (message, level)
    suggestion_ready = Signal(object)        # Suggestion
    notes_chunk_ready = Signal(str)          # notes text chunk

    def __init__(self, settings: AppSettings = None, parent=None):
        super().__init__(parent)
        self.settings = settings or AppSettings()
        self._loop = asyncio.get_event_loop()

        self.transcript_store = TranscriptStore()
        self._mic = MicCapture(self._loop, device=self.settings.input_device)
        self._sys = SystemCapture(self._loop)
        self._engine: TranscriptionEngine | None = None
        self._session_store: SessionStore | None = None
        self._engine_task: asyncio.Task | None = None

        self.kb = self._build_kb()
        self.suggestion_engine: SuggestionEngine | None = None
        self.notes_engine: NotesEngine | None = None

    def _build_kb(self) -> KnowledgeBase | None:
        if not self.settings.kb_folder:
            return None
        from pathlib import Path
        embed_fn = self._get_embed_fn()
        if not embed_fn:
            return None
        return KnowledgeBase(folder=Path(self.settings.kb_folder), embed_fn=embed_fn)

    def _get_embed_fn(self):
        provider = self.settings.embedding_provider
        if provider == "voyage":
            key = self.settings.get_secret("voyage_api_key") or ""
            if not key:
                return None
            from intelligence.clients.voyage import VoyageClient
            client = VoyageClient(api_key=key, model=self.settings.embedding_model)
            return client.embed
        elif provider == "ollama":
            from intelligence.clients.ollama import OllamaClient
            client = OllamaClient(
                self.settings.ollama_base_url,
                self.settings.ollama_llm_model,
                self.settings.ollama_embedding_model,
            )
            return client.embed
        return None

    def _get_llm_fn(self):
        provider = self.settings.llm_provider
        if provider == "openrouter":
            key = self.settings.get_secret("openrouter_api_key") or ""
            if not key:
                return None
            from intelligence.clients.openrouter import OpenRouterClient
            client = OpenRouterClient(api_key=key, model=self.settings.llm_model)
            return client.complete
        elif provider == "ollama":
            from intelligence.clients.ollama import OllamaClient
            client = OllamaClient(
                self.settings.ollama_base_url,
                self.settings.ollama_llm_model,
                self.settings.ollama_embedding_model,
            )
            return client.complete
        return None

    async def start_session(self) -> None:
        self.transcript_store.clear()

        self._session_store = SessionStore(
            session_dir=self.settings.session_dir,
            notes_dir=self.settings.notes_dir,
        )

        self.toast_requested.emit("Loading transcription model…", "info")
        self._engine = await asyncio.to_thread(
            TranscriptionEngine,
            model_dir=self.settings.model_dir,
            model_size=self.settings.transcription_model,
        )

        self._mic.start()
        if not self._mic.available:
            self.toast_requested.emit(
                "Microphone access denied — check Windows Privacy Settings > Microphone", "error"
            )
            return

        self._sys.start()
        if not self._sys.available:
            self.system_audio_unavailable.emit()
        self._engine.on_utterance = self._on_utterance
        self._engine.on_partial = self.transcript_store.update_partial

        llm_fn = self._get_llm_fn()
        if self.kb and llm_fn:
            self.suggestion_engine = SuggestionEngine(
                kb=self.kb,
                llm_complete=llm_fn,
                on_suggestion=self._on_suggestion,
            )
        self.notes_engine = NotesEngine(
            llm_complete=llm_fn,
            system_prompt="Summarize this meeting as structured notes.",
        )

        self._engine_task = asyncio.create_task(
            self._engine.start(self._mic.stream(), self._sys.stream())
        )
        self.session_started.emit()

    async def end_session(self) -> None:
        if self._engine_task:
            self._engine_task.cancel()
            try:
                await self._engine_task
            except asyncio.CancelledError:
                pass

        self._mic.stop()
        self._sys.stop()

        if self._session_store:
            topic = self.transcript_store.conversation_state.topic or "Meeting"
            index = self._session_store.finalize(title=topic, template_id=None)
            self.session_ended.emit(index)

        if self.notes_engine:
            asyncio.ensure_future(self._generate_notes())

    async def _generate_notes(self) -> None:
        utterances = list(self.transcript_store.utterances)
        if not utterances:
            return
        try:
            chunk = await self.notes_engine.generate(utterances)
            if chunk:
                self.notes_chunk_ready.emit(chunk)
        except Exception as exc:
            logger.warning("Notes generation failed: %s", exc)

    def _on_utterance(self, utterance: Utterance) -> None:
        self.transcript_store.append(utterance)
        if self._session_store:
            self._session_store.write_utterance(utterance)
        if self.suggestion_engine:
            asyncio.create_task(self.suggestion_engine.on_utterance(utterance))

    def _on_suggestion(self, suggestion: Suggestion) -> None:
        if self._session_store:
            self._session_store.write_suggestion(suggestion)
        self.suggestion_ready.emit(suggestion)

    def record_feedback(self, suggestion_id: str, polarity: str) -> None:
        if self._session_store:
            self._session_store.write_feedback(suggestion_id, polarity)
