# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - edge.py
Speech synthesis using Microsoft Edge Neural TTS API, implementing BaseTTS.
"""

import os
import subprocess

from alzeini_video_translator.tts.base import BaseTTS

class EdgeTTSProvider(BaseTTS):
    """Premium Neural speech synthesis using Microsoft Edge API."""
    def __init__(self, voice="ar-EG-SalmaNeural"):
        self.voice = voice

    def generate_speech(self, text, output_path):
        cmd = [
            "edge-tts",
            "--voice", self.voice,
            "--text", text,
            "--write-media", output_path
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception:
            return False
