# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - base.py
Translation Base Interface.
"""

class BaseTranslator:
    """Base Contract for text translation and subtitle translation engines."""
    def translate_srt(self, input_srt_path, output_srt_path, batch_size=20):
        raise NotImplementedError("Translators must implement the translate_srt method.")
