# Text Cleanup Fine-Tuning Dataset Creator

A comprehensive toolkit for creating fine-tuning datasets for speech-to-text cleanup models. This system records audio responses to questions, transcribes them using OpenAI Whisper, performs automated cleanup using Gemini, and provides a framework for creating manually-validated ground truth transcripts for model training.

## Overview

This project helps create high-quality training data for fine-tuning audio multimodal models or text cleanup models to achieve the "Goldilocks" level of transcript cleanup—not too much, not too little, just right.

### The Workflow

```
Audio Recording
      ↓
Whisper Transcription (raw)
      ↓
Gemini Auto-Cleanup
      ↓
Manual Ground Truth (your target)
```

The manual ground truth becomes the training target, showing the model exactly the level of cleanup you want to achieve.

## Directory Structure

```
├── audio/                    # Recorded audio files (UUID.wav)
├── whisper-transcripts/      # Raw Whisper transcriptions (UUID.txt)
├── auto-cleanup/             # Gemini auto-cleanup transcripts (UUID.txt)
├── manual-cleanups/          # Manual ground truth transcripts (UUID.txt)
├── questions/                # Question markdown files (for reference)
├── system-prompts/           # System prompts for cleanup
│   └── cleanup.md           # Cleanup instructions for Gemini
├── questions.json            # Question database with UUIDs and status
├── .env                      # API keys (not in git)
├── requirements.txt          # Python dependencies
├── transcript_recorder.py    # GUI application for recording
└── process_audio.py          # CLI tool for processing existing audio
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure API Keys

Create a [.env](.env) file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENROTUER_API_KEY=your_openrouter_api_key_here
TEXT_CLEANUP_VALIDATION_MODEL=google/gemini-2.5-flash
```

### 3. Customize System Prompt (Optional)

Edit [system-prompts/cleanup.md](system-prompts/cleanup.md) to define how you want Gemini to clean up transcripts. This helps establish a baseline for what "cleanup" means in your workflow.

## Usage

### Option 1: GUI Application (Recommended)

The GUI application provides a complete workflow for recording audio, automatic processing, and tracking progress.

```bash
python transcript_recorder.py
```

**Features:**
- View all questions with recording status
- Select microphone from available input devices
- Record audio responses directly in the app
- Automatic processing pipeline:
  - Whisper transcription
  - Gemini cleanup
  - Blank manual cleanup file creation
- Progress tracking and status logging

**Workflow:**
1. Select a question from the list
2. Choose your microphone
3. Click "Start Recording" and speak your response
4. Click "Stop Recording" when done
5. Wait for automatic processing (Whisper → Gemini)
6. Open the manual cleanup file and create your ground truth transcript

### Option 2: CLI Processing Tool

For processing existing audio files or batch processing:

```bash
python process_audio.py audio/1.mp3
```

This will:
1. Transcribe the audio with Whisper → `whisper-transcripts/1.txt`
2. Clean it up with Gemini → `auto-cleanup/1.txt`
3. Create a blank file → `manual-cleanups/1.txt` (for you to fill)

## Question Management

Questions are stored in [questions.json](questions.json) with UUID-based identification:

```json
{
  "uuid": "a7f3e9d1-8c4b-4e5a-9f2d-1a3b5c7d9e0f",
  "number": 1,
  "question": "Describe your typical workflow...",
  "recorded": false,
  "audio_file": null,
  "whisper_transcript": null,
  "auto_cleanup": null,
  "manual_cleanup": null
}
```

UUIDs ensure consistent file naming across audio, transcripts, and cleanup files.

## Creating Your Training Dataset

### Step 1: Record or Process Audio
Use the GUI app to record or the CLI tool to process existing audio files.

### Step 2: Review Outputs

**Whisper Transcript** ([whisper-transcripts/](whisper-transcripts/))
- Raw transcription with filler words, pauses, and imperfections
- This is your "before" state

**Auto-Cleanup** ([auto-cleanup/](auto-cleanup/))
- Gemini's attempt at cleanup using the system prompt
- Useful as a reference or starting point
- May be too aggressive or not aggressive enough

### Step 3: Create Ground Truth

Open the corresponding file in [manual-cleanups/](manual-cleanups/) and create your ideal transcript:
- Remove filler words (um, uh, like, you know)
- Fix grammar and sentence structure
- Add proper punctuation and paragraph breaks
- Keep the meaning and content intact
- **This becomes your training target**

### Step 4: Prepare Training Data

Your training dataset consists of:
- **Input**: Audio files or Whisper transcripts
- **Target**: Your manual cleanup transcripts

This creates pairs showing the model exactly what transformation you want.

## Example Output Comparison

### Whisper Transcript (Raw)
```
So, the typical way that I would develop software, okay, over the course of
the past year, working with AI agents very extensively, daily and intensively,
my method has kind of come to be shaped by them, which doesn't necessarily mean
that this is my method across the board. Like it's something that...
```

### Auto-Cleanup (Gemini)
```
The typical way that I would develop software, over the course of the past year,
working with AI agents very extensively, daily, and intensively, my method has
come to be shaped by them. This doesn't necessarily mean that this is my method
across the board. It's something that, because I've seen that this is how to get
to success, I've shifted my workflow accordingly.
```

### Manual Ground Truth (Your Target)
```
Over the past year of working extensively with AI agents, my software development
method has been shaped by that experience. This approach is specifically for
AI-assisted development rather than a universal method.

I've gravitated toward using voice for initial project specifications because...
```

## Technical Details

### Audio Recording
- Format: WAV (PCM)
- Sample Rate: 44.1 kHz
- Channels: Mono
- Microphone: User-selectable from available input devices

### API Integrations
- **OpenAI Whisper API**: Speech-to-text transcription
- **OpenRouter (Gemini)**: Text cleanup and improvement
- Both APIs require valid API keys in [.env](.env)

### Processing Pipeline
1. Audio recording → `.wav` file
2. Whisper API → raw transcript `.txt`
3. Gemini API (via OpenRouter) → cleaned transcript `.txt`
4. Manual file creation → blank `.txt` for ground truth

## Tips for Creating Quality Training Data

1. **Be Consistent**: Use the same cleanup style across all manual transcripts
2. **Document Your Rules**: Keep notes on what you remove/keep/change
3. **Review Auto-Cleanup**: Use Gemini's output as a reference, but don't rely on it
4. **Focus on Intent**: Keep the speaker's meaning while improving clarity
5. **Balance Cleanup**: Don't over-polish—maintain natural speech patterns

## Use Cases

- **Fine-tuning multimodal models**: Train models to clean up speech transcripts
- **Dataset creation**: Build training data for custom text cleanup models
- **Transcript standardization**: Establish consistent cleanup rules for your workflow
- **Voice-to-text pipelines**: Improve speech-to-text output quality

## Troubleshooting

### No audio recording
- Check microphone permissions
- Ensure correct microphone is selected
- Try refreshing the microphone list

### API errors
- Verify API keys in [.env](.env)
- Check API quota/billing status
- Ensure internet connection

### Processing failures
- Check audio file format (should be readable by soundfile)
- Verify file paths are correct
- Review status log for error details

## Future Enhancements

- [ ] Batch processing for multiple audio files
- [ ] Export training dataset in common formats (JSONL, CSV)
- [ ] Audio quality metrics and validation
- [ ] Transcript comparison/diff view
- [ ] Automated evaluation metrics
- [ ] Support for additional transcription services

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

**Note**: This is a tool for creating training data. The actual model fine-tuning would happen separately using frameworks like Hugging Face Transformers, OpenAI Fine-Tuning API, or similar platforms.
