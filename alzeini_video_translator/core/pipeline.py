# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - pipeline.py
Orchestrates pipeline execution, supporting Dependency Injection, 
Real-time Event callbacks, and metadata JSON logging.
"""

import os
import sys
import logging
import json
import time
import subprocess
from datetime import datetime

from alzeini_video_translator.core.config import load_config
from alzeini_video_translator.stt.whispercpp import VideoTranscriber
from alzeini_video_translator.translation.gemma import OllamaSRTTranslator
from alzeini_video_translator.tts.voiceover import VideoDubber

logger = logging.getLogger("video_translator")

def setup_file_logging():
    """Configures logging handlers to write to a log file logs/YYYY-MM-DD.log."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    logs_dir = os.path.join(root_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(logs_dir, f"{date_str}.log")
    
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    file_handler.setFormatter(formatter)
    
    for h in logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            
    logger.addHandler(file_handler)


class VideoTranslationPipeline:
    def __init__(self, input_video, stt=None, translator=None, tts=None, config_name="config.yaml", voice_override=None, model_override=None):
        self.video_path = os.path.abspath(input_video)
        self.config = load_config(config_name)
        self.voice_override = voice_override
        self.model_override = model_override
        self.base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        
        # 1. Dependency Injection Resolution
        self.stt = stt
        self.translator = translator
        self.tts = tts
        
        # 2. Callbacks initialization
        self.callbacks = {
            "on_start": [],
            "on_progress": [],  # receives: (percentage: float, message: str)
            "on_finish": [],    # receives: (results: dict)
            "on_error": []      # receives: (error_message: str)
        }
        
        setup_file_logging()

    def register_listener(self, event_name, callback):
        """Allows external modules to listen to pipeline events."""
        if event_name in self.callbacks:
            self.callbacks[event_name].append(callback)
            
    def _trigger_event(self, event_name, *args, **kwargs):
        """Fires registered callbacks for a specific event."""
        for callback in self.callbacks.get(event_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error during {event_name}: {e}")

    def _get_video_duration(self):
        """Queries video duration in seconds via ffprobe."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            self.video_path
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            duration = float(res.stdout.decode("utf-8").strip())
            return f"{duration:.2f} seconds"
        except Exception:
            return "unknown"

    def run(self, no_translate=False, dub=False, output_dir=None):
        """Executes the translation and dubbing stages, emitting progress updates."""
        start_time = time.time()
        self._trigger_event("on_start")
        logger.info(f"🚀 Starting AlZeini Media Pipeline for: {self.base_name}")
        
        try:
            if not os.path.exists(self.video_path):
                raise FileNotFoundError(f"Video file not found: {self.video_path}")
                
            # 1. Output folder setup
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            if output_dir:
                out_dir = os.path.abspath(output_dir)
            else:
                out_dir = os.path.join(root_dir, "output", self.base_name)
                
            audio_dir = os.path.join(out_dir, "audio")
            subtitle_dir = os.path.join(out_dir, "subtitle")
            translation_dir = os.path.join(out_dir, "translation")
            voice_dir = os.path.join(out_dir, "voice")
            
            for folder in [audio_dir, subtitle_dir, translation_dir, voice_dir]:
                os.makedirs(folder, exist_ok=True)
                
            self._trigger_event("on_progress", 10.0, "Extracting audio track...")
            
            # 2. Default Resolution if not injected
            if not self.stt:
                whisper_conf = self.config.get("whisper", {})
                self.stt = VideoTranscriber(
                    whisper_dir=whisper_conf.get("dir", "whisper.cpp"),
                    model_name=whisper_conf.get("model", "ggml-small.bin")
                )
                
            # 3. Audio Extraction & Speech Recognition
            temp_wav = os.path.join(audio_dir, f"{self.base_name}_temp.wav")
            # We cast our self.stt checking
            if hasattr(self.stt, "extract_audio"):
                success = self.stt.extract_audio(self.video_path, temp_wav)
            else:
                # Default extraction fallback
                success = VideoTranscriber().extract_audio(self.video_path, temp_wav)
                
            if not success:
                raise RuntimeError("Audio extraction failed.")
                
            self._trigger_event("on_progress", 30.0, "Transcribing speech to text...")
            
            english_srt_prefix = os.path.join(subtitle_dir, f"{self.base_name}_EN")
            english_srt_path = self.stt.transcribe(temp_wav, english_srt_prefix)
            
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            if not english_srt_path:
                raise RuntimeError("Speech transcription failed.")
                
            self._trigger_event("on_progress", 60.0, "Translating subtitles to Arabic...")
            
            # 4. Subtitle Translation
            llm_conf = self.config.get("llm", {})
            enable_translate = not no_translate and llm_conf.get("correct", True)
            
            arabic_srt_path = None
            if enable_translate:
                if not self.translator:
                    model_name = self.model_override or llm_conf.get("model", "gemma3:4b")
                    self.translator = OllamaSRTTranslator(
                        host=llm_conf.get("host", "localhost"),
                        port=llm_conf.get("port", 11434),
                        model_name=model_name,
                        temperature=llm_conf.get("temperature", 0.1)
                    )
                arabic_srt_path = os.path.join(translation_dir, f"{self.base_name}_AR.srt")
                trans_conf = self.config.get("translation", {})
                self.translator.translate_srt(
                    input_srt_path=english_srt_path,
                    output_srt_path=arabic_srt_path,
                    batch_size=trans_conf.get("batch_size", 20)
                )
                
            self._trigger_event("on_progress", 80.0, "Generating voiceover and dubbing video...")
            
            # 5. Video Dubbing
            dubbed_video_path = None
            if dub and arabic_srt_path and os.path.exists(arabic_srt_path):
                if not self.tts:
                    self.tts = VideoDubber(config=self.config, voice_override=self.voice_override)
                    
                dubbed_video_path = os.path.join(voice_dir, f"{self.base_name}_dubbed.mp4")
                success = self.tts.generate_dubbed_video(self.video_path, arabic_srt_path, dubbed_video_path)
                if not success:
                    logger.error("❌ Audio dubbing failed.")
                    dubbed_video_path = None
                    
            self._trigger_event("on_progress", 95.0, "Writing project metadata.json...")
            
            # 6. Exporter: Write metadata.json for audit and reproducibility
            elapsed_time = time.time() - start_time
            metadata = {
                "video_name": self.base_name,
                "duration": self._get_video_duration(),
                "stt_engine": self.stt.__class__.__name__,
                "translator_engine": self.translator.__class__.__name__ if self.translator else "None",
                "tts_engine": self.tts.__class__.__name__ if (dub and self.tts) else "None",
                "processing_time_seconds": round(elapsed_time, 2),
                "created_at": datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(out_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            self._trigger_event("on_progress", 100.0, "Pipeline completed successfully!")
            
            results = {
                "english_srt": english_srt_path,
                "arabic_srt": arabic_srt_path,
                "dubbed_video": dubbed_video_path,
                "metadata": metadata_path
            }
            
            self._trigger_event("on_finish", results)
            return results
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            self._trigger_event("on_error", str(e))
            raise e
