# AlZeini Smart Video Translator (v1.0 CLI Engine)

> AI-Powered Local Video Transcription, AI Translation & Dubbing Platform

**AlZeini Smart Video Translator** is a modular, local-first video transcription, translation, and voiceover dubbing engine optimized for Linux (Ubuntu). It:
1. Extracts audio and transcribes spoken English using an optimized C++ implementation of Whisper (`whisper.cpp`) running on CPU cores.
2. Translates transcripts into natural Arabic using local LLMs (Gemma / Qwen) via Ollama.
3. Synthesizes a high-quality Arabic voiceover (TTS), automatically fits speech durations to subtitle bounds, and merges the new track onto the video with background music ducking.

---

## 🌟 Key Features

* **Dependency Injection Architecture**: Decoupled interface wrappers (`BaseSTT`, `BaseTranslator`, `BaseTTS`) allow hot-swapping processing engines at runtime.
* **Callback Event System**: Subscribable event hooks (`on_start`, `on_progress`, `on_finish`, `on_error`) emit real-time processing percentages and messages, making GUI integrations simple.
* **Structured Output Folder**: Automatically groups outputs under `output/<video_name>/` (`audio/`, `subtitle/`, `translation/`, `voice/`).
* **Bilingual Subtitles**: Generates stacked English and Arabic subtitles for language learning.
* **Smart Audio Dubbing (TTS)**: Converts Arabic subtitles into a voiceover track using premium Microsoft Neural TTS voices, automatically adjusting speech speed (`atempo` filter) to fit subtitle timings.
* **Audio Ducking Mix**: Merges the voiceover with the original video's audio, dropping the original track volume to 20% to keep background music/atmosphere clear while keeping the voiceover crisp.
* **File-based Logging**: Dynamic daily logging saved to `logs/YYYY-MM-DD.log`.
* **Metadata Export**: Generates `metadata.json` for every processed video containing duration, processing speed, and models.

---

## 🛠️ Requirements & Installation

1. **System Dependencies**:
   Ensure `ffmpeg` and compiler tools are installed:
   ```bash
   sudo apt update
   sudo apt install -y ffmpeg cmake build-essential
   ```

2. **Project Setup**:
   Clones, compiles `whisper.cpp` binaries, and downloads the `small` GGML Whisper model weights (~466MB):
   ```bash
   python3 setup_whisper.py --model small
   ```

3. **Install Package**:
   Install the library in editable/local mode:
   ```bash
   pip install -e .
   ```
   *This registers the global command line command `azvt` in your environment.*

---

## 🚀 Quick Start

Once installed via pip, you can call the engine globally from any directory:

### 1. Transcribe & Translate (English & Arabic Subtitles)
```bash
azvt "/path/to/video.mp4"
```

### 2. Transcribe, Translate & Dub (Arabic Voiceover Video Output)
Generate Arabic subtitles and dub them directly onto the video:
```bash
azvt "/path/to/video.mp4" --dub
```

### 3. Specify Target Voice & Custom LLM
```bash
azvt "/path/to/video.mp4" --dub --voice ar-SA-HamedNeural --model qwen2.5-coder:7b
```

### Command Flags:
* `--dub`: Enables Arabic voiceover synthesis and video multiplexing.
* `--voice`: Specify a target Edge-TTS voice (default: `ar-EG-SalmaNeural`, alternatives: `ar-SA-HamedNeural`, `ar-SA-ZariyahNeural`).
* `--model`: Specify a custom Ollama model.
* `--no-translate`: Transcribe only (English subtitles only).
* `--output-dir`: Target output directory.

---

## ⚙️ Configuration

Options can be customized in **[config.yaml](file:///home/mohamed-al-zeini/Documents/AI-Projects/AlZeini_Smart_Video_Translator/config.yaml)**.
