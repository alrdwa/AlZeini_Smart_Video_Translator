# Installation Guide - AlZeini Smart Video Translator

This document provides a step-by-step setup guide to install and verify the AlZeini Smart Video Translator on Ubuntu.

---

## 📋 Prerequisites

Ensure your system has the required compilers, libraries, and utilities installed.

### 1. System Packages
Install `ffmpeg` (for audio extraction/ducking) and standard C++ compilers (for Whisper.cpp compilation):
```bash
sudo apt update
sudo apt install -y ffmpeg cmake build-essential
```

### 2. Ollama (For Local Translation)
Install Ollama locally to run AI translations and model weights offline:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Start the Ollama server and pull the default translation model:
```bash
ollama pull gemma3:4b
```

---

## ⚙️ Installation Steps

Follow these steps to compile the speech engine and register the package globally:

### Step 1: Clone and Set Up the Repository
```bash
cd "/home/mohamed-al-zeini/Documents/AI-Projects/AlZeini_Smart_Video_Translator"
```

### Step 2: Compile Whisper.cpp & Download Weights
Run the compilation setup script. This clones the C++ Whisper source code, builds the optimized main executable utilizing CPU AVX instruction sets, and downloads the `small` model weight file (~466MB) into your centralized `models/` directory:
```bash
python3 setup_whisper.py --model small
```

### Step 3: Install Package Bindings
Install the package in editable mode via pip to link the global CLI executable `azvt` directly in your environment:
```bash
pip install -e .
```

---

## 🔍 Verification

Verify that the installation was successful by running the test suite:
```bash
python3 -m unittest discover -s tests
```
If you see `OK`, the modular contracts, dependency injection, and event callback systems are fully functional.

To check if the global command line utility is mapped correctly, run:
```bash
azvt --help
```
