# FAQ (Frequently Asked Questions)

---

### Does it work completely offline?
**Yes.** The speech recognition (`whisper.cpp`), local translators (Ollama), and local TTS providers (`pyttsx3` and `piper`) run 100% locally on your machine. No data is sent over the internet. The only online provider is `edge-tts` (which is optional and can be toggled to `piper` or `pyttsx3` inside `config.yaml`).

---

### What are the hardware requirements?
The system is optimized to run on standard modern laptops without dedicated GPUs:
* **CPU**: Core i5/i7 (Haswell architecture or newer) supporting AVX/AVX2 instructions.
* **RAM**: 8 GB minimum (16 GB recommended to run Ollama and transcription simultaneously).
* **Storage**: 1-2 GB of free space for Whisper models and libraries.

---

### Can I run a custom LLM translation model?
**Yes.** Simply pull the model using Ollama (`ollama pull your-model-name`) and set it inside `config.yaml` under `llm.model` or pass it as a parameter:
```bash
azvt "video.mp4" --model your-model-name
```

---

### What video formats are supported?
Since audio extraction runs through `ffmpeg`, almost all standard media formats are supported, including `.mp4`, `.mkv`, `.avi`, `.mov`, and `.webm`.

---

### How do I change the speech synthesis voice?
Open `config.yaml` and edit the `tts.voice` setting to any valid Edge-TTS voice (such as `ar-SA-HamedNeural` or `ar-EG-SalmaNeural`). You can also override this on the command line:
```bash
azvt "video.mp4" --dub --voice ar-SA-ZariyahNeural
```
