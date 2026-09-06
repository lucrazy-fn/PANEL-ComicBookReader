"""Descoberta de arquivos da biblioteca local."""
from pathlib import Path
SUPPORTED_EXTENSIONS={".cbz",".cbr",".pdf"}
def scan(folder):
    root=Path(folder)
    return sorted((str(p) for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS),key=str.casefold)
