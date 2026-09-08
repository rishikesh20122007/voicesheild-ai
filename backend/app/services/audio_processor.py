import librosa
import numpy as np
import soundfile as sf

# Target sample rate all audio is normalized to before feature extraction.
# 16kHz is standard for speech/voice analysis models.
TARGET_SAMPLE_RATE = 16000

MIN_DURATION_SECONDS = 1.0
MAX_DURATION_SECONDS = 60.0


class AudioProcessingError(Exception):
    """Raised when an uploaded audio file cannot be processed."""
    pass


def load_and_preprocess_audio(filepath: str) -> tuple[np.ndarray, int]:
    """
    Load an audio file from disk and preprocess it for analysis:
      1. Load audio (librosa handles WAV, MP3, M4A, FLAC, etc.)
      2. Convert to mono if stereo
      3. Resample to TARGET_SAMPLE_RATE
      4. Trim leading/trailing silence
      5. Validate duration is within acceptable bounds

    Returns:
        (audio_array, sample_rate)

    Raises:
        AudioProcessingError: if the file can't be loaded or fails validation.
    """
    try:
        # sr=TARGET_SAMPLE_RATE resamples during load; mono=True averages channels
        audio, sr = librosa.load(filepath, sr=TARGET_SAMPLE_RATE, mono=True)
    except Exception as exc:
        raise AudioProcessingError(f"Could not read audio file: {exc}") from exc

    if audio is None or len(audio) == 0:
        raise AudioProcessingError("Audio file appears to be empty or corrupted.")

    # Trim leading/trailing silence (top_db controls sensitivity;
    # lower = more aggressive trimming)
    trimmed_audio, _ = librosa.effects.trim(audio, top_db=25)

    if len(trimmed_audio) == 0:
        raise AudioProcessingError("Audio contains no detectable speech/sound.")

    duration = len(trimmed_audio) / sr

    if duration < MIN_DURATION_SECONDS:
        raise AudioProcessingError(
            f"Audio is too short ({duration:.2f}s). Minimum duration is {MIN_DURATION_SECONDS}s."
        )

    if duration > MAX_DURATION_SECONDS:
        raise AudioProcessingError(
            f"Audio is too long ({duration:.2f}s). Maximum duration is {MAX_DURATION_SECONDS}s."
        )

    return trimmed_audio, sr


def get_audio_duration(filepath: str) -> float:
    """
    Quickly get the duration (in seconds) of an audio file without
    fully processing it. Useful for early validation before running
    the full preprocessing pipeline.
    """
    try:
        info = sf.info(filepath)
        return info.frames / info.samplerate
    except Exception:
        # Fall back to librosa if soundfile can't read the format (e.g. some MP3s)
        try:
            duration = librosa.get_duration(path=filepath)
            return duration
        except Exception as exc:
            raise AudioProcessingError(f"Could not determine audio duration: {exc}") from exc