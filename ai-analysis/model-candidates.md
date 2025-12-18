# Fine-Tuning Model Candidates

## Overview

This document lists audio-text multimodal models that could be fine-tuned on this dataset. The task is **audio-to-text with cleanup**, requiring models that accept audio input and produce text output.

## Required Capabilities

A suitable model must:
1. Accept audio as input modality
2. Generate text as output
3. Support fine-tuning (open weights or fine-tuning API)
4. Handle 2-5 minute audio clips
5. Ideally preserve conversational nuance while learning cleanup patterns

## Model Candidates

### Qwen Audio Series

**Qwen-Audio-7B**
- **Developer**: Alibaba Cloud
- **Parameters**: 7B
- **Input**: Audio + text (multimodal)
- **Output**: Text
- **Fine-tuning**: Open weights, supports LoRA/QLoRA
- **Pros**: Strong audio understanding, relatively lightweight
- **Cons**: May need adaptation for cleanup vs. general transcription
- **HuggingFace**: `Qwen/Qwen-Audio-7B`

**Qwen2-Audio-7B-Instruct**
- **Developer**: Alibaba Cloud
- **Parameters**: 7B
- **Input**: Audio + text
- **Output**: Text
- **Fine-tuning**: Instruction-tuned base, supports fine-tuning
- **Pros**: Better instruction following, good for stylistic tasks
- **HuggingFace**: `Qwen/Qwen2-Audio-7B-Instruct`

### Whisper Series (OpenAI)

**Whisper Large v3**
- **Developer**: OpenAI
- **Parameters**: 1.5B
- **Input**: Audio
- **Output**: Text (transcription)
- **Fine-tuning**: Supports fine-tuning via OpenAI API or local
- **Pros**: Excellent transcription quality, well-documented
- **Cons**: Trained for verbatim transcription, may resist cleanup patterns
- **HuggingFace**: `openai/whisper-large-v3`

**Whisper Medium/Small**
- **Parameters**: 769M / 244M
- **Pros**: Lighter weight, faster inference
- **Cons**: Lower base accuracy than Large
- **Use case**: Good for testing fine-tuning approach before scaling

### Distil-Whisper

**distil-whisper/distil-large-v3**
- **Developer**: Hugging Face (distilled from Whisper)
- **Parameters**: ~750M (distilled from 1.5B)
- **Pros**: 6x faster inference, similar quality to Whisper Large
- **Fine-tuning**: Fully open, easier to fine-tune locally
- **HuggingFace**: `distil-whisper/distil-large-v3`

### SALMONN

**SALMONN-7B**
- **Developer**: Tsinghua University / ByteDance
- **Parameters**: 7B
- **Input**: Audio + text (speech and audio events)
- **Output**: Text
- **Fine-tuning**: Open weights
- **Pros**: Strong audio understanding beyond speech
- **Cons**: May be overkill for speech-only task

### Seamless Models (Meta)

**seamless-m4t-v2-large**
- **Developer**: Meta
- **Parameters**: Large (exact varies by component)
- **Input**: Audio + text (multilingual)
- **Output**: Text, audio
- **Fine-tuning**: Open weights
- **Pros**: Multilingual, strong audio processing
- **Cons**: Complex architecture, designed for translation

### Speech-to-Text Specific

**wav2vec2-bert-2.0**
- **Developer**: Meta
- **Input**: Audio waveform
- **Output**: Text (via fine-tuning)
- **Fine-tuning**: Designed to be fine-tuned
- **Pros**: Strong speech representation learning
- **Cons**: Requires more fine-tuning infrastructure

## Placeholder Models to Research

- **Voxtral** (mentioned as "Voxdrill for Mistro") - needs verification
- **Gemini Audio models** (if they release fine-tunable versions)
- **AudioGPT variants**
- **LTU (Language Transformer with Universal audio)** series

## Recommended Starting Points

### Option 1: Whisper Large v3 (Conservative)
- **Why**: Proven transcription quality, well-documented fine-tuning
- **Risk**: May resist learning cleanup patterns (trained for verbatim)
- **Best for**: If you want to fine-tune on top of best-in-class ASR

### Option 2: Qwen2-Audio-7B-Instruct (Recommended)
- **Why**: Instruction-tuned, designed for flexible audio-to-text tasks
- **Risk**: Less common than Whisper, fewer community examples
- **Best for**: Learning cleanup patterns as a stylistic instruction

### Option 3: Distil-Whisper (Practical)
- **Why**: Lighter weight, faster iteration during development
- **Risk**: Slightly lower base accuracy
- **Best for**: Rapid experimentation and testing

## Fine-Tuning Approaches

### Full Fine-Tuning
- Update all model weights
- Requires significant compute
- Best quality if you have resources

### LoRA (Low-Rank Adaptation)
- Fine-tune only adapter layers
- Much lower compute requirement
- Good balance of quality and practicality
- **Recommended approach**

### QLoRA (Quantized LoRA)
- LoRA with quantization
- Can fine-tune 7B models on consumer GPUs
- Slight quality tradeoff for accessibility

## Hardware Considerations

Based on AMD Radeon RX 7700 XT (12GB VRAM):

- **Whisper Large v3**: Feasible with QLoRA
- **Qwen Audio 7B**: Feasible with QLoRA, tight on memory
- **Distil-Whisper**: Comfortable with LoRA or QLoRA
- **Smaller Whisper models**: Full fine-tuning possible

**Recommendation**: Start with QLoRA approach for 7B models, or full LoRA for Whisper/Distil-Whisper.

## Next Steps

1. Select 1-2 candidate models for initial experiments
2. Test base model performance on Sample 1 (before fine-tuning)
3. Fine-tune on 10 samples to validate approach
4. Scale to 50-300 samples based on results

## Resources Needed

- [ ] Verify Voxtral/Voxdrill model details
- [ ] Test base model inference on Sample 1
- [ ] Set up fine-tuning environment (Hugging Face Transformers + PEFT)
- [ ] Calculate VRAM requirements for each model
- [ ] Research ROCm compatibility for each model
