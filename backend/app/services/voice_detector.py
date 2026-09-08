import numpy as np
from typing import Dict, Tuple


class VoiceDetectionError(Exception):
    """Raised when voice detection fails to run."""
    pass


class BaselineVoiceDetector:
    """
    A transparent, rule-based BASELINE detector.

    IMPORTANT — READ THIS:
    This is NOT a trained machine learning classifier. It is a heuristic
    scorer based on acoustic properties that research literature associates
    with synthetic speech (unnaturally low pitch variability, overly smooth
    spectral characteristics, unusually consistent energy). It has NOT been
    trained or evaluated on a labeled real-vs-synthetic voice dataset, and
    its accuracy is NOT validated. It exists so the rest of the system
    (risk engine, prevention engine, dashboard, history) can be built and
    tested end-to-end while a properly trained model is developed.

    DO NOT present this model's output as production-grade deepfake
    detection accuracy in any report, demo claim, or documentation.

    To upgrade: implement `MLVoiceDetector` (see stub below) with a real
    trained PyTorch model, and swap it in via `get_voice_detector()` at
    the bottom of this file. The calling code (API routes) never needs
    to change, since both detectors expose the same `predict()` interface.
    """

    def __init__(self):
        self.model_type = "baseline_heuristic"
        self.model_version = "0.1.0-demo"

    def predict(self, features: Dict[str, float]) -> Tuple[float, float]:
        """
        Given extracted audio features, return:
            (human_probability, ai_probability)
        as floats between 0 and 1, summing to 1.0.
        """
        try:
            score = 0.5  # start neutral

            # --- Pitch variability (jitter) ---
            # Natural voices have more pitch variation. Very low pitch_std
            # (relative to pitch_mean) suggests unnaturally smooth/synthetic speech.
            pitch_mean = features.get("pitch_mean", 0.0)
            pitch_std = features.get("pitch_std", 0.0)
            if pitch_mean > 0:
                pitch_variability_ratio = pitch_std / pitch_mean
                if pitch_variability_ratio < 0.02:
                    score -= 0.15  # suspiciously smooth pitch -> lean toward AI
                elif pitch_variability_ratio > 0.08:
                    score += 0.10  # natural jitter -> lean toward human

            # --- Spectral centroid variability ---
            # Overly consistent spectral brightness can indicate synthetic audio.
            centroid_mean = features.get("spectral_centroid_mean", 0.0)
            centroid_std = features.get("spectral_centroid_std", 0.0)
            if centroid_mean > 0:
                centroid_variability_ratio = centroid_std / centroid_mean
                if centroid_variability_ratio < 0.15:
                    score -= 0.10
                elif centroid_variability_ratio > 0.35:
                    score += 0.10

            # --- RMS energy consistency ---
            # Natural speech has dynamic energy (pauses, emphasis). Very
            # uniform energy can suggest synthetic generation.
            rms_mean = features.get("rms_mean", 0.0)
            rms_std = features.get("rms_std", 0.0)
            if rms_mean > 0:
                energy_variability_ratio = rms_std / rms_mean
                if energy_variability_ratio < 0.2:
                    score -= 0.10
                elif energy_variability_ratio > 0.6:
                    score += 0.05

            # --- MFCC std spread (timbral variability) ---
            mfcc_stds = [v for k, v in features.items() if k.startswith("mfcc_") and k.endswith("_std")]
            if mfcc_stds:
                avg_mfcc_std = float(np.mean(mfcc_stds))
                if avg_mfcc_std < 8.0:
                    score -= 0.10
                elif avg_mfcc_std > 20.0:
                    score += 0.05

            # Clamp to valid probability range
            human_probability = float(np.clip(score, 0.02, 0.98))
            ai_probability = 1.0 - human_probability

            return human_probability, ai_probability

        except Exception as exc:
            raise VoiceDetectionError(f"Voice detection failed: {exc}") from exc


class MLVoiceDetector:
    """
    STUB for a future trained ML model (e.g. PyTorch CNN or fine-tuned
    wav2vec2). Not implemented yet -- requires a labeled training dataset.

    When ready, implement:
      - __init__: load trained model weights (torch.load / from_pretrained)
      - predict(features): run real inference and return
        (human_probability, ai_probability)

    This class intentionally raises NotImplementedError so it's impossible
    to accidentally use an untrained/unloaded model in production.
    """

    def __init__(self, model_path: str = None):
        raise NotImplementedError(
            "MLVoiceDetector is not yet implemented. "
            "A trained model checkpoint is required. "
            "Use BaselineVoiceDetector until training data is available."
        )

    def predict(self, features: Dict[str, float]) -> Tuple[float, float]:
        raise NotImplementedError


def get_voice_detector():
    """
    Factory function -- returns the currently active detector.
    Swap this to MLVoiceDetector once a trained model is available,
    and no other code in the project needs to change.
    """
    return BaselineVoiceDetector()