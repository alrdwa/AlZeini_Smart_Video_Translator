# -*- coding: utf-8 -*-
"""
AlZeini Smart Video Translator - setup_whisper.py
Automates cloning, compiling whisper.cpp, and downloading model weights into models/whisper.
"""

import os
import subprocess
import urllib.request
import sys
import argparse

def run_cmd(cmd, cwd=None):
    print(f"🚀 Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if res.returncode != 0:
        print(f"❌ Command failed with exit code: {res.returncode}")
        sys.exit(res.returncode)

def download_file(url, output_path):
    print(f"📥 Downloading: {url} -> {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Custom progress indicator
    def report(block_num, block_size, total_size):
        read_so_far = block_num * block_size
        if total_size > 0:
            percent = min(100, read_so_far * 100 / total_size)
            sys.stdout.write(f"\r   Download Progress: {percent:.1f}% ({read_so_far / (1024*1024):.1f} MB of {total_size / (1024*1024):.1f} MB)")
        else:
            sys.stdout.write(f"\r   Downloaded: {read_so_far / (1024*1024):.1f} MB")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, output_path, reporthook=report)
    print("\n✅ Download completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Compile whisper.cpp and download model weights.")
    parser.add_argument(
        "--model", 
        default="small", 
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size to download (default: small - best accuracy/speed balance for CPU)"
    )
    args = parser.parse_args()

    repo_url = "https://github.com/ggerganov/whisper.cpp.git"
    whisper_dir = "whisper.cpp"
    
    # Hugging Face URL structure for GGML models
    model_file = f"ggml-{args.model}.bin"
    model_url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{model_file}"
    
    # Save directly to root models/whisper directory
    models_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "whisper"))
    model_path = os.path.join(models_root, model_file)

    # 1. Clone whisper.cpp if not present
    if not os.path.exists(whisper_dir):
        print(f"📂 Cloning whisper.cpp repository...")
        run_cmd(["git", "clone", repo_url, whisper_dir])
    else:
        print(f"✅ whisper.cpp repository already exists.")

    # 2. Build whisper.cpp using make
    binary_path = os.path.join(whisper_dir, "main")
    if not os.path.exists(binary_path):
        print(f"🛠️ Compiling whisper.cpp...")
        run_cmd(["make"], cwd=whisper_dir)
    else:
        print(f"✅ whisper.cpp binary already compiled.")

    # 3. Download Model Weights if not present
    if not os.path.exists(model_path):
        print(f"📊 Model weights missing. Fetching '{args.model}' model ({model_file})...")
        download_file(model_url, model_path)
    else:
        print(f"✅ Whisper '{args.model}' model weights already present.")

    print(f"\n🎉 whisper.cpp setup completed successfully! Ready to transcribe with model: {args.model}")

if __name__ == "__main__":
    main()
