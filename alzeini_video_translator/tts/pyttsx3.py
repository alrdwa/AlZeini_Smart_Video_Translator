# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - pyttsx3.py
Speech synthesis using local pyttsx3 (espeak-ng) offline engine, implementing BaseTTS.
"""

import os
import subprocess
import logging

from alzeini_video_translator.tts.base import BaseTTS

logger = logging.getLogger("video_translator")

class PyTTSX3Provider(BaseTTS):
    """Completely offline, local speech synthesis using espeak-ng."""
    def __init__(self, voice_name=None):
        self.voice_name = voice_name

    def generate_speech(self, text, output_path):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Select Arabic voice if present
            for v in voices:
                if "arabic" in v.name.lower() or "ar" in v.languages:
                    engine.setProperty('voice', v.id)
                    break
                    
            temp_file = output_path.replace(".wav", ".mp3")
            engine.save_to_file(text, temp_file)
            engine.runAndWait()
            
            if os.path.exists(temp_file):
                subprocess.run(["ffmpeg", "-y", "-i", temp_file, output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.remove(temp_file)
                return True
        except Exception as e:
            logger.error(f"pyttsx3 local synthesis failed: {e}")
        return False
