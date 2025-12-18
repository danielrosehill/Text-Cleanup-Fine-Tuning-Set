#!/usr/bin/env python3
"""
Process Audio Script
Process existing audio files through Whisper and Gemini cleanup.
Usage: python process_audio.py <audio_file>
"""

import sys
import os
from pathlib import Path
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
WHISPER_DIR = BASE_DIR / "whisper-transcripts"
AUTO_CLEANUP_DIR = BASE_DIR / "auto-cleanup"
MANUAL_CLEANUP_DIR = BASE_DIR / "manual-cleanups"
SYSTEM_PROMPT_FILE = BASE_DIR / "system-prompts" / "cleanup.md"

# Ensure directories exist
for dir_path in [WHISPER_DIR, AUTO_CLEANUP_DIR, MANUAL_CLEANUP_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROTUER_API_KEY")  # Note: typo in .env preserved
CLEANUP_MODEL = os.getenv("TEXT_CLEANUP_VALIDATION_MODEL", "google/gemini-2.5-flash")


def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI Whisper"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in .env file")

    client = OpenAI(api_key=OPENAI_API_KEY)

    print(f"Transcribing {audio_path} with Whisper...")
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcript


def cleanup_transcript(transcript_text, system_prompt):
    """Clean up transcript using Gemini via OpenRouter"""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROTUER_API_KEY not set in .env file")

    print("Cleaning up transcript with Gemini...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": CLEANUP_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript_text}
            ]
        }
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")


def process_audio_file(audio_path):
    """Process a single audio file"""
    audio_path = Path(audio_path)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {audio_path}")
        return False

    # Get base name (without extension)
    base_name = audio_path.stem

    # Load system prompt
    if SYSTEM_PROMPT_FILE.exists():
        with open(SYSTEM_PROMPT_FILE, 'r') as f:
            system_prompt = f.read()
    else:
        system_prompt = "Clean up this transcript by removing filler words and improving readability."
        print("Warning: System prompt file not found, using default prompt")

    try:
        # Step 1: Whisper transcription
        transcript = transcribe_audio(audio_path)
        whisper_path = WHISPER_DIR / f"{base_name}.txt"
        with open(whisper_path, 'w') as f:
            f.write(transcript)
        print(f"✓ Whisper transcript saved: {whisper_path}")

        # Step 2: Gemini cleanup
        cleaned = cleanup_transcript(transcript, system_prompt)
        auto_cleanup_path = AUTO_CLEANUP_DIR / f"{base_name}.txt"
        with open(auto_cleanup_path, 'w') as f:
            f.write(cleaned)
        print(f"✓ Auto cleanup saved: {auto_cleanup_path}")

        # Step 3: Create blank manual cleanup file
        manual_cleanup_path = MANUAL_CLEANUP_DIR / f"{base_name}.txt"
        if not manual_cleanup_path.exists():
            with open(manual_cleanup_path, 'w') as f:
                f.write("")
            print(f"✓ Blank manual cleanup file created: {manual_cleanup_path}")
        else:
            print(f"⚠ Manual cleanup file already exists: {manual_cleanup_path}")

        print(f"\n✓ Processing complete!")
        print(f"\nNext steps:")
        print(f"1. Review Whisper transcript: {whisper_path}")
        print(f"2. Review auto cleanup: {auto_cleanup_path}")
        print(f"3. Create your manual cleanup: {manual_cleanup_path}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python process_audio.py <audio_file>")
        print("\nExample:")
        print("  python process_audio.py audio/1.mp3")
        sys.exit(1)

    audio_file = sys.argv[1]
    success = process_audio_file(audio_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
