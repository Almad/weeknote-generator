from datetime import date, timedelta
import os, os.path
from pathlib import Path

from .generator import generate_weeknote


def generate(argv=None):
    """Main command line entry point"""
    # If there is an override, use it
    if "WEEK" in os.environ:
        week_number = int(os.environ["WEEK"])
        week_day = date(date.today().year, 1, 1) + timedelta(weeks=week_number)
        # We are always making weeknotes from sunday
        today = week_day + timedelta(days=7 - week_day.isoweekday())
    else:
        # If we are slacking, assume we are making notes for last week
        today = date.today()
        if today.isoweekday() < 5:
            today = date.today() - timedelta(days=today.isoweekday())

    year = today.strftime("%Y")
    week = today.strftime("%W")

    weeknote_dir = Path(f"content/notes/{year}")
    weeknote_name = f"week-{week}.md"

    if not weeknote_dir.exists():
        weeknote_path = Path(os.path.curdir) / weeknote_name
    else:
        weeknote_path = weeknote_dir / weeknote_name

    if not weeknote_dir.exists():
        print(
            f"Default post directory {weeknote_dir} doesn't exist, the weekly note will be generated in {weeknote_path}"
        )

    generate_weeknote(weeknote_path, today=today)
