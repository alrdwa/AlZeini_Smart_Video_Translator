# Contributing to AlZeini Smart Video Translator

We welcome contributions of all kinds! Please take a moment to review this guide before submitting issues or pull requests.

---

## 🛠️ Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/alrdwa/AlZeini_Smart_Video_Translator.git
   cd AlZeini_Smart_Video_Translator
   ```

2. **Set Up Compiler & Models**:
   ```bash
   python3 setup_whisper.py --model small
   ```

3. **Install in Editable Mode**:
   ```bash
   pip install -e .
   ```

---

## 📜 Coding Guidelines

* **Modular Contracts**: If adding a new STT, Translator, or TTS engine, ensure it inherits from the appropriate base interface under `stt/base.py`, `translation/base.py`, or `tts/base.py`.
* **Clean Code**: Keep methods focused and document new capabilities.
* **No Hardcoded Options**: Place configurable options inside `config.yaml` and parse them inside `config.py`.
* **Logging**: Use the standard logger (`logger = logging.getLogger("video_translator")`) to track execution details.

---

## 🧪 Testing

All new features must pass existing tests and include corresponding test cases under `tests/`.

To run the unit tests:
```bash
python3 -m unittest discover -s tests
```

---

## 🚀 Submitting Pull Requests

1. Fork the repository and create your feature branch: `git checkout -b feature/amazing-feature`.
2. Commit your changes: `git commit -m 'Add some amazing feature'`.
3. Push to the branch: `git push origin feature/amazing-feature`.
4. Open a Pull Request for review.
