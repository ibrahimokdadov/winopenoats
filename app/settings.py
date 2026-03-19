import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULTS = {
    "llm_provider": "openrouter",
    "llm_model": "openai/gpt-4o-mini",
    "transcription_model": "small.en",
    "embedding_provider": "voyage",
    "embedding_model": "voyage-3-lite",
    "ollama_base_url": "http://localhost:11434",
    "ollama_llm_model": "llama3",
    "ollama_embedding_model": "nomic-embed-text",
    "kb_folder": None,
    "input_device": None,
    "hide_from_screen_capture": False,
    "recording_consent_acknowledged": False,
}


class AppSettings:
    def __init__(self):
        self._config_path = (
            Path(os.environ.get("APPDATA", Path.home())) / "OpenOats" / "settings.json"
        )
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: dict = {}  # plaintext fallback when keyring is unavailable
        data = DEFAULTS.copy()
        if self._config_path.exists():
            try:
                data.update(json.loads(self._config_path.read_text()))
            except (json.JSONDecodeError, OSError):
                pass
        for k, v in data.items():
            setattr(self, k, v)

    def save(self):
        data = {k: getattr(self, k) for k in DEFAULTS}
        self._config_path.write_text(json.dumps(data, indent=2))

    @property
    def model_dir(self) -> Path:
        p = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "OpenOats" / "models"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def session_dir(self) -> Path:
        p = Path.home() / "Documents" / "OpenOats" / "sessions"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def notes_dir(self) -> Path:
        p = Path.home() / "Documents" / "OpenOats" / "notes"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_secret(self, key: str) -> str | None:
        try:
            import keyring
            return keyring.get_password("OpenOats", key)
        except Exception:
            logger.warning(
                "keyring unavailable; secrets stored in plaintext. "
                "Check Windows Credential Manager."
            )
            return self._config.get(f"_secret_{key}")

    def set_secret(self, key: str, value: str) -> None:
        try:
            import keyring
            keyring.set_password("OpenOats", key, value)
        except Exception:
            logger.warning("keyring unavailable; storing secret in plaintext.")
            self._config[f"_secret_{key}"] = value
            self.save()
