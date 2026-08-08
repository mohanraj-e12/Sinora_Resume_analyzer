import os
import re

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def sanitize_filename(filename: str) -> str:
    # Keep alphanumeric, dots, underscores, hyphens
    clean = re.sub(r"[^\w\.-]", "_", filename)
    return clean
