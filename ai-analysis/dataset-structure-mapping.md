# Dataset Structure Mapping for Fine-Tuning

## Overview

This document explains how the different transcript versions in this dataset map to the fine-tuning process for an audio multimodal model.

## The Four Components

### 1. Audio File
**Directory:** `dataset/data/audio/`
**Format:** MP3 (44.1kHz)
**Role in Fine-Tuning:** PRIMARY INPUT

This is the source audio recording that the model will process. In the fine-tuning task:
- **Training:** Audio serves as the input to the model
- **Inference:** New audio files will be processed the same way

### 2. Whisper ASR Transcript
**Directory:** `dataset/data/whisper-transcripts/`
**Model:** `openai/whisper-1`
**Role in Fine-Tuning:** BASELINE REFERENCE (what NOT to produce)

This verbatim transcript shows:
- Raw ASR output with all filler words ("um", "uh", "like")
- False starts and repetitions
- Disfluencies and self-corrections
- Natural speech artifacts

**Example characteristics:**
- "So, the typical way that I would develop software, okay, over the course of..."
- Contains unnecessary verbal markers
- ~911 words for Sample 1

**Fine-tuning use:** This demonstrates the "before" state and helps establish the baseline we're improving upon. While not directly used in training, it provides context for understanding the cleanup task.

### 3. Auto Cleanup Transcript
**Directory:** `dataset/data/auto-cleanup/`
**Model:** `google/gemini-2.5-flash` (with general cleanup prompt)
**Role in Fine-Tuning:** INTERMEDIATE REFERENCE (partially correct)

This guided cleanup shows what an **untrained** model produces when given a general system prompt for transcript cleanup:
- Some filler words removed
- Some sentence restructuring
- But not consistently matching target quality
- May be too aggressive or not aggressive enough

**Example characteristics:**
- Cleaner than Whisper but not perfect
- ~891 words for Sample 1 (slight reduction from 911)
- Inconsistent cleanup decisions

**Fine-tuning use:** This shows the "middle ground" and demonstrates why fine-tuning is necessary. A general-purpose model with prompting alone doesn't achieve the desired consistency.

### 4. Manual Cleanup Transcript
**Directory:** `dataset/data/manual-cleanups/`
**Created by:** Human editor (Daniel)
**Role in Fine-Tuning:** GROUND TRUTH TARGET (what the model should learn)

This is the **gold standard** that the fine-tuned model should learn to reproduce:
- Filler words removed appropriately
- False starts cleaned up
- Natural tone preserved
- Meaning maintained
- Consistent cleanup philosophy applied

**Example characteristics:**
- "Over the course of the past year, during which I have worked with AI systems very extensively, my development method has come to be shaped by using them."
- ~859 words for Sample 1 (cleaned from 911 original)
- Demonstrates the "Goldilocks" level - not too much, not too little

**Fine-tuning use:** This is the TARGET OUTPUT that the model learns to produce when given audio input.

## Fine-Tuning Architecture

### Standard Fine-Tuning Approach

```
INPUT:  Audio file (MP3)
         ↓
    [Audio Encoder]
         ↓
    [Fine-tuned Model]
         ↓
OUTPUT: Manual cleanup style text
```

**Training pairs:**
- Audio file → Manual cleanup transcript

**Loss calculation:**
- Compare model output to manual cleanup transcript
- Adjust weights to minimize difference

### Alternative: Multi-Reference Fine-Tuning

Some approaches might use additional references:

```
INPUT:  Audio file + Whisper transcript
         ↓
    [Fine-tuned Model]
         ↓
OUTPUT: Manual cleanup style text
```

This could help the model learn the transformation from verbatim → cleaned.

## Dataset Statistics Example (Sample 1)

| Component | Word Count | Reduction | Purpose |
|-----------|------------|-----------|---------|
| Audio | 367s duration | - | Model input |
| Whisper | 911 words | 0% | Baseline |
| Auto cleanup | 891 words | -2.2% | Shows guided attempt |
| Manual cleanup | 859 words | -5.7% | Training target |

## Training Data Format

For Hugging Face fine-tuning (audio-text-to-text task), each sample becomes:

```json
{
  "audio": "path/to/audio/1.mp3",
  "text": "Over the course of the past year, during which I have worked with AI systems very extensively..."
}
```

Where:
- `audio`: Path to audio file
- `text`: Content from manual cleanup transcript (the ground truth)

## Summary

**What the model learns:**
"When given audio that sounds like the Whisper transcript, produce text that looks like the manual cleanup transcript."

**Key mapping:**
- 🎵 **Audio files** → Model INPUT
- 📝 **Whisper transcripts** → Baseline reference (not directly used in training)
- 🤖 **Auto cleanup** → Shows why fine-tuning is needed (not directly used in training)
- ✅ **Manual cleanup** → Model TARGET OUTPUT (used in training loss calculation)

The fine-tuning process teaches the model to internalize the cleanup patterns demonstrated in the manual cleanups, so it can apply the same style to new audio without needing explicit prompting.
