import numpy as np
import librosa
from typing import Dict


N_MFCC = 13


class FeatureExtractionError(Exception):
    """Raised when audio features cannot be extracted."""
    pass


def extract_features(audio: np.ndarray, sr: int) -> Dict[str, float]:
    """
    Extract a fixed-size dictionary of numerical audio features from
    a preprocessed audio signal. These features feed into the voice
    detection model and are also useful for basic anomaly checks.

    Each feature is reduced to summary statistics (mean/std) so the
    output is a flat, fixed-length feature vector regardless of
    audio duration.
    """
    try:
        features: Dict[str, float] = {}

        # --- MFCCs (Mel-Frequency Cepstral Coefficients) ---
        # Capture the timbral/spectral envelope of the voice -- one of the
        # most important feature families for distinguishing natural vs
        # synthetic speech.
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
        for i in range(N_MFCC):
            features[f"mfcc_{i+1}_mean"] = float(np.mean(mfccs[i]))
            features[f"mfcc_{i+1}_std"] = float(np.std(mfccs[i]))

        # --- Mel Spectrogram (summarized) ---
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr)
        mel_db = librosa.power_to_db(mel_spec, ref=np.max)
        features["mel_spec_mean"] = float(np.mean(mel_db))
        features["mel_spec_std"] = float(np.std(mel_db))

        # --- Spectral Centroid ---
        # "Brightness" of the sound -- synthetic voices often have
        # unnaturally smooth/consistent spectral centroids.
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        features["spectral_centroid_mean"] = float(np.mean(spectral_centroid))
        features["spectral_centroid_std"] = float(np.std(spectral_centroid))

        # --- Spectral Rolloff ---
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        features["spectral_rolloff_mean"] = float(np.mean(spectral_rolloff))
        features["spectral_rolloff_std"] = float(np.std(spectral_rolloff))

        # --- Zero Crossing Rate ---
        # How often the signal changes sign -- relates to noisiness/pitch.
        zcr = librosa.feature.zero_crossing_rate(audio)
        features["zcr_mean"] = float(np.mean(zcr))
        features["zcr_std"] = float(np.std(zcr))

        # --- RMS Energy ---
        rms = librosa.feature.rms(y=audio)
        features["rms_mean"] = float(np.mean(rms))
        features["rms_std"] = float(np.std(rms))

        # --- Pitch (fundamental frequency) via pyin ---
        # Natural human voices have more pitch variability (jitter/shimmer)
        # than many synthetic voices, which can sound "too smooth."
        try:
            f0, voiced_flag, _ = librosa.pyin(
                audio,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sr,
            )
            voiced_f0 = f0[voiced_flag] if voiced_flag is not None else np.array([])
            if len(voiced_f0) > 0:
                features["pitch_mean"] = float(np.nanmean(voiced_f0))
                features["pitch_std"] = float(np.nanstd(voiced_f0))
            else:
                features["pitch_mean"] = 0.0
                features["pitch_std"] = 0.0
        except Exception:
            # Pitch extraction can occasionally fail on unusual audio;
            # fall back to zeros rather than failing the whole request.
            features["pitch_mean"] = 0.0
            features["pitch_std"] = 0.0

        # --- Duration ---
        features["duration"] = float(len(audio) / sr)

        # --- Spectral Bandwidth (basic prosody-adjacent feature) ---
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        features["spectral_bandwidth_mean"] = float(np.mean(spectral_bandwidth))
        features["spectral_bandwidth_std"] = float(np.std(spectral_bandwidth))

        return features

    except Exception as exc:
        raise FeatureExtractionError(f"Failed to extract audio features: {exc}") from exc


def features_to_vector(features: Dict[str, float]) -> np.ndarray:
    """
    Convert the feature dictionary into a fixed-order numpy vector,
    suitable for feeding into an ML model. Keys are sorted alphabetically
    to guarantee consistent ordering between training and inference.
    """
    sorted_keys = sorted(features.keys())
    return np.array([features[k] for k in sorted_keys], dtype=np.float32)