from datetime import date
import os, os.path
from pathlib import Path

from .generator import generate_weeknote

year = date.today().strftime("%Y")
week = date.today().strftime("%W")


def generate(argv=None):
    """Main command line entry point"""
    weeknote_dir = Path(f"content/notes/{year}")
    if not weeknote_dir.exists():
        print(
            f"Default post directory {weeknote_dir} doesn't exist, the weekly note will be generated in the current directory"
        )
        weeknote_dir = Path(os.path.curdir)

    weeknote_path = f"week-{week}.md"

    post_path = weeknote_dir / weeknote_path

    generate_weeknote(post_path)
