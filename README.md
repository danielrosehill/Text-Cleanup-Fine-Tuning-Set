# Text Cleanup Fine-Tuning Dataset

A dataset in progress for fine-tuning models to clean up speech-to-text transcripts.

## What This Is

A collection of speech transcripts with multiple versions showing different levels of cleanup, intended for fine-tuning models to achieve optimal transcript cleanup ("Goldilocks" level - not too much, not too little).

## Fine-Tuning Objective

The goal is to generate a fine-tuned audio multimodal model (Hugging Face task: audio-text to text) that can automatically produce cleaned transcripts matching the quality and style demonstrated in the manual cleanup examples.

**Dataset Components:**
- **Audio file**: Source recording (2-5 minutes)
- **Whisper ASR transcript**: Verbatim baseline from speech-to-text (includes all filler words and disfluencies)
- **Manual cleanup transcript**: Ground truth target demonstrating the desired cleanup quality

The fine-tuned model should learn to transform audio directly into text matching the manual cleanup style - removing filler words and disfluencies while preserving natural tone and meaning.

**Note:** Sample 1 includes an auto-cleanup transcript from Gemini 2.5 Flash as a reference example, showing the deviation between a general-purpose model and the target cleanup quality. This helps illustrate why fine-tuning is necessary. Future samples will only include audio, Whisper transcript, and manual cleanup.

## Repository Structure

```
Text-Cleanup-Fine-Tuning-Set/
│
├── dataset/                      # The actual dataset
│   ├── data/
│   │   ├── audio/               # Original audio recordings
│   │   ├── whisper-transcripts/ # Raw Whisper ASR output
│   │   ├── auto-cleanup/        # Sample 1 reference (Gemini)
│   │   └── manual-cleanups/     # Human-edited ground truth
│   ├── questions.json           # Question metadata
│   ├── dataset.json             # Complete dataset metadata
│   └── README.md               # Dataset-specific documentation
│
├── ai-analysis/                 # Fine-tuning planning & strategy
│   ├── sample-size-recommendations.md  # Target sample counts
│   ├── dataset-structure-mapping.md    # Component relationships
│   └── model-candidates.md             # Audio-text models to fine-tune
│
├── divergence-analysis/         # Sample-level cleanup analysis
│   ├── sample-1-analysis.md    # Divergence patterns in Sample 1
│   └── README.md               # Analysis methodology
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
3. **Manual Cleanup** - Human-edited ground truth showing target quality

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
