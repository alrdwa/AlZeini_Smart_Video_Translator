# Quick Start

Get your video transcribing, translating, and dubbing in three simple commands.

---

## 🏃‍♂️ 3-Step Start

Ensure you have completed the [💻 Installation](installation.md) steps, then follow these steps:

### 1. Initialize the Environment
Open a Terminal and navigate to the project directory:
```bash
cd "/home/mohamed-al-zeini/Documents/AI-Projects/AlZeini_Smart_Video_Translator"
```

### 2. Configure Settings (Optional)
Open **[config.yaml](file:///home/mohamed-al-zeini/Documents/AI-Projects/AlZeini_Smart_Video_Translator/config.yaml)** in your editor to verify Ollama tags, default voices, and mixing modes:
```yaml
tts:
  provider: "edge-tts"      # 'edge-tts' (online neural) or 'pyttsx3' (local offline)
  mode: "voice_over"        # 'subtitles_only', 'voice_over', or 'full_dub'
  bg_volume: 0.20           # ducks original audio to 20%
```

### 3. Run the Translation & Dubbing Command
Execute the global command utility `azvt` followed by your video file:
```bash
azvt "/path/to/your/video.mp4" --dub
```

---

## ⚙️ Everyday CLI Examples

### Generate Bilingual Subtitles Only (No Dubbing)
```bash
azvt "lecture.mp4"
```
*Outputs English subtitles (`video_EN.srt`) and Arabic subtitles (`video_AR.srt`) next to each other.*

### Dub Video with a Custom Voice (e.g. Saudi Hamed)
```bash
azvt "lecture.mp4" --dub --voice ar-SA-HamedNeural
```

### Override the Default Translation Model
```bash
azvt "lecture.mp4" --dub --model qwen2.5-coder:7b
```

### Transcribe Only (English Subtitles Only)
```bash
azvt "lecture.mp4" --no-translate
```
