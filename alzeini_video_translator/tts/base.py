# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - base.py
TTS Base Interface.
"""

class BaseTTS:
    """Base Contract for Speech Synthesis engines."""
    def generate_speech(self, text, output_path):
        raise NotImplementedError("TTS engines must implement the generate_speech method.")
