# Installation

Follow these steps to compile the C++ speech recognition libraries and register the global execution script in your environment.

---

## 🛠️ Prerequisites

Make sure your machine runs Ubuntu (or another Linux distribution) and has the standard compilation toolchains installed.

### 1. Build Utilities & ffmpeg
Install compilation compilers and audio manipulation libraries:
```bash
sudo apt update
sudo apt install -y ffmpeg cmake build-essential
```

### 2. Local Ollama Server
Download and start Ollama on your system:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Start the Ollama daemon and pull the default Gemma model:
```bash
ollama pull gemma3:4b
```

---

## 💻 Package Setup

### 1. Navigate to Project Root
```bash
cd "/home/mohamed-al-zeini/Documents/AI-Projects/AlZeini_Smart_Video_Translator"
```

### 2. Compile Whisper.cpp
Run the compilation helper. This clones the C++ repository, compiles binary code optimized for your CPU (AVX instruction sets), and downloads the `small` model weight file (~466MB) directly to the root `models/whisper/` folder:
```bash
python3 setup_whisper.py --model small
```

### 3. Install Package Globally
Install the package in local/editable mode. This registers the executable command **`azvt`** globally:
```bash
pip install -e .
```

---

## 🧪 Verify Installation
Verify that the components are registered correctly by running unit tests:
```bash
python3 -m unittest discover -s tests
```
If the tests print `OK`, the contracts are functional.
