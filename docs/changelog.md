# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0-beta] - 2026-07-11

This major beta release restructures the codebase into a modular, production-ready library package (`alzeini_video_translator`), preparing the platform for plugin and API development.

### Added
- **Dependency Injection**: Injected decoupled instances of STT, Translation, and TTS engines into the central pipeline constructor.
- **Base Interfaces**: Added abstract contract classes (`BaseSTT`, `BaseTranslator`, `BaseTTS`) under each respective namespace directory.
- **Event Callbacks**: Implemented subscribable callback hooks (`on_start`, `on_progress`, `on_finish`, `on_error`) that emit progress percentages and status messages.
- **Multiple Dubbing Modes**: Introduced `subtitles_only`, `voice_over` (ducking background volume to 20%), and `full_dub` (replacing the original audio track completely).
- **TTS Providers**: Added `PyTTSX3Provider` (local offline espeak fallback) and `PiperTTSProvider` (local offline neural ONNX voice skeleton) in addition to `EdgeTTSProvider`.
- **Project Metadata Exporter**: Automatically generates `metadata.json` under each video output folder containing processing speeds, durations, and model footprints.
- **Centralized Directories**: Set up centralized root directories for models (`models/whisper/`, `models/piper/`) and daily run logs (`logs/YYYY-MM-DD.log`).
- **Structured Output Layout**: Cleaned root folder by placing outputs in structured directories (`output/<video_name>/{audio,subtitle,translation,voice}`).
- **PIP Package Mapping**: Created `pyproject.toml` registering the package and the global CLI execution script command **`azvt`**.
- **Automated Tests**: Created unit test suite `tests/test_pipeline.py` verifying callbacks and Dependency Injection.

### Changed
- Refactored files out of the flat layout into modular folders.
- Upgraded the default Whisper model from `ggml-base.bin` to the high-accuracy `ggml-small.bin` (~466MB).

---

## [0.1.0-beta] - 2026-07-11

Initial prototype release establishing local speech-to-text transcription and translation capabilities.

### Added
- ffmpeg WAV audio extractor.
- Whisper.cpp compilation CLI wrapper downloading base weights.
- Ollama context-aware subtitle translation batch script.
- Basic audio voiceover script mixing Edge-TTS voice files over background.
