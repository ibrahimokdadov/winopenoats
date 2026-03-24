# WinOpenOats

A Windows port of [OpenOats](https://github.com/yazinsai/OpenOats) — a real-time meeting assistant that transcribes conversations, surfaces relevant notes from your knowledge base, and saves session summaries. Runs entirely on your machine.

> Original macOS app by [@yazinsai](https://github.com/yazinsai). This repo reimplements it for Windows using Python + PySide6.

---

## Features

- **Real-time transcription** — mic + system audio captured simultaneously via WASAPI
- **Live suggestions** — searches your local knowledge base and surfaces relevant notes during the call
- **Auto-generated session notes** — summarizes each meeting using an LLM when the session ends
- **Past sessions browser** — view transcripts and notes from previous meetings
- **System tray** — runs quietly in the background, single-click to show/hide
- **Screen share protection** — optionally hides the window from screen capture (Windows `SetWindowDisplayAffinity`)
- **Transcript search** — filter the live transcript in real time
- **Fully local option** — use Ollama for LLM + embeddings, Whisper or Parakeet for transcription (no data leaves your machine)

---

## Transcription Models

| Model | Size | Notes |
|---|---|---|
| Parakeet TDT v2 | ~600 MB | English, fast, NeMo backend |
| Parakeet TDT 1.1B | ~1.1 GB | Multilingual, NeMo backend |
| Whisper Base | ~142 MB | Good for low-resource machines |
| Whisper Small | ~244 MB | Balanced speed/accuracy |
| Whisper Large v3 Turbo | ~800 MB | Best accuracy, recommended |
| Whisper Large v3 | ~1.5 GB | Maximum accuracy |

---

## Requirements

- Windows 10/11
- Python 3.12
- A microphone
- System audio capture via WASAPI (built into Windows)

For **cloud mode**: OpenRouter API key (for LLM) + Voyage AI API key (for embeddings)
For **local mode**: [Ollama](https://ollama.com) running locally with a language model and an embedding model

---

## Installation

```bash
git clone https://github.com/ibrahimokdadov/winopenoats.git
cd winopenoats
pip install -r requirements.txt
python main.py
```

On first launch, the onboarding wizard will walk you through model selection and API key setup.

### Optional: Parakeet (NeMo) support

```bash
pip install nemo_toolkit[asr] --user
```

---

## Usage

1. Click **Record** to start a session — transcription begins immediately
2. Speak normally; the transcript updates in real time
3. Suggestions from your knowledge base appear automatically
4. Click **Stop** — notes are generated and the session is saved
5. Click **Notes** to browse past sessions

---

## Stack

| Component | Technology |
|---|---|
| UI | PySide6 (Qt6) |
| Event loop | qasync |
| Transcription | faster-whisper / NeMo (Parakeet) |
| VAD | Silero VAD |
| Audio capture | sounddevice (mic) + pyaudiowpatch WASAPI (system) |
| LLM / embeddings | OpenRouter or Ollama |
| Secrets | Windows Credential Manager (keyring) |

---

## Legal

You are solely responsible for obtaining consent from all parties before recording any conversation. Recording laws vary by jurisdiction.

---

## Credits

Based on [OpenOats](https://github.com/yazinsai/OpenOats) by [@yazinsai](https://github.com/yazinsai), originally built for macOS in Swift. This project is a ground-up reimplementation for Windows in Python.

Licensed under the [MIT License](LICENSE).
