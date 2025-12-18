#!/usr/bin/env python3
"""
Dataset Builder for Text Cleanup Fine-Tuning
Builds and validates the fine-tuning dataset with comprehensive metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class DatasetBuilder:
    """Build and manage the fine-tuning dataset"""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.dataset_dir = self.base_dir / "dataset"
        self.questions_file = self.dataset_dir / "questions.json"
        self.dataset_file = self.dataset_dir / "dataset.json"
        self.audio_dir = self.dataset_dir / "data" / "audio"
        self.whisper_dir = self.dataset_dir / "data" / "whisper-transcripts"
        self.auto_cleanup_dir = self.dataset_dir / "data" / "auto-cleanup"
        self.manual_cleanup_dir = self.dataset_dir / "data" / "manual-cleanups"

    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    def get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file"""
        if not file_path.exists():
            return None
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]

    def read_text_file(self, file_path: Path) -> Optional[str]:
        """Read text file and return contents"""
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def get_audio_duration(self, audio_path: Path) -> Optional[float]:
        """Get audio duration in seconds"""
        try:
            import soundfile as sf
            if audio_path.exists():
                data, samplerate = sf.read(audio_path)
                return len(data) / samplerate
        except Exception:
            return None
        return None

    def build_sample_metadata(self, question_data: Dict) -> Dict:
        """Build comprehensive metadata for a single sample"""
        uuid = question_data['uuid']
        number = question_data['number']

        # File paths - check both UUID and numeric naming
        audio_path = self.audio_dir / f"{uuid}.wav"
        if not audio_path.exists():
            audio_path = self.audio_dir / f"{number}.wav"
        if not audio_path.exists():
            audio_path = self.audio_dir / f"{number}.mp3"

        whisper_path = self.whisper_dir / f"{uuid}.txt"
        if not whisper_path.exists():
            whisper_path = self.whisper_dir / f"{number}.txt"

        auto_cleanup_path = self.auto_cleanup_dir / f"{uuid}.txt"
        if not auto_cleanup_path.exists():
            auto_cleanup_path = self.auto_cleanup_dir / f"{number}.txt"

        manual_cleanup_path = self.manual_cleanup_dir / f"{uuid}.txt"
        if not manual_cleanup_path.exists():
            manual_cleanup_path = self.manual_cleanup_dir / f"{number}.txt"

        # Read text contents
        whisper_text = self.read_text_file(whisper_path)
        auto_cleanup_text = self.read_text_file(auto_cleanup_path)
        manual_cleanup_text = self.read_text_file(manual_cleanup_path)

        # Build sample metadata
        sample = {
            "id": uuid,
            "sample_number": number,
            "question": question_data['question'],
            "recorded": question_data.get('recorded', False),

            # File paths (relative)
            "files": {
                "audio": str(audio_path.relative_to(self.base_dir)) if audio_path.exists() else None,
                "whisper_transcript": str(whisper_path.relative_to(self.base_dir)) if whisper_path.exists() else None,
                "auto_cleanup": str(auto_cleanup_path.relative_to(self.base_dir)) if auto_cleanup_path.exists() else None,
                "manual_cleanup": str(manual_cleanup_path.relative_to(self.base_dir)) if manual_cleanup_path.exists() else None,
            },

            # Audio metadata
            "audio_metadata": {
                "duration_seconds": self.get_audio_duration(audio_path) if audio_path.exists() else None,
                "format": audio_path.suffix[1:] if audio_path.exists() else None,
                "sample_rate": 44100,
            } if audio_path.exists() else None,

            # Text statistics
            "text_statistics": {
                "whisper_word_count": self.count_words(whisper_text) if whisper_text else None,
                "auto_cleanup_word_count": self.count_words(auto_cleanup_text) if auto_cleanup_text else None,
                "manual_cleanup_word_count": self.count_words(manual_cleanup_text) if manual_cleanup_text else None,
            },

            # Model information
            "models": {
                "transcription": "openai/whisper-1",
                "auto_cleanup": os.getenv("TEXT_CLEANUP_VALIDATION_MODEL", "google/gemini-2.5-flash"),
            },

            # Processing status
            "status": {
                "has_audio": audio_path.exists(),
                "has_whisper_transcript": whisper_path.exists() and bool(whisper_text),
                "has_auto_cleanup": auto_cleanup_path.exists() and bool(auto_cleanup_text),
                "has_manual_cleanup": manual_cleanup_path.exists() and bool(manual_cleanup_text),
                "is_complete": all([
                    audio_path.exists(),
                    whisper_path.exists() and bool(whisper_text),
                    manual_cleanup_path.exists() and bool(manual_cleanup_text),
                ])
            },

            # Content (only if exists)
            "content": {}
        }

        # Add content if available
        if whisper_text:
            sample["content"]["whisper_transcript"] = whisper_text
        if auto_cleanup_text:
            sample["content"]["auto_cleanup"] = auto_cleanup_text
        if manual_cleanup_text:
            sample["content"]["manual_cleanup"] = manual_cleanup_text

        return sample

    def build_dataset(self) -> Dict:
        """Build complete dataset metadata"""
        # Load questions
        if not self.questions_file.exists():
            raise FileNotFoundError(f"Questions file not found: {self.questions_file}")

        with open(self.questions_file, 'r') as f:
            questions = json.load(f)

        # Build samples
        samples = []
        for question_data in questions:
            sample = self.build_sample_metadata(question_data)
            samples.append(sample)

        # Calculate statistics
        total_samples = len(samples)
        completed_samples = sum(1 for s in samples if s['status']['is_complete'])
        recorded_samples = sum(1 for s in samples if s['recorded'])

        # Build dataset metadata
        dataset = {
            "metadata": {
                "name": "Text Cleanup Fine-Tuning Dataset",
                "description": "Dataset for fine-tuning speech-to-text cleanup models",
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "author": "Daniel Rosehill",
                "license": "Private",
            },

            "statistics": {
                "total_samples": total_samples,
                "recorded_samples": recorded_samples,
                "completed_samples": completed_samples,
                "completion_percentage": (completed_samples / total_samples * 100) if total_samples > 0 else 0,
            },

            "configuration": {
                "transcription_model": "openai/whisper-1",
                "cleanup_model": os.getenv("TEXT_CLEANUP_VALIDATION_MODEL", "google/gemini-2.5-flash"),
                "audio_format": "wav",
                "audio_sample_rate": 44100,
            },

            "samples": samples
        }

        return dataset

    def save_dataset(self, dataset: Dict = None):
        """Save dataset to JSON file"""
        if dataset is None:
            dataset = self.build_dataset()

        with open(self.dataset_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"✓ Dataset saved: {self.dataset_file}")
        return dataset

    def validate_dataset(self, dataset: Dict = None) -> Dict:
        """Validate dataset and return validation report"""
        if dataset is None:
            dataset = self.build_dataset()

        report = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "samples": []
        }

        for sample in dataset['samples']:
            sample_report = {
                "sample_number": sample['sample_number'],
                "id": sample['id'],
                "errors": [],
                "warnings": []
            }

            # Check required fields
            if not sample['status']['has_audio']:
                sample_report['errors'].append("Missing audio file")
            if not sample['status']['has_whisper_transcript']:
                sample_report['errors'].append("Missing Whisper transcript")
            # Note: auto_cleanup is optional (only sample 1 has it as a reference)
            if not sample['status']['has_manual_cleanup']:
                sample_report['warnings'].append("Missing manual cleanup (ground truth)")

            # Check word counts
            if sample['text_statistics']['manual_cleanup_word_count'] is not None:
                manual_words = sample['text_statistics']['manual_cleanup_word_count']
                if manual_words == 0:
                    sample_report['warnings'].append("Manual cleanup is empty")

            if sample_report['errors']:
                report['valid'] = False
                report['errors'].extend([f"Sample {sample['sample_number']}: {e}" for e in sample_report['errors']])

            if sample_report['warnings']:
                report['warnings'].extend([f"Sample {sample['sample_number']}: {w}" for w in sample_report['warnings']])

            sample_report['valid'] = len(sample_report['errors']) == 0
            report['samples'].append(sample_report)

        return report

    def export_for_training(self, output_format: str = "jsonl") -> Path:
        """Export dataset in training-ready format"""
        dataset = self.build_dataset()

        if output_format == "jsonl":
            output_file = self.base_dir / "dataset_training.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for sample in dataset['samples']:
                    if sample['status']['is_complete']:
                        training_sample = {
                            "input": sample['content']['whisper_transcript'],
                            "output": sample['content']['manual_cleanup'],
                            "metadata": {
                                "sample_id": sample['id'],
                                "sample_number": sample['sample_number'],
                                "question": sample['question'],
                            }
                        }
                        f.write(json.dumps(training_sample, ensure_ascii=False) + '\n')

        elif output_format == "json":
            output_file = self.base_dir / "dataset_training.json"
            training_data = []
            for sample in dataset['samples']:
                if sample['status']['is_complete']:
                    training_sample = {
                        "input": sample['content']['whisper_transcript'],
                        "output": sample['content']['manual_cleanup'],
                        "metadata": {
                            "sample_id": sample['id'],
                            "sample_number": sample['sample_number'],
                            "question": sample['question'],
                        }
                    }
                    training_data.append(training_sample)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        print(f"✓ Training dataset exported: {output_file}")
        return output_file

    def print_summary(self):
        """Print dataset summary"""
        dataset = self.build_dataset()
        stats = dataset['statistics']

        print("\n" + "="*60)
        print("DATASET SUMMARY")
        print("="*60)
        print(f"Total samples: {stats['total_samples']}")
        print(f"Recorded samples: {stats['recorded_samples']}")
        print(f"Completed samples: {stats['completed_samples']}")
        print(f"Completion: {stats['completion_percentage']:.1f}%")
        print()

        # Show sample details
        print("Sample Status:")
        print("-" * 60)
        for sample in dataset['samples']:
            status_str = "✓" if sample['status']['is_complete'] else "○"
            manual_str = "✓" if sample['status']['has_manual_cleanup'] else "✗"
            print(f"  {status_str} Sample {sample['sample_number']:2d}: {sample['question'][:50]}...")
            print(f"     Manual cleanup: {manual_str}")

        print("="*60 + "\n")


def main():
    """Main entry point"""
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    builder = DatasetBuilder()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "build":
            print("Building dataset...")
            dataset = builder.save_dataset()
            print(f"\n✓ Dataset built with {len(dataset['samples'])} samples")
            builder.print_summary()

        elif command == "validate":
            print("Validating dataset...")
            report = builder.validate_dataset()

            print("\nValidation Report:")
            print("-" * 60)
            print(f"Valid: {report['valid']}")

            if report['errors']:
                print(f"\nErrors ({len(report['errors'])}):")
                for error in report['errors']:
                    print(f"  ✗ {error}")

            if report['warnings']:
                print(f"\nWarnings ({len(report['warnings'])}):")
                for warning in report['warnings']:
                    print(f"  ⚠ {warning}")

            if not report['errors'] and not report['warnings']:
                print("  ✓ No issues found!")

        elif command == "export":
            output_format = sys.argv[2] if len(sys.argv) > 2 else "jsonl"
            print(f"Exporting dataset in {output_format} format...")
            builder.export_for_training(output_format)

        elif command == "summary":
            builder.print_summary()

        else:
            print(f"Unknown command: {command}")
            print_usage()

    else:
        print_usage()


def print_usage():
    """Print usage information"""
    print("\nUsage: python dataset_builder.py <command>")
    print("\nCommands:")
    print("  build     - Build and save dataset.json")
    print("  validate  - Validate dataset completeness")
    print("  export    - Export training-ready dataset (json or jsonl)")
    print("  summary   - Print dataset summary")
    print("\nExamples:")
    print("  python dataset_builder.py build")
    print("  python dataset_builder.py validate")
    print("  python dataset_builder.py export jsonl")
    print("  python dataset_builder.py summary")


if __name__ == "__main__":
    main()
