# Model Benchmarks

Below are local benchmarks measured on typical development hardware (such as an Intel Core i5/i7 mobile CPU with 8-16GB RAM) running completely offline.

---

## 🎙️ Speech Recognition (Whisper GGML Models)

Processing speeds are relative to the video duration (e.g. `0.2x` means 10 minutes of video is processed in 2 minutes).

| Model Size | Accuracy | File Size | Speed (CPU) | RAM Footprint | Recommended Use Case |
|------------|----------|-----------|-------------|---------------|----------------------|
| **tiny** | Low | ~75 MB | ~0.05x | ~200 MB | Quick testing and fast checks. |
| **base** | Moderate | ~140 MB | ~0.10x | ~400 MB | Standard conversations, clear audio. |
| **small** (Default) | High | ~466 MB | ~0.25x | ~1.0 GB | Technical videos, programming lectures. |
| **medium** | Very High | ~1.5 GB | ~0.80x | ~3.0 GB | Multi-speaker dialog, poor audio conditions. |
| **large-v3** | Outstanding | ~2.9 GB | >1.5x | ~6.0 GB | Heavy GPU setups only. |

---

## 🧠 LLM Translation Models (Local Ollama)

| Model Name | Parameter Size | VRAM / RAM | Processing Speed | Context Window | Accuracy |
|------------|----------------|------------|------------------|----------------|----------|
| **gemma3:4b** | 4 Billion | ~3.2 GB | ~35 tokens/sec | 8k tokens | High |
| **qwen2.5-coder:7b** | 7 Billion | ~5.8 GB | ~18 tokens/sec | 32k tokens | Very High (Contextual) |

---

## 🔊 Speech Synthesis (TTS Engines)

| Engine | Type | Audio Quality | Speed (CPU) | Offline Status | Notes |
|--------|------|---------------|-------------|----------------|-------|
| **Edge-TTS** | Cloud API | Premium (Neural) | Real-time | Online | Requires internet connection. |
| **Piper TTS** | Neural ONNX | High (Natural) | Real-time | 100% Offline | High quality on CPU. |
| **pyttsx3** | espeak-ng | Moderate (Robotic) | Real-time | 100% Offline | Built-in fallback option. |
