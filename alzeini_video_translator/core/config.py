# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - config.py
Handles loading and validation of config.yaml.
"""

import os
import yaml
import logging

logger = logging.getLogger("video_translator")

def load_config(config_name="config.yaml"):
    """Loads configuration options from config.yaml in the project root."""
    # Find config.yaml in the project root folder
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    config_path = os.path.join(root_dir, config_name)
    
    if not os.path.exists(config_path):
        logger.warning(f"⚠️ Configuration file {config_name} not found. Using defaults.")
        return {}
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"❌ Failed to parse configuration file: {e}")
        return {}
