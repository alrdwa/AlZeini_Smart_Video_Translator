# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - gemma.py
Translates SRT files using local Ollama model (Gemma/Qwen), implementing BaseTranslator.
"""

import os
import re
import json
import urllib.request
import logging

from alzeini_video_translator.translation.base import BaseTranslator

logger = logging.getLogger("video_translator")

class OllamaSRTTranslator(BaseTranslator):
    def __init__(self, host="localhost", port=11434, model_name="gemma3:4b", temperature=0.1):
        self.api_url = f"http://{host}:{port}/api/chat"
        self.model_name = model_name
        self.temperature = temperature
        self.is_available = self._check_ollama_status()

    def _check_ollama_status(self):
        """Checks if local Ollama server is running and accessible."""
        try:
            check_url = self.api_url.replace("/api/chat", "/api/tags")
            req = urllib.request.Request(check_url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    def parse_srt(self, srt_path):
        """Parses an SRT file into a list of dictionaries containing index, timestamp, and text."""
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"SRT file not found: {srt_path}")
            
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        blocks_raw = re.split(r'\n\s*\n', content)
        subtitles = []
        
        for block in blocks_raw:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                idx = lines[0].strip()
                timestamp = lines[1].strip()
                text = " ".join(lines[2:]).strip()
                subtitles.append({
                    "index": idx,
                    "timestamp": timestamp,
                    "text": text
                })
        return subtitles

    def write_srt(self, subtitles, output_path):
        """Compiles a list of subtitle dictionaries back into a standard SRT file."""
        with open(output_path, "w", encoding="utf-8") as f:
            for sub in subtitles:
                f.write(f"{sub['index']}\n")
                f.write(f"{sub['timestamp']}\n")
                f.write(f"{sub['text']}\n\n")

    def _translate_batch(self, batch):
        """Translates a batch of subtitle blocks using context-aware XML tags."""
        prompt_blocks = []
        for item in batch:
            prompt_blocks.append(f'<block id="{item["index"]}">{item["text"]}</block>')
            
        xml_payload = "\n".join(prompt_blocks)
        
        system_instructions = (
            "You are an expert translator. Translate the following English video subtitle blocks into natural, "
            "conversational, and contextually accurate Arabic. Keep explanations out of the translation. "
            "Preserve block IDs exactly. Do not translate the XML tags themselves. Output the translated texts inside the matching XML blocks.\n"
            "Format example:\n"
            "<block id=\"1\">الترجمة العربية...</block>"
        )
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": xml_payload}
            ],
            "options": {
                "temperature": self.temperature
            },
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                response_text = res_data["message"]["content"]
                
                pattern = re.compile(r'<block id="(\d+)"[^>]*>(.*?)</block>', re.DOTALL | re.IGNORECASE)
                matches = pattern.findall(response_text)
                
                translations = {}
                for idx, text in matches:
                    translations[idx.strip()] = text.strip()
                    
                for item in batch:
                    idx_str = str(item["index"])
                    if idx_str in translations:
                        item["text"] = translations[idx_str]
                    else:
                        item["text"] = self._translate_single_fallback(item["text"])
                        
        except Exception as e:
            logger.error(f"Error during batch translation: {e}. Bypassing correction for this batch.")
            pass

    def _translate_single_fallback(self, text):
        """Translates a single block on failure to preserve timing alignment."""
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "Translate this video subtitle line to natural Arabic. Output only the translation, no explanations."},
                {"role": "user", "content": text}
            ],
            "options": {"temperature": 0.1},
            "stream": False
        }
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["message"]["content"].strip()
        except Exception:
            return text

    def translate_srt(self, input_srt_path, output_srt_path, batch_size=20):
        """Translates the complete SRT file page/batch-by-page."""
        if not self.is_available:
            logger.warning("⚠️ Ollama is offline. Subtitle translation bypassed. Copying raw English subtitles...")
            try:
                shutil.copy(input_srt_path, output_srt_path)
            except Exception:
                pass
            return output_srt_path
            
        logger.info(f"🧠 Translating subtitles from {input_srt_path} to {output_srt_path} using model {self.model_name}...")
        subtitles = self.parse_srt(input_srt_path)
        
        for i in range(0, len(subtitles), batch_size):
            batch = subtitles[i:i+batch_size]
            logger.info(f"   Translating subtitle blocks {i+1} to {min(i+batch_size, len(subtitles))}...")
            self._translate_batch(batch)
            
        self.write_srt(subtitles, output_srt_path)
        logger.info(f"✅ Subtitles successfully translated and saved: {output_srt_path}")
        return output_srt_path
