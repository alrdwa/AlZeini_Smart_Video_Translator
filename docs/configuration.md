# Configuration

Configuration parameters are declared inside **`config.yaml`** at the project root. This file centralizes default engine selections, models, ports, and audio mixing parameters.

---

## ⚙️ Configuration Properties

Here is a breakdown of the standard `config.yaml` file properties:

```yaml
whisper:
  dir: "whisper.cpp"               # Subfolder containingcompiled whisper.cpp binaries
  model: "ggml-small.bin"          # Name of the model weights file under models/whisper/

llm:
  correct: true                   # Enables translation stage
  host: "localhost"               # Local Ollama address
  port: 11434                     # Ollama server port
  model: "gemma3:4b"              # LLM model tag
  temperature: 0.1                # Keep low for translation accuracy

translation:
  batch_size: 20                  # Subtitle lines processed in a single context prompt

tts:
  provider: "edge-tts"             # Options: 'edge-tts' (Cloud) or 'pyttsx3' (Local offline)
  voice: "ar-EG-SalmaNeural"       # Default speech voice
  mode: "voice_over"               # Options: 'subtitles_only', 'voice_over', 'full_dub'
  bg_volume: 0.20                  # Ducks background audio to 20% in voice_over mode
```

---

## 🎛️ Audio Mixing Modes

The translator supports three distinct audio multiplexing modes under the `tts` configuration header:

### 1. Subtitles Only (`subtitles_only`)
Generates English and Arabic SRT subtitle files but does not perform speech synthesis, copy-pasting the original video track as-is. Useful for users who want translations without vocal overrides.

### 2. Voice Over (`voice_over`)
Lowers the volume of the original audio track to a specified percentage (e.g. `bg_volume: 0.20` ducks it to 20%) and overlays the newly synthesized Arabic voice track. Excellent for classes and software tutorials, keeping background details and system sounds audible.

### 3. Full Dub (`full_dub`)
Strip the original audio track completely, replacing it with the synthesized Arabic voice track. Recommended for maximum clarity during monologue lectures or when background vocals interfere with translations.
