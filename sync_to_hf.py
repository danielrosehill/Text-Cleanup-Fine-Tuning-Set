#!/usr/bin/env python3
"""
Sync the dataset folder to Hugging Face dataset repository.
Dataset: https://huggingface.co/datasets/danielrosehill/Transcription-Cleanup-Trainer
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi, upload_folder

# Load environment variables
load_dotenv()

# Configuration
DATASET_REPO = "danielrosehill/Transcription-Cleanup-Trainer"
DATASET_PATH = Path(__file__).parent / "dataset"
HF_TOKEN = os.getenv("HF_CLI")  # Token stored as HF_CLI in .env

def check_prerequisites():
    """Check if all prerequisites are met."""
    if not HF_TOKEN:
        print("❌ Error: HF_CLI token not found in .env file")
        return False

    if not DATASET_PATH.exists():
        print(f"❌ Error: Dataset path does not exist: {DATASET_PATH}")
        return False

    print(f"✓ HF Token found")
    print(f"✓ Dataset path found: {DATASET_PATH}")
    return True

def sync_to_huggingface():
    """Sync dataset folder to Hugging Face."""
    print(f"\n📤 Syncing dataset to Hugging Face...")
    print(f"   Repository: {DATASET_REPO}")
    print(f"   Local path: {DATASET_PATH}")

    try:
        api = HfApi()

        # Upload the entire dataset folder
        result = api.upload_folder(
            folder_path=str(DATASET_PATH),
            repo_id=DATASET_REPO,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message="Sync dataset from local repository",
            ignore_patterns=[".git", "__pycache__", "*.pyc", ".DS_Store"]
        )

        print(f"\n✅ Successfully synced to Hugging Face!")
        print(f"   Dataset URL: https://huggingface.co/datasets/{DATASET_REPO}")
        return True

    except Exception as e:
        print(f"\n❌ Error syncing to Hugging Face: {e}")
        return False

def sync_via_git():
    """Alternative: Sync via git clone and push."""
    print(f"\n🔄 Using git-based sync (workaround for XET/LFS issues)...")

    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        clone_path = Path(tmpdir) / "hf-repo"

        try:
            # Clone the HF dataset repo
            print(f"   Cloning HF repo...")
            os.system(f"git clone https://huggingface.co/datasets/{DATASET_REPO} {clone_path} --quiet")

            # Copy dataset files
            print(f"   Copying dataset files...")
            for item in DATASET_PATH.iterdir():
                if item.name not in ['.git', '__pycache__']:
                    dest = clone_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)

            # Git add, commit, push
            print(f"   Committing changes...")
            os.chdir(clone_path)
            os.system("git add .")
            os.system('git commit -m "Sync dataset from local repository"')

            print(f"   Pushing to HF...")
            os.system(f"git push https://desktopcli:{HF_TOKEN}@huggingface.co/datasets/{DATASET_REPO}")

            print(f"\n✅ Successfully synced via git!")
            print(f"   Dataset URL: https://huggingface.co/datasets/{DATASET_REPO}")
            return True

        except Exception as e:
            print(f"\n❌ Error in git sync: {e}")
            return False

def main():
    """Main function."""
    print("=" * 70)
    print("Hugging Face Dataset Sync")
    print("=" * 70)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Confirm sync
    print(f"\nThis will upload all files from {DATASET_PATH}")
    print(f"to https://huggingface.co/datasets/{DATASET_REPO}")

    response = input("\nContinue? [y/N]: ").strip().lower()
    if response != 'y':
        print("Aborted.")
        sys.exit(0)

    # Try API upload first
    success = sync_to_huggingface()

    # If API fails, try git-based sync
    if not success:
        print("\n⚠️  API upload failed. Trying git-based sync as fallback...")
        success = sync_via_git()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
