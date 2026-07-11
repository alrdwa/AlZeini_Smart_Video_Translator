# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - app.py (v1.0 CLI Wrapper)
Command line interface to transcribe, translate, and dub video files.
Demonstrates Dependency Injection and Event Callbacks.
"""

import os
import sys
import argparse
import logging

from alzeini_video_translator.core.config import load_config
from alzeini_video_translator import VideoTranslationPipeline
from alzeini_video_translator.stt.whispercpp import VideoTranscriber
from alzeini_video_translator.translation.gemma import OllamaSRTTranslator
from alzeini_video_translator.tts.voiceover import VideoDubber

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("video_translator")

def main():
    parser = argparse.ArgumentParser(
        description="AlZeini Smart Video Translator - Modular Media dubbing engine (v1.0)"
    )
    parser.add_argument("video_path", help="Path to the input video file (.mp4, .mkv, .avi, etc.)")
    parser.add_argument("--model", help="Override default Ollama LLM model (e.g. gemma3:4b)")
    parser.add_argument("--no-translate", action="store_true", help="Bypass subtitle translation stage")
    parser.add_argument("--dub", action="store_true", help="Generate Arabic voiceover and dub the video")
    parser.add_argument("--voice", help="Target voice name override (e.g. ar-SA-HamedNeural)")
    parser.add_argument("--output-dir", help="Target output directory")
    
    args = parser.parse_args()
    
    video_path = os.path.abspath(args.video_path)
    if not os.path.exists(video_path):
        logger.error(f"❌ Input video file not found: {video_path}")
        sys.exit(1)
        
    try:
        # Load configuration parameters
        config = load_config()
        
        # 1. Dependency Injection setup
        # Instantiating the engine dependencies outside of the pipeline class
        whisper_conf = config.get("whisper", {})
        stt_engine = VideoTranscriber(
            whisper_dir=whisper_conf.get("dir", "whisper.cpp"),
            model_name=whisper_conf.get("model", "ggml-small.bin")
        )
        
        translator_engine = None
        llm_conf = config.get("llm", {})
        if not args.no_translate and llm_conf.get("correct", True):
            model_name = args.model or llm_conf.get("model", "gemma3:4b")
            translator_engine = OllamaSRTTranslator(
                host=llm_conf.get("host", "localhost"),
                port=llm_conf.get("port", 11434),
                model_name=model_name,
                temperature=llm_conf.get("temperature", 0.1)
            )
            
        tts_engine = None
        if args.dub:
            tts_engine = VideoDubber(config=config, voice_override=args.voice)
            
        # 2. Injecting dependencies into the pipeline constructor
        pipeline = VideoTranslationPipeline(
            input_video=video_path,
            stt=stt_engine,
            translator=translator_engine,
            tts=tts_engine
        )
        
        # 3. Register Event Callback listeners (Progress Manager)
        def progress_callback(percentage, message):
            print(f"📊 [Progress {percentage:.0f}%] {message}", flush=True)
            
        pipeline.register_listener("on_progress", progress_callback)
        
        # Run pipeline
        results = pipeline.run(
            no_translate=args.no_translate,
            dub=args.dub,
            output_dir=args.output_dir
        )
        
        logger.info("🎉 Processing complete!")
        print("\n==========================================")
        print("📈 Output Subtitles, Video & Metadata:")
        print(f"   🇬🇧 English SRT: {results['english_srt']}")
        if results['arabic_srt']:
            print(f"   🇸🇦 Arabic SRT:  {results['arabic_srt']}")
        if results['dubbed_video']:
            print(f"   🎬 Dubbed Video: {results['dubbed_video']}")
        print(f"   📄 Metadata Log: {results['metadata']}")
        print("==========================================\n")
        
    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
