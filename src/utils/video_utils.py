from pathlib import Path


UPLOAD_DIR = Path("data") / "uploads"


def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR
