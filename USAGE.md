# Usage Guide - AlZeini Smart Video Translator

The AlZeini Smart Video Translator can be run globally via the command line utility `azvt` or imported programmatically into other Python applications.

---

## 🚀 Command Line Usage (CLI)

The general syntax to run the translator is:
```bash
azvt "<path_to_video>" [options]
```

### Options and Flags
* `--dub`: Enables Text-to-Speech synthesis and multiplexes the Arabic voiceover onto the video.
* `--voice <voice_name>`: Overrides the default TTS voice. Examples:
  * `ar-EG-SalmaNeural` (Default, Egyptian Female)
  * `ar-SA-HamedNeural` (Saudi Male)
  * `ar-SA-ZariyahNeural` (Saudi Female)
* `--model <model_name>`: Overrides the default Ollama translation model (e.g. `--model qwen2.5-coder:7b`).
* `--no-translate`: Disables translation. Outputs raw English SRT subtitles only.
* `--output-dir <path>`: Specifies a custom directory to write output files.

### Examples

#### 1. Generate Subtitles (Bilingual Arabic + English)
Extracts audio, transcribes speech, and translates it, saving subtitles next to the video:
```bash
azvt "/home/user/Videos/lesson.mp4"
```

#### 2. Dub Video (Voiceover Mode)
Generates subtitles and mixes the Arabic voiceover track over the video, ducking the original background audio to 20%:
```bash
azvt "/home/user/Videos/lesson.mp4" --dub
```

#### 3. Full Dubbing (Saudi Male Voice)
Excludes the original audio track completely, replacing it with the Arabic Hamed voiceover:
*(Ensure `mode: "full_dub"` is set in `config.yaml` or run with custom parameters).*
```bash
azvt "/home/user/Videos/lesson.mp4" --dub --voice ar-SA-HamedNeural
```

---

## ⚙️ Global Configuration (`config.yaml`)

Manage default behaviors in **[config.yaml](file:///home/mohamed-al-zeini/Documents/AI-Projects/AlZeini_Smart_Video_Translator/config.yaml)**:
```yaml
whisper:
  dir: "whisper.cpp"
  model: "ggml-small.bin"  # Set defaults: ggml-tiny.bin, ggml-base.bin, ggml-small.bin

llm:
  correct: true
  host: "localhost"
  port: 11434
  model: "gemma3:4b"

tts:
  provider: "edge-tts"      # Options: edge-tts (cloud neural) or pyttsx3 (local offline)
  voice: "ar-EG-SalmaNeural"
  mode: "voice_over"        # Options: subtitles_only, voice_over, full_dub
  bg_volume: 0.20           # Original video audio volume ducking ratio (20% volume)
```

---

## 🛠️ Programmatic Python Integration (Developer Guide)

Because the project utilizes **Dependency Injection** and an **Event Callback System**, you can easily integrate it into GUI scripts, web servers, or workers.

```python
from alzeini_video_translator import VideoTranslationPipeline
from alzeini_video_translator.stt.whispercpp import VideoTranscriber
from alzeini_video_translator.translation.gemma import OllamaSRTTranslator
from alzeini_video_translator.tts.voiceover import VideoDubber

# 1. Instantiate engine dependencies
stt = VideoTranscriber(model_name="ggml-small.bin")
translator = OllamaSRTTranslator(model_name="gemma3:4b")
tts = VideoDubber() # loads configuration parameters

# 2. Setup pipeline and inject dependencies
pipeline = VideoTranslationPipeline(
    input_video="tutorial.mp4",
    stt=stt,
    translator=translator,
    tts=tts
)

# 3. Register callback listeners
def on_progress_handler(percent, message):
    print(f"🔄 Progress: {percent}% - {message}")

pipeline.register_listener("on_progress", on_progress_handler)

# 4. Execute pipeline
results = pipeline.run(dub=True)
print("Finished. Dubbed video saved at:", results["dubbed_video"])
```
