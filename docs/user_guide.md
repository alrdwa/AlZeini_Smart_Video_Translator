# User Guide

This guide details how AlZeini Smart Video Translator processes videos, structures its output directories, logs executions, and exposes options.

---

## 🛠️ CLI Flags & Parameter Reference

Call the global executable command `azvt` followed by flags:

| Flag | Argument | Description | Default |
|------|----------|-------------|---------|
| `--dub` | *(None)* | Enables Text-to-Speech voiceover generation and video mixing. | Disabled |
| `--voice` | `str` | Name of the target voice (e.g. `ar-SA-HamedNeural`). | `ar-EG-SalmaNeural` |
| `--model` | `str` | Override Ollama model tag (e.g. `qwen2.5-coder:7b`). | `gemma3:4b` |
| `--no-translate` | *(None)*| Skips translation, saving raw English subtitles only. | Disabled |
| `--output-dir` | `str` | Override path where output folder structure is saved. | Root `output/` |

---

## 📂 Structured Project Outputs

To keep your workspace clean, the pipeline separates generated files inside a dedicated subfolder located under the root **`output/`** directory.

For a video named `lesson01.mp4`, the structure is:

```text
output/
└── lesson01/
    ├── audio/
    │   └── lesson01_temp.wav        # Temporary extracted WAV (deleted after transcription)
    ├── subtitle/
    │   └── lesson01_EN.srt          # Extracted English subtitles
    ├── translation/
    │   └── lesson01_AR.srt          # Translated Arabic subtitles
    ├── voice/
    │   └── lesson01_dubbed.mp4      # Final dubbed video output
    └── metadata.json                # Project report and metrics
```

### Understanding `metadata.json`
Every execution saves a metadata audit log containing details for the session:
```json
{
  "video_name": "lesson01",
  "duration": "180.25 seconds",
  "stt_engine": "VideoTranscriber",
  "translator_engine": "OllamaSRTTranslator",
  "tts_engine": "VideoDubber",
  "processing_time_seconds": 24.52,
  "created_at": "2026-07-11T17:15:30.123456"
}
```

---

## 📝 Daily Logging

The package records system logs, warnings, and durations inside **`logs/`**:
```text
logs/
└── 2026-07-11.log
```
Each entry logs the timestamp, file line, log level (`INFO`, `WARNING`, `ERROR`), and detailed message trace.
