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

    def predict(self, audio: np.ndarray, sr: int, features: Dict[str, float]) -> Tuple[float, float]:
        """
        Given the raw audio (unused here -- kept for interface parity with
        MLVoiceDetector) and extracted hand-crafted features, return:
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


import logging
import os

logger = logging.getLogger(__name__)

# Pretrained wav2vec2 model fine-tuned specifically for binary
# real-vs-AI-generated audio classification. Override via the
# VOICE_MODEL_ID environment variable if you want to try a different
# checkpoint without touching code.
DEFAULT_MODEL_ID = "MelodyMachine/Deepfake-audio-detection-V2"


class MLVoiceDetector:
    """
    Real pretrained deepfake-speech detector. Uses a wav2vec2 model that
    has actually been trained on labeled real-vs-synthetic audio,
    unlike BaselineVoiceDetector above.

    Loading the model (downloading + initializing weights) is slow, so
    this class is meant to be instantiated ONCE and reused -- see
    get_voice_detector() below, which caches the instance.
    """

    def __init__(self, model_id: str = None):
        # Imports are local to this method (not top-of-file) so that the
        # rest of the app -- and BaselineVoiceDetector -- can still run
        # even in an environment where `transformers` isn't installed or
        # fails to import for some reason.
        import torch
        from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

        self.torch = torch
        self.model_id = model_id or os.environ.get("VOICE_MODEL_ID", DEFAULT_MODEL_ID)
        self.sample_rate = 16000

        self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_id)
        self.model = AutoModelForAudioClassification.from_pretrained(self.model_id)
        self.model.eval()

        # Figure out which output index means "real/human" and which means
        # "fake/AI-generated" by reading the model's own label names,
        # rather than hardcoding index 0/1 -- different checkpoints order
        # their labels differently, and guessing wrong would silently
        # invert every result.
        id2label = {int(k): str(v).lower() for k, v in self.model.config.id2label.items()}
        self.fake_index = next(
            (idx for idx, label in id2label.items()
             if any(kw in label for kw in ("fake", "spoof", "synthetic", "ai_gen", "generated"))),
            None,
        )
        self.real_index = next(
            (idx for idx, label in id2label.items()
             if any(kw in label for kw in ("real", "bona", "human", "genuine"))),
            None,
        )

        if self.fake_index is None or self.real_index is None or self.fake_index == self.real_index:
            raise VoiceDetectionError(
                f"Could not confidently map model labels to real/fake for "
                f"'{self.model_id}' (labels were: {id2label}). Refusing to "
                f"guess, since a wrong guess would silently invert results."
            )

        self.model_type = "wav2vec2_pretrained"
        self.model_version = self.model_id

    def predict(self, audio: np.ndarray, sr: int, features: Dict[str, float]) -> Tuple[float, float]:
        """
        Runs the actual pretrained model on the raw waveform (this model
        works directly on audio, unlike the baseline's hand-crafted
        features -- `features` is accepted but unused, kept for interface
        parity so callers don't need to know which detector is active).
        """
        try:
            inputs = self.feature_extractor(
                audio, sampling_rate=self.sample_rate, return_tensors="pt"
            )
            with self.torch.no_grad():
                logits = self.model(**inputs).logits
            probs = self.torch.nn.functional.softmax(logits, dim=-1)[0]

            human_probability = float(probs[self.real_index])
            ai_probability = float(probs[self.fake_index])

            # Normalize defensively in case the checkpoint has more than
            # two output classes.
            total = human_probability + ai_probability
            if total > 0:
                human_probability /= total
                ai_probability /= total

            return human_probability, ai_probability
        except Exception as exc:
            raise VoiceDetectionError(f"ML voice detection failed: {exc}") from exc


# Cached singleton so the (slow) model load only happens once per running
# process, not on every request.
_detector_instance = None
_ml_load_failed = False


def get_voice_detector():
    """
    Factory function -- returns the currently active detector.

    Tries to load the real pretrained MLVoiceDetector first. If that
    fails for any reason (no internet access to download weights, not
    enough memory on a constrained hosting tier, missing dependency,
    ambiguous labels, etc.), logs a warning and falls back to the
    transparent heuristic BaselineVoiceDetector so the app keeps working
    rather than crashing every analysis request.
    """
    global _detector_instance, _ml_load_failed

    if _detector_instance is not None:
        return _detector_instance

    if not _ml_load_failed:
        try:
            _detector_instance = MLVoiceDetector()
            logger.info("Loaded pretrained ML voice detector: %s", _detector_instance.model_id)
            return _detector_instance
        except Exception as exc:
            logger.warning(
                "Could not load pretrained voice detection model, "
                "falling back to BaselineVoiceDetector: %s", exc,
            )
            _ml_load_failed = True

    _detector_instance = BaselineVoiceDetector()
    return _detector_instance