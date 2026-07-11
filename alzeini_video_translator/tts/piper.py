# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - piper.py
Local offline neural speech synthesis using Piper TTS, implementing BaseTTS.
"""

import os
import subprocess
import logging

from alzeini_video_translator.tts.base import BaseTTS

logger = logging.getLogger("video_translator")

class PiperTTSProvider(BaseTTS):
    """Local, offline neural speech synthesis using Piper (ONNX)."""
    def __init__(self, voice_model="ar_JO-amina-medium.onnx"):
        self.voice_model = voice_model
        # Find voice model relative to project root
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.model_path = os.path.join(root_dir, "models", "piper", voice_model)
        self.config_path = self.model_path + ".json"

    def is_available(self):
        """Checks if piper CLI and model files are ready."""
        piper_exists = False
        try:
            import shutil
            piper_exists = shutil.which("piper") is not None
        except Exception:
            pass
            
        model_exists = os.path.exists(self.model_path)
        return piper_exists and model_exists

    def generate_speech(self, text, output_path):
        if not self.is_available():
            logger.warning("⚠️ Piper CLI or Arabic ONNX voice model is not installed. Falling back...")
            return False
            
        try:
            safe_text = text.replace('"', '\\"')
            echo_process = subprocess.Popen(["echo", safe_text], stdout=subprocess.PIPE)
            piper_cmd = [
                "piper",
                "--model", self.model_path,
                "--config", self.config_path,
                "--output_file", output_path
            ]
            
            res = subprocess.run(piper_cmd, stdin=echo_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            echo_process.stdout.close()
            
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Piper speech generation failed: {e}")
            return False
