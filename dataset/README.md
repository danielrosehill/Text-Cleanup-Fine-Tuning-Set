# Text Cleanup Fine-Tuning Dataset

A curated dataset for training speech-to-text cleanup models to achieve optimal transcript refinement.

## Dataset Description

This dataset contains paired examples of raw speech-to-text transcriptions and manually-cleaned versions, designed for fine-tuning models to clean up transcripts to a specific quality level ("Goldilocks" cleanup - not too much, not too little).

### Dataset Structure

```
dataset/
├── data/
│   ├── audio/                    # Audio recordings (MP3/WAV)
│   ├── whisper-transcripts/      # Raw Whisper ASR transcriptions
│   ├── auto-cleanup/             # Automated cleanup (Gemini 2.5 Flash)
│   └── manual-cleanups/          # Human-edited ground truth
├── questions.json                # Question metadata
├── dataset.json                  # Complete dataset metadata
└── README.md                     # This file
```

### Data Fields

Each sample in `dataset.json` contains:

- **id**: Unique sample identifier (UUID)
- **sample_number**: Sequential sample number
- **question**: The question that prompted the response
- **files**: Paths to audio and text files
- **audio_metadata**: Duration, format, sample rate
- **text_statistics**: Word counts for each version
- **models**: Models used for transcription and cleanup
- **status**: Processing completion flags
- **content**: Full text of transcripts and cleanups

### Cleanup Guidelines

The manual cleanups follow these principles:

**What to Remove:**
- Filler words (um, uh, like, you know)
- False starts and repetitions
- Disfluencies and verbal pauses

**What to Preserve:**
- Natural conversational tone
- Speaker's meaning and intent
- Personality and voice
- Casual but clear language

**Goal:** Readable transcripts that maintain the speaker's voice while removing transcription artifacts.

## Dataset Creation

### Source Data

- Audio recordings of natural speech responses to open-ended questions
- Recorded by a single speaker (Daniel Rosehill)
- Questions designed to elicit 2-5 minute conversational responses
- Topics: software development, AI, technology, workflows

### Processing Pipeline

1. **Recording**: Audio captured via microphone (44.1kHz WAV)
2. **ASR Transcription**: OpenAI Whisper (whisper-1 model)
3. **Automated Cleanup**: Google Gemini 2.5 Flash via OpenRouter
4. **Manual Cleanup**: Human-edited ground truth

### Annotations

Manual cleanups are created by the dataset author following consistent cleanup principles to establish a target quality level for model training.

## Usage

### Training Format

The dataset can be exported in JSONL format with input/output pairs:

```json
{
  "input": "Raw Whisper transcript with filler words and disfluencies...",
  "output": "Cleaned transcript maintaining natural tone...",
  "metadata": {
    "sample_id": "uuid",
    "sample_number": 1,
    "question": "Original question..."
  }
}
```

### Intended Use

- Fine-tuning text cleanup models
- Training audio multimodal models for direct audio-to-clean-text
- Establishing transcript quality standards
- Voice-to-text pipeline improvement

### Out-of-Scope Use

- This is not a speech recognition dataset (use Whisper or similar for ASR)
- Not suitable for speaker identification or voice cloning
- Single-speaker dataset (may not generalize to all speakers)

## Dataset Statistics

- **Total Samples**: See `dataset.json` for current count
- **Average Audio Length**: ~3-5 minutes per sample
- **Average Word Count**:
  - Whisper: ~900 words
  - Manual Cleanup: ~850 words (5-10% reduction)
- **Language**: English (US)
- **Speaker**: Single speaker (male, native English)

## Versioning

- **Version**: 1.0.0
- **Created**: December 2024
- **License**: Private (see main repository LICENSE)

## Citation

If you use this dataset, please cite:

```
@dataset{text_cleanup_finetuning,
  author = {Daniel Rosehill},
  title = {Text Cleanup Fine-Tuning Dataset},
  year = {2024},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/[username]/text-cleanup-finetuning}
}
```

## Contact

For questions or issues with this dataset:
- **Author**: Daniel Rosehill
- **Website**: danielrosehill.com
- **Email**: public@danielrosehill.com

## Acknowledgments

- **Transcription**: OpenAI Whisper API
- **Automated Cleanup**: Google Gemini 2.5 Flash via OpenRouter
- **Tools**: Custom Python GUI and dataset management scripts

---

**Note**: This dataset is part of an ongoing project. Additional samples will be added over time to reach target dataset size of 50-100 samples.
