# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - whispercpp.py
Speech-To-Text transcriber using compiled whisper.cpp binaries, implementing BaseSTT.
"""

import os
import subprocess
import logging

from alzeini_video_translator.stt.base import BaseSTT

logger = logging.getLogger("video_translator")

class VideoTranscriber(BaseSTT):
    def __init__(self, whisper_dir="whisper.cpp", model_name="ggml-small.bin"):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if not os.path.isabs(whisper_dir):
            self.whisper_dir = os.path.abspath(os.path.join(root_dir, whisper_dir))
        else:
            self.whisper_dir = os.path.abspath(whisper_dir)
            
        self.binary_path = os.path.join(self.whisper_dir, "main")
        
        # Resolve model path from the centralized models/whisper directory
        self.model_path = os.path.join(root_dir, "models", "whisper", model_name)

    def is_ready(self):
        """Checks if whisper.cpp binaries and models are fully compiled and download-complete."""
        return os.path.exists(self.binary_path) and os.path.exists(self.model_path)

    def extract_audio(self, video_path, output_wav_path):
        """Uses ffmpeg to extract 16kHz mono WAV from the input video file."""
        logger.info(f"🎙️ Extracting audio track from: {video_path}")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            output_wav_path
        ]
        
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode != 0:
                logger.error(f"ffmpeg extraction failed: {res.stderr.decode('utf-8', errors='ignore')}")
                return False
            logger.info("✅ Audio extraction completed successfully.")
            return True
        except FileNotFoundError:
            logger.error("❌ ffmpeg command not found. Please install ffmpeg ('sudo apt install ffmpeg').")
            return False

    def transcribe(self, wav_path, srt_prefix):
        """Runs whisper.cpp on the audio file and saves the transcript in SRT format."""
        if not self.is_ready():
            raise FileNotFoundError(f"Whisper.cpp binary or model file missing. Checked binary: {self.binary_path}, model: {self.model_path}")
            
        logger.info(f"✍️ Starting audio transcription using Whisper.cpp...")
        
        cmd = [
            self.binary_path,
            "-m", self.model_path,
            "-f", wav_path,
            "-osrt",
            "-of", srt_prefix
        ]
        
        logger.info(f"   Executing command: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode != 0:
                logger.error(f"Whisper.cpp transcription failed: {res.stderr.decode('utf-8', errors='ignore')}")
                return None
                
            srt_path = f"{srt_prefix}.srt"
            if os.path.exists(srt_path):
                logger.info(f"✅ Transcription completed. Subtitles saved to: {srt_path}")
                return srt_path
            else:
                logger.error("❌ Transcription finished but output SRT file was not generated.")
                return None
        except Exception as e:
            logger.error(f"Failed to execute Whisper.cpp: {e}")
            return None
