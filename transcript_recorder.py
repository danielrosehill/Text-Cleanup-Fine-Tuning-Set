#!/usr/bin/env python3
"""
Transcript Recorder GUI
A GUI application for recording audio responses to questions and automatically
processing them through Whisper transcription and Gemini cleanup.
"""

import json
import os
import sys
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Import dataset builder
try:
    from dataset_builder import DatasetBuilder
except ImportError:
    DatasetBuilder = None

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
AUDIO_DIR = BASE_DIR / "audio"
WHISPER_DIR = BASE_DIR / "whisper-transcripts"
AUTO_CLEANUP_DIR = BASE_DIR / "auto-cleanup"
MANUAL_CLEANUP_DIR = BASE_DIR / "manual-cleanups"
SYSTEM_PROMPT_FILE = BASE_DIR / "system-prompts" / "cleanup.md"
DATASET_FILE = BASE_DIR / "dataset.json"

# Ensure directories exist
for dir_path in [AUDIO_DIR, WHISPER_DIR, AUTO_CLEANUP_DIR, MANUAL_CLEANUP_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROTUER_API_KEY")  # Note: typo in .env preserved
CLEANUP_MODEL = os.getenv("TEXT_CLEANUP_VALIDATION_MODEL", "google/gemini-2.5-flash")


class AudioRecorder:
    """Handles audio recording functionality"""

    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.stream = None

    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.audio_data = []
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        """Stop recording and return audio data"""
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        return np.concatenate(self.audio_data, axis=0) if self.audio_data else None

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if self.recording:
            self.audio_data.append(indata.copy())

    @staticmethod
    def get_input_devices():
        """Get list of available input devices"""
        devices = sd.query_devices()
        input_devices = []
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((idx, device['name']))
        return input_devices


class TranscriptProcessor:
    """Handles Whisper transcription and Gemini cleanup"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.openrouter_api_key = OPENROUTER_API_KEY

        # Load system prompt
        if SYSTEM_PROMPT_FILE.exists():
            with open(SYSTEM_PROMPT_FILE, 'r') as f:
                self.cleanup_prompt = f.read()
        else:
            self.cleanup_prompt = "Clean up this transcript by removing filler words and improving readability."

    def transcribe_audio(self, audio_path):
        """Transcribe audio using OpenAI Whisper"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        with open(audio_path, 'rb') as audio_file:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript

    def cleanup_transcript(self, transcript_text):
        """Clean up transcript using Gemini via OpenRouter"""
        if not self.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": CLEANUP_MODEL,
                "messages": [
                    {"role": "system", "content": self.cleanup_prompt},
                    {"role": "user", "content": transcript_text}
                ]
            }
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")


class TranscriptRecorderGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Transcript Recorder - Fine-Tuning Dataset Creator")
        self.root.geometry("1000x700")

        self.recorder = AudioRecorder()
        self.processor = TranscriptProcessor()
        self.dataset_builder = DatasetBuilder(BASE_DIR) if DatasetBuilder else None
        self.questions = self.load_questions()
        self.current_question = None
        self.recording = False

        self.setup_ui()
        self.refresh_question_list()

    def load_questions(self):
        """Load questions from JSON file"""
        if QUESTIONS_FILE.exists():
            with open(QUESTIONS_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_questions(self):
        """Save questions to JSON file"""
        with open(QUESTIONS_FILE, 'w') as f:
            json.dump(self.questions, f, indent=2)

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Speech-to-Text Fine-Tuning Dataset Recorder",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=10)

        # Questions list
        questions_frame = ttk.LabelFrame(main_frame, text="Questions", padding="10")
        questions_frame.grid(row=1, column=0, sticky=(N, W, E, S), pady=10)
        questions_frame.columnconfigure(0, weight=1)
        questions_frame.rowconfigure(0, weight=1)

        # Questions tree
        self.questions_tree = ttk.Treeview(
            questions_frame,
            columns=("number", "question", "status"),
            show="tree headings",
            selectmode="browse"
        )
        self.questions_tree.heading("number", text="Q#")
        self.questions_tree.heading("question", text="Question")
        self.questions_tree.heading("status", text="Status")
        self.questions_tree.column("number", width=50)
        self.questions_tree.column("question", width=600)
        self.questions_tree.column("status", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(questions_frame, orient=VERTICAL, command=self.questions_tree.yview)
        self.questions_tree.configure(yscrollcommand=scrollbar.set)

        self.questions_tree.grid(row=0, column=0, sticky=(N, W, E, S))
        scrollbar.grid(row=0, column=1, sticky=(N, S))

        self.questions_tree.bind("<<TreeviewSelect>>", self.on_question_select)

        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, sticky=(W, E), pady=10)

        # Microphone selection
        ttk.Label(control_frame, text="Microphone:").grid(row=0, column=0, padx=5)
        self.mic_var = StringVar()
        self.mic_combo = ttk.Combobox(control_frame, textvariable=self.mic_var, width=40, state="readonly")
        self.refresh_microphones()
        self.mic_combo.grid(row=0, column=1, padx=5)

        ttk.Button(control_frame, text="Refresh Mics", command=self.refresh_microphones).grid(row=0, column=2, padx=5)

        # Record button
        self.record_button = ttk.Button(
            control_frame,
            text="Start Recording",
            command=self.toggle_recording,
            state=DISABLED
        )
        self.record_button.grid(row=0, column=3, padx=20)

        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, sticky=(W, E), pady=10)
        status_frame.columnconfigure(0, weight=1)

        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, wrap=WORD)
        self.status_text.grid(row=0, column=0, sticky=(W, E))

        self.log_status("Application started. Select a question to begin recording.")

    def refresh_microphones(self):
        """Refresh the list of available microphones"""
        devices = AudioRecorder.get_input_devices()
        self.mic_combo['values'] = [f"{idx}: {name}" for idx, name in devices]
        if devices:
            self.mic_combo.current(0)

    def refresh_question_list(self):
        """Refresh the questions treeview"""
        # Clear existing items
        for item in self.questions_tree.get_children():
            self.questions_tree.delete(item)

        # Add questions
        for q in self.questions:
            status = "Recorded ✓" if q['recorded'] else "Not Recorded"
            self.questions_tree.insert(
                "",
                "end",
                iid=q['uuid'],
                values=(q['number'], q['question'][:80] + "...", status)
            )

    def on_question_select(self, event):
        """Handle question selection"""
        selection = self.questions_tree.selection()
        if selection:
            uuid = selection[0]
            self.current_question = next((q for q in self.questions if q['uuid'] == uuid), None)
            if self.current_question:
                self.record_button['state'] = NORMAL
                self.log_status(f"Selected Q{self.current_question['number']}: {self.current_question['question']}")

    def toggle_recording(self):
        """Toggle recording state"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording audio"""
        if not self.current_question:
            messagebox.showerror("Error", "Please select a question first")
            return

        # Get selected microphone
        mic_selection = self.mic_var.get()
        if mic_selection:
            mic_idx = int(mic_selection.split(":")[0])
            sd.default.device = (mic_idx, None)

        self.recording = True
        self.record_button.config(text="Stop Recording")
        self.recorder.start_recording()
        self.log_status("Recording started...")

    def stop_recording(self):
        """Stop recording and process audio"""
        self.recording = False
        self.record_button.config(text="Start Recording", state=DISABLED)

        audio_data = self.recorder.stop_recording()
        if audio_data is None or len(audio_data) == 0:
            messagebox.showerror("Error", "No audio recorded")
            self.record_button['state'] = NORMAL
            return

        self.log_status("Recording stopped. Processing...")

        # Save audio file
        uuid = self.current_question['uuid']
        audio_path = AUDIO_DIR / f"{uuid}.wav"
        sf.write(audio_path, audio_data, self.recorder.sample_rate)
        self.log_status(f"Audio saved: {audio_path.name}")

        # Process in background thread
        threading.Thread(target=self.process_audio, args=(audio_path, uuid), daemon=True).start()

    def process_audio(self, audio_path, uuid):
        """Process audio through Whisper and Gemini"""
        try:
            # Whisper transcription
            self.log_status("Transcribing with Whisper...")
            transcript = self.processor.transcribe_audio(audio_path)

            # Save Whisper transcript
            whisper_path = WHISPER_DIR / f"{uuid}.txt"
            with open(whisper_path, 'w') as f:
                f.write(transcript)
            self.log_status(f"Whisper transcript saved: {whisper_path.name}")

            # Gemini cleanup
            self.log_status("Cleaning up transcript with Gemini...")
            cleaned = self.processor.cleanup_transcript(transcript)

            # Save auto cleanup
            auto_cleanup_path = AUTO_CLEANUP_DIR / f"{uuid}.txt"
            with open(auto_cleanup_path, 'w') as f:
                f.write(cleaned)
            self.log_status(f"Auto cleanup saved: {auto_cleanup_path.name}")

            # Create blank manual cleanup file
            manual_cleanup_path = MANUAL_CLEANUP_DIR / f"{uuid}.txt"
            if not manual_cleanup_path.exists():
                with open(manual_cleanup_path, 'w') as f:
                    f.write("")  # Blank file for manual editing
                self.log_status(f"Blank manual cleanup file created: {manual_cleanup_path.name}")

            # Update question status
            for q in self.questions:
                if q['uuid'] == uuid:
                    q['recorded'] = True
                    q['audio_file'] = str(audio_path)
                    q['whisper_transcript'] = str(whisper_path)
                    q['auto_cleanup'] = str(auto_cleanup_path)
                    q['manual_cleanup'] = str(manual_cleanup_path)
                    break

            self.save_questions()

            # Update dataset metadata
            self.update_dataset()

            self.root.after(0, self.refresh_question_list)
            self.log_status(f"✓ Processing complete for Q{self.current_question['number']}")
            self.log_status(f"✓ Dataset metadata updated")
            self.root.after(0, lambda: self.record_button.config(state=NORMAL))

        except Exception as e:
            error_msg = f"Error processing audio: {str(e)}"
            self.log_status(f"✗ {error_msg}")
            messagebox.showerror("Processing Error", error_msg)
            self.root.after(0, lambda: self.record_button.config(state=NORMAL))

    def update_dataset(self):
        """Update dataset.json with latest metadata"""
        if self.dataset_builder:
            try:
                self.dataset_builder.save_dataset()
            except Exception as e:
                self.log_status(f"Warning: Could not update dataset metadata: {e}")

    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(END, log_message)
        self.status_text.see(END)


def main():
    """Main entry point"""
    root = Tk()
    app = TranscriptRecorderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
