# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - voiceover.py
Coordinates speech synthesis providers and applies audio dubbing mixing modes.
"""

import os
import re
import subprocess
import shutil
import logging

from alzeini_video_translator.tts.edge import EdgeTTSProvider
from alzeini_video_translator.tts.pyttsx3 import PyTTSX3Provider
from alzeini_video_translator.tts.piper import PiperTTSProvider

logger = logging.getLogger("video_translator")

class VideoDubber:
    def __init__(self, config=None, voice_override=None):
        self.config = config or {}
        
        tts_conf = self.config.get("tts", {})
        self.provider_type = tts_conf.get("provider", "edge-tts")
        self.voice = voice_override or tts_conf.get("voice", "ar-EG-SalmaNeural")
        self.mode = tts_conf.get("mode", "voice_over")
        self.bg_volume = tts_conf.get("bg_volume", 0.20)
        
        # Resolve provider
        if self.provider_type == "piper":
            logger.info("🎙️ Resolving local neural speech engine: PIPER TTS...")
            self.provider = PiperTTSProvider()
            if not self.provider.is_available():
                logger.warning("⚠️ Piper not available. Falling back to edge-tts.")
                self.provider = EdgeTTSProvider(voice=self.voice)
                self.provider_type = "edge-tts"
        elif self.provider_type == "pyttsx3":
            logger.info("🎙️ Resolving local system speech engine: PyTTSX3...")
            self.provider = PyTTSX3Provider(voice_name=self.voice)
        else:
            logger.info(f"🎙️ Resolving premium cloud neural speech engine: Edge-TTS ({self.voice})...")
            self.provider = EdgeTTSProvider(voice=self.voice)

    def _parse_timestamp(self, ts_str):
        """Converts SRT timestamp format (HH:MM:SS,mmm) to seconds (float)."""
        match = re.match(r"(\d+):(\d+):(\d+),(\d+)", ts_str.strip())
        if not match:
            return 0.0
        h, m, s, ms = map(int, match.groups())
        return h * 3600 + m * 60 + s + ms / 1000.0

    def _get_audio_duration(self, file_path):
        """Uses ffprobe to fetch the exact duration of an audio file in seconds."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return float(res.stdout.decode("utf-8").strip())
        except Exception:
            return 0.0

    def generate_dubbed_video(self, video_path, srt_path, output_video_path):
        """Orchestrates subtitle-to-speech rendering, timeline alignment, and selected video mixing mode."""
        logger.info(f"🎬 Starting video dubbing process. Mode: {self.mode}")
        
        if self.mode == "subtitles_only":
            logger.info("   Subtitles-only mode active. Bypassing voiceover synthesis. Copying video file...")
            try:
                shutil.copy(video_path, output_video_path)
                return True
            except Exception as e:
                logger.error(f"Failed to copy subtitles_only video: {e}")
                return False
                
        temp_dir = "temp_dubbing"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. Parse SRT subtitles
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        blocks = re.split(r'\n\s*\n', content)
        timeline = []
        
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                idx = lines[0].strip()
                timestamps = lines[1].split("-->")
                start = self._parse_timestamp(timestamps[0])
                end = self._parse_timestamp(timestamps[1])
                
                # Filter Arabic subtitles line
                arabic_lines = [line.strip() for line in lines[2:] if any(ord(c) in range(0x0600, 0x06FF) for c in line)]
                text = " ".join(arabic_lines) if arabic_lines else " ".join(lines[2:]).strip()
                
                timeline.append({
                    "index": idx,
                    "start": start,
                    "end": end,
                    "text": text
                })
                
        if not timeline:
            logger.error("❌ No subtitles found to render.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

        timeline.sort(key=lambda x: x["start"])
        
        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        concat_files = []
        current_time = 0.0
        
        # 2. Render each subtitle block and compile the timeline
        for item in timeline:
            idx = item["index"]
            start = item["start"]
            end = item["end"]
            text = item["text"]
            
            clean_text = re.sub(r'<[^>]*>', '', text)
            clean_text = re.sub(r'\[[^\]]*\]', '', clean_text).strip()
            
            if not clean_text:
                continue
                
            # A. Draw silence before block if needed
            silence_dur = start - current_time
            if silence_dur > 0.01:
                silence_file = os.path.join(temp_dir, f"silence_{idx}.wav")
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
                    "-t", f"{silence_dur:.3f}",
                    silence_file
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                concat_files.append(silence_file)
                current_time += silence_dur
                
            # B. Generate Speech Clip using selected provider
            speech_raw = os.path.join(temp_dir, f"speech_raw_{idx}.wav")
            logger.info(f"   Generating speech {idx} (len={len(clean_text)}) using provider: {self.provider_type}...")
            
            success = self.provider.generate_speech(clean_text, speech_raw)
            if not success or not os.path.exists(speech_raw):
                logger.warning(f"⚠️ Speech generation failed for block {idx}. Inserting silence.")
                # Create silent spacer
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", f"{end-start:.3f}", speech_raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            # C. Check duration and fit (atempo speed-up filter)
            speech_dur = self._get_audio_duration(speech_raw)
            allowed_dur = end - start
            final_speech_file = os.path.join(temp_dir, f"speech_final_{idx}.wav")
            
            if speech_dur > allowed_dur and allowed_dur > 0.1:
                speed = speech_dur / allowed_dur
                if speed > 2.0:
                    speed = 2.0
                logger.info(f"   ⏱️ Fitting block {idx} (speedup {speed:.2f}x)...")
                cmd = [
                    "ffmpeg", "-y",
                    "-i", speech_raw,
                    "-filter:a", f"atempo={speed:.2f}",
                    final_speech_file
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                current_time += (speech_dur / speed)
            else:
                # Format normalization
                cmd = [
                    "ffmpeg", "-y",
                    "-i", speech_raw,
                    final_speech_file
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                current_time += speech_dur
                
            concat_files.append(final_speech_file)
            
        # 3. Write concat list
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for fpath in concat_files:
                f.write(f"file '{os.path.abspath(fpath)}'\n")
                
        # 4. Compile compiled voiceover WAV track
        voiceover_wav = os.path.join(temp_dir, "voiceover_compiled.wav")
        logger.info("🔊 Concatenating speech timeline segments...")
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c:a", "pcm_s16le",
            voiceover_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if not os.path.exists(voiceover_wav):
            logger.error("❌ Failed to compile voiceover track.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
            
        # 5. Multiplex Voiceover WAV based on selected mode
        if self.mode == "full_dub":
            logger.info("🎛️ Mixing Mode: FULL DUB (Original audio completely replaced with Arabic voiceover)...")
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", voiceover_wav,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                output_video_path
            ]
        else: # Default: voice_over
            logger.info(f"🎛️ Mixing Mode: VOICE OVER (Background audio ducked to {self.bg_volume*100:.1f}%)...")
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", voiceover_wav,
                "-filter_complex", f"[0:a]volume={self.bg_volume:.2f}[bg]; [1:a]volume=1.0[voice]; [bg][voice]amix=inputs=2:duration=first[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy",
                output_video_path
            ]
            
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if res.returncode == 0 and os.path.exists(output_video_path):
            logger.info(f"🎉 Success! Dubbed video created: {output_video_path}")
            return True
        else:
            logger.error(f"❌ Video mixing failed: {res.stderr.decode('utf-8', errors='ignore')}")
            return False
