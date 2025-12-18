# Dataset Creation Workflow

This document describes the complete workflow for creating the text cleanup fine-tuning dataset.

## Overview

This repository creates a fine-tuning dataset for training models to clean up speech-to-text transcripts. The workflow captures:

1. **Audio recordings** - Voice responses to predefined questions
2. **Raw ASR transcripts** - Whisper transcriptions (with filler words, disfluencies)
3. **Auto cleanup** - Gemini 2.5 Flash automated cleanup
4. **Manual cleanup** - Human-edited ground truth (the "Goldilocks" level)

## Prerequisites

### Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
OPENROTUER_API_KEY=your_openrouter_key_here
TEXT_CLEANUP_VALIDATION_MODEL=google/gemini-2.5-flash
```

## Workflow Steps

### Step 1: Record Audio Responses

Use the GUI application to record responses to questions:

```bash
python transcript_recorder.py
```

**GUI Workflow:**

1. Select a question from the list
2. Choose your microphone
3. Click "Start Recording"
4. Answer the question (speak naturally!)
5. Click "Stop Recording"

The application automatically:
- Saves the audio file
- Transcribes with OpenAI Whisper
- Cleans up with Gemini 2.5 Flash
- Creates a blank manual cleanup file
- Updates `dataset.json` with metadata

### Step 2: Create Manual Cleanup (Ground Truth)

After recording, edit the manual cleanup file to create your ideal transcript:

1. Open `manual-cleanups/{sample_number}.txt`
2. Review the auto cleanup version for reference
3. Create your perfect cleanup:
   - Remove filler words ("um", "uh", "like", "you know")
   - Add proper punctuation and paragraph breaks
   - Fix disfluencies and false starts
   - Maintain natural voice and meaning
   - **Don't go too far** - keep it conversational

**Example:**

```
Raw Whisper:
"So, um, the typical way that I would develop software, okay, over the course
of the past year, working with AI agents very extensively..."

Manual Cleanup:
"Over the course of the past year, during which I have worked with AI systems
very extensively, my development method has come to be shaped by using them."
```

### Step 3: Build and Validate Dataset

After creating manual cleanups, rebuild the dataset metadata:

```bash
# Build dataset.json with comprehensive metadata
python dataset_builder.py build

# Validate completeness
python dataset_builder.py validate

# View summary
python dataset_builder.py summary
```

### Step 4: Export Training Dataset

Once you have enough complete samples:

```bash
# Export to JSONL format (common for fine-tuning)
python dataset_builder.py export jsonl

# Or export to JSON format
python dataset_builder.py export json
```

This creates `dataset_training.jsonl` with input/output pairs ready for fine-tuning.

## Dataset Structure

### Directory Layout

```
Text-Cleanup-Fine-Tuning-Set/
├── audio/                      # Audio recordings (MP3/WAV)
├── whisper-transcripts/        # Raw Whisper ASR output
├── auto-cleanup/               # Gemini automated cleanup
├── manual-cleanups/            # Human-edited ground truth
├── questions/                  # Question definitions
├── system-prompts/            # Prompts for cleanup
├── questions.json             # Question metadata
├── dataset.json              # Complete dataset metadata
├── dataset_training.jsonl    # Training-ready export
├── transcript_recorder.py    # GUI recording application
├── dataset_builder.py        # Dataset management
└── process_audio.py          # CLI audio processor
```

### dataset.json Structure

```json
{
  "metadata": {
    "name": "Text Cleanup Fine-Tuning Dataset",
    "version": "1.0.0",
    "author": "Daniel Rosehill"
  },
  "statistics": {
    "total_samples": 10,
    "completed_samples": 1,
    "completion_percentage": 10.0
  },
  "configuration": {
    "transcription_model": "openai/whisper-1",
    "cleanup_model": "google/gemini-2.5-flash"
  },
  "samples": [
    {
      "id": "uuid",
      "sample_number": 1,
      "question": "Question text...",
      "files": {
        "audio": "audio/1.mp3",
        "whisper_transcript": "whisper-transcripts/1.txt",
        "auto_cleanup": "auto-cleanup/1.txt",
        "manual_cleanup": "manual-cleanups/1.txt"
      },
      "audio_metadata": {
        "duration_seconds": 367.44,
        "format": "mp3"
      },
      "text_statistics": {
        "whisper_word_count": 911,
        "auto_cleanup_word_count": 891,
        "manual_cleanup_word_count": 859
      },
      "models": {
        "transcription": "openai/whisper-1",
        "auto_cleanup": "google/gemini-2.5-flash"
      },
      "status": {
        "is_complete": true
      },
      "content": {
        "whisper_transcript": "...",
        "auto_cleanup": "...",
        "manual_cleanup": "..."
      }
    }
  ]
}
```

## Dataset Builder Commands

### Build Dataset

```bash
python dataset_builder.py build
```

Builds `dataset.json` from all files, calculating statistics and metadata.

### Validate Dataset

```bash
python dataset_builder.py validate
```

Checks for:
- Missing audio files
- Missing transcripts
- Missing cleanups
- Empty manual cleanups

### View Summary

```bash
python dataset_builder.py summary
```

Shows progress and completion status for all samples.

### Export for Training

```bash
# JSONL format (one JSON object per line)
python dataset_builder.py export jsonl

# JSON format (array of objects)
python dataset_builder.py export json
```

Creates training-ready dataset with input/output pairs:

```json
{
  "input": "Raw Whisper transcript...",
  "output": "Manual cleanup ground truth...",
  "metadata": {
    "sample_id": "uuid",
    "sample_number": 1,
    "question": "Question text..."
  }
}
```

## Processing Existing Audio (CLI)

If you have audio files recorded outside the GUI:

```bash
python process_audio.py audio/my_recording.mp3
```

This will:
1. Transcribe with Whisper
2. Clean up with Gemini
3. Create blank manual cleanup file

Then manually edit the manual cleanup file and rebuild the dataset.

## Best Practices

### Recording Tips

1. **Speak naturally** - Don't try to be perfect
2. **Answer completely** - Give full, detailed responses
3. **Use your normal voice** - Include natural pauses and filler words
4. **Choose good questions** - Pick questions that elicit natural, conversational speech

### Manual Cleanup Guidelines

The goal is to find the "Goldilocks" level - not too clean, not too raw:

**Do:**
- Remove obvious filler words (um, uh, like)
- Fix false starts and repetitions
- Add proper punctuation and paragraphs
- Maintain conversational tone
- Preserve meaning and intent

**Don't:**
- Make it sound too formal or written
- Add content that wasn't said
- Remove personality and voice
- Over-correct casual language
- Remove all informality

### Dataset Quality

- **Consistency** - Apply the same cleanup standards to all samples
- **Completeness** - Ensure all samples have all components
- **Validation** - Run `validate` before considering the dataset complete
- **Documentation** - Note your cleanup approach in the system prompt

## Troubleshooting

### Audio Not Recording

- Check microphone selection in GUI
- Verify microphone permissions
- Try `arecord -l` to list audio devices

### API Errors

- Verify API keys in `.env` file
- Check API rate limits
- Ensure models are available (Whisper, Gemini)

### File Not Found

- Run `python dataset_builder.py build` to refresh metadata
- Check file naming (UUID vs numeric)
- Verify files exist in expected directories

## Next Steps

Once you have a complete dataset:

1. **Fine-tune a model** using the exported training data
2. **Test the model** on new audio samples
3. **Iterate** - Add more samples if needed
4. **Version** - Tag dataset versions in git

## Version Control

The repository uses git to track:
- Questions and metadata
- Code and scripts
- System prompts
- Dataset structure (dataset.json)

**Not tracked:**
- Audio files (large, generated)
- Transcript files (generated)
- Exported training files (generated from dataset.json)

To save your manual cleanups, commit `dataset.json` which contains all the text.

## Support

For issues or questions:
- Check this WORKFLOW.md
- Review the README.md
- Examine the code comments in Python scripts
- Run commands with `--help` or check function docstrings
