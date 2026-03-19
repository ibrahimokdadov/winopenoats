import json
import os
import pytest
from pathlib import Path
from app.settings import AppSettings


@pytest.fixture
def tmp_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    return AppSettings()


def test_defaults(tmp_settings):
    s = tmp_settings
    assert s.llm_provider == "openrouter"
    assert s.transcription_model == "small.en"
    assert s.recording_consent_acknowledged is False


def test_save_and_reload(tmp_settings, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    tmp_settings.llm_model = "openai/gpt-4o"
    tmp_settings.save()
    s2 = AppSettings()
    assert s2.llm_model == "openai/gpt-4o"


def test_model_dir(tmp_settings, tmp_path):
    assert "OpenOats" in str(tmp_settings.model_dir)
    assert tmp_settings.model_dir.exists()


def test_session_dir(tmp_settings, tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert tmp_settings.session_dir.exists()
    assert "OpenOats" in str(tmp_settings.session_dir)
