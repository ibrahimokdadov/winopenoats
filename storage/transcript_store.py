from PySide6.QtCore import QObject, Signal
from models.models import Utterance, ConversationState


class TranscriptStore(QObject):
    utterance_added = Signal(object)       # Utterance
    partial_updated = Signal(str, str)     # (speaker, text)
    state_updated = Signal(object)         # ConversationState

    def __init__(self, parent=None):
        super().__init__(parent)
        self.utterances: list[Utterance] = []
        self.conversation_state = ConversationState()
        self._them_since_update = 0

    def append(self, utterance: Utterance) -> None:
        self.utterances.append(utterance)
        if utterance.speaker == "them":
            self._them_since_update += 1
        self.utterance_added.emit(utterance)

    def update_partial(self, speaker: str, text: str) -> None:
        self.partial_updated.emit(speaker, text)

    def update_state(self, state: ConversationState) -> None:
        self.conversation_state = state
        self._them_since_update = 0
        self.state_updated.emit(state)

    def clear(self) -> None:
        self.utterances = []
        self.conversation_state = ConversationState()
        self._them_since_update = 0

    @property
    def recent_utterances(self) -> list[Utterance]:
        return self.utterances[-10:]

    @property
    def should_update_state(self) -> bool:
        return self._them_since_update >= 2
