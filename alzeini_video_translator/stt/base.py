# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - base.py
STT Base Interface.
"""

class BaseSTT:
    """Base Contract for Speech-To-Text transcribers."""
    def transcribe(self, wav_path, srt_prefix):
        raise NotImplementedError("STT engines must implement the transcribe method.")
