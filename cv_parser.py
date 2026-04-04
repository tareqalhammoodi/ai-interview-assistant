# Helpers for loading CV content from text files.

from pathlib import Path

def load_cv(file_path: str) -> str:
    # Read a CV text file and normalize whitespace. 
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(cleaned_lines)
