# Helpers for loading CV content from text files.

from pathlib import Path

def load_cv(file_path: str) -> str:
    # Read a CV text file and normalize whitespace.
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(cleaned_lines)

def load_all_cvs(directory_path: str) -> list[tuple[str, str]]:
    # Load every text CV from a directory.
    directory = Path(directory_path)
    if not directory.exists():
        return []

    documents: list[tuple[str, str]] = []
    for path in sorted(directory.glob("*.txt")):
        if path.is_file():
            documents.append((path.name, load_cv(str(path))))
    return documents
