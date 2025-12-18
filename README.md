# Text Cleanup Fine-Tuning Dataset

A dataset in progress for fine-tuning models to clean up speech-to-text transcripts.

## What This Is

A collection of speech transcripts with multiple versions showing different levels of cleanup, intended for fine-tuning models to achieve optimal transcript cleanup ("Goldilocks" level - not too much, not too little).

## Repository Structure

```
Text-Cleanup-Fine-Tuning-Set/
│
├── dataset/                      # The actual dataset
│   ├── data/
│   │   ├── audio/               # Original audio recordings
│   │   ├── whisper-transcripts/ # Raw Whisper ASR output
│   │   ├── auto-cleanup/        # Automated cleanup (Gemini)
│   │   └── manual-cleanups/     # Human-edited ground truth
│   ├── questions.json           # Question metadata
│   ├── dataset.json             # Complete dataset metadata
│   └── README.md               # Dataset-specific documentation
│
└── Tools for dataset creation
    ├── transcript_recorder.py   # GUI for recording and processing
    ├── dataset_builder.py       # Dataset management and export
    ├── process_audio.py         # CLI audio processor
    └── requirements.txt         # Python dependencies
```

## The Pipeline

Each sample goes through this process:

1. **Audio Recording** - Voice response to a question (2-5 minutes)
2. **Whisper Transcription** - Raw ASR output with filler words and disfluencies
3. **Auto Cleanup** - Gemini 2.5 Flash attempts cleanup
4. **Manual Cleanup** - Human-edited ground truth showing target quality

The manual cleanup is the training target, demonstrating the desired level of cleanup.

## Dataset Format

The `dataset.json` file contains comprehensive metadata for each sample:

- Sample ID and question
- File paths to all versions
- Audio metadata (duration, format)
- Text statistics (word counts)
- Models used
- Processing status

Export formats available: JSON, JSONL (for training)

## Usage

### Recording New Samples

```bash
source .venv/bin/activate
python transcript_recorder.py
```

GUI walks through: select question → record audio → automatic processing → create manual cleanup

### Managing the Dataset

```bash
# Build/update metadata
python dataset_builder.py build

# Check completeness
python dataset_builder.py validate

# Export for training
python dataset_builder.py export jsonl
```

## Cleanup Philosophy

**Remove:**
- Filler words (um, uh, like)
- False starts and repetitions
- Disfluencies

**Preserve:**
- Natural conversational tone
- Speaker's meaning
- Personality and voice

## Current Status

See `dataset/dataset.json` for current sample count and completion status.

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys in .env
OPENAI_API_KEY=your_key_here
OPENROTUER_API_KEY=your_key_here
TEXT_CLEANUP_VALIDATION_MODEL=google/gemini-2.5-flash
```

## License

MIT License

## Author

Daniel Rosehill
- Website: danielrosehill.com
- Email: public@danielrosehill.com
