import os
import uuid
import tempfile


TEMP_AUDIO_DIR = os.path.join(tempfile.gettempdir(), "voiceshield_temp_audio")


def ensure_temp_dir() -> str:
    """
    Ensure the temporary audio directory exists and return its path.
    """
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    return TEMP_AUDIO_DIR


def generate_temp_filepath(extension: str = ".wav") -> str:
    """
    Generate a unique temporary file path for storing an uploaded/recorded
    audio file during processing. The filename is a random UUID so it
    never collides and never reveals anything about the original file.
    """
    temp_dir = ensure_temp_dir()
    filename = f"{uuid.uuid4().hex}{extension}"
    return os.path.join(temp_dir, filename)


def delete_temp_file(filepath: str) -> None:
    """
    Safely delete a temporary file if it exists. Used to enforce our
    privacy rule: raw audio is never kept longer than needed to run
    the analysis pipeline.
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        # If deletion fails (e.g. file locked), don't crash the request.
        # In production this should be logged for cleanup monitoring.
        pass