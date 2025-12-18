# Quick Start Guide

Get started creating your text cleanup fine-tuning dataset in 5 minutes.

## Prerequisites

- Python 3.8+
- OpenAI API key (for Whisper transcription)
- OpenRouter API key (for Gemini cleanup)

## Setup (2 minutes)

### 1. Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
OPENROTUER_API_KEY=your_openrouter_key_here
TEXT_CLEANUP_VALIDATION_MODEL=google/gemini-2.5-flash
```

## Create Your First Sample (3 minutes)

### 1. Launch the GUI

```bash
python transcript_recorder.py
```

### 2. Record

1. Select question #1 from the list
2. Choose your microphone
3. Click "Start Recording"
4. Answer the question naturally (2-3 minutes)
5. Click "Stop Recording"

The app will automatically:
- Save your audio
- Transcribe with Whisper
- Clean up with Gemini
- Create a blank manual cleanup file

### 3. Create Ground Truth

Open `manual-cleanups/1.txt` and create your ideal cleanup:

**Tips:**
- Remove "um", "uh", "like" filler words
- Fix false starts and repetitions
- Add proper punctuation
- Keep conversational tone
- Don't over-polish

### 4. Build Dataset

```bash
python dataset_builder.py build
```

This creates `dataset.json` with complete metadata.

## View Your Progress

```bash
# See summary
python dataset_builder.py summary

# Validate completeness
python dataset_builder.py validate
```

## Export for Training

When you have multiple complete samples:

```bash
python dataset_builder.py export jsonl
```

This creates `dataset_training.jsonl` ready for fine-tuning.

## Next Steps

- Record more samples (aim for 10-20 minimum)
- Review [WORKFLOW.md](WORKFLOW.md) for detailed workflow
- Read [README.md](README.md) for comprehensive documentation

## Common Issues

**No audio recording?**
- Check microphone permissions
- Select correct device in dropdown

**API errors?**
- Verify API keys in `.env`
- Check internet connection

**Files not found?**
- Run `python dataset_builder.py build`

## Dataset Structure at a Glance

```
Your answer (audio)
    ↓
Whisper transcript (raw with filler words)
    ↓
Gemini cleanup (automated)
    ↓
Manual cleanup (your ground truth) ← This is what you create!
```

The manual cleanup shows the model exactly the cleanup level you want.

## That's It!

You now have:
- ✅ One complete training sample
- ✅ Dataset metadata tracking
- ✅ Validation and export tools

Record 9 more samples and you'll have a solid fine-tuning dataset!

---

For detailed documentation, see [WORKFLOW.md](WORKFLOW.md) and [README.md](README.md).
