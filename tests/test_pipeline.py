# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - test_pipeline.py
Unit tests for pipeline initialization, dependency injection, and event callbacks.
"""

import unittest
import os
import sys

# Ensure package is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alzeini_video_translator.core.pipeline import VideoTranslationPipeline
from alzeini_video_translator.stt.base import BaseSTT
from alzeini_video_translator.translation.base import BaseTranslator
from alzeini_video_translator.tts.base import BaseTTS

class MockSTT(BaseSTT):
    def transcribe(self, wav_path, srt_prefix):
        return f"{srt_prefix}.srt"

class MockTranslator(BaseTranslator):
    def translate_srt(self, input_srt_path, output_srt_path, batch_size=20):
        return output_srt_path

class MockTTS(BaseTTS):
    def generate_speech(self, text, output_path):
        return True
    def generate_dubbed_video(self, video_path, srt_path, output_video_path):
        return True

class TestPipelineContract(unittest.TestCase):
    def setUp(self):
        self.dummy_video = "dummy_lecture.mp4"
        # Create a dummy video file for testing initialization
        with open(self.dummy_video, "w") as f:
            f.write("mock content")

    def tearDown(self):
        if os.path.exists(self.dummy_video):
            os.remove(self.dummy_video)

    def test_dependency_injection(self):
        """Verify that STT, Translator, and TTS dependencies are correctly injected."""
        stt = MockSTT()
        translator = MockTranslator()
        tts = MockTTS()
        
        pipeline = VideoTranslationPipeline(
            input_video=self.dummy_video,
            stt=stt,
            translator=translator,
            tts=tts
        )
        
        self.assertEqual(pipeline.stt, stt)
        self.assertEqual(pipeline.translator, translator)
        self.assertEqual(pipeline.tts, tts)

    def test_event_callback_registration(self):
        """Test callback listener subscriptions and execution."""
        pipeline = VideoTranslationPipeline(self.dummy_video)
        
        progress_fired = False
        def mock_progress_callback(percent, msg):
            nonlocal progress_fired
            progress_fired = True
            
        pipeline.register_listener("on_progress", mock_progress_callback)
        
        # Manually trigger event for verification
        pipeline._trigger_event("on_progress", 50.0, "Test in progress")
        self.assertTrue(progress_fired)

if __name__ == "__main__":
    unittest.main()
