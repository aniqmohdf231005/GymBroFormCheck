from pathlib import Path

import numpy as np

from src.physics.classifier import process_video_csv

TEMPLATES_DIR = Path(__file__).parent / "templates"

LIFT_PRIMARY_ANGLE = {
    "squat": "knee_flexion",
    "deadlift": "hip_extension",
    "bench": "elbow_flexion",
}


def _load_reference(lift_type):
    path = TEMPLATES_DIR / f"{lift_type}_reference.npy"
    if not path.exists():
        raise FileNotFoundError(
            f"No reference template found for '{lift_type}'. "
            f"Run tools/make_reference.py to generate one, or run "
            f"tools/generate_synthetic_templates.py for a placeholder."
        )
    return np.load(str(path))


def _extract_angle_sequence(csv_path, lift_type):
    timeline = process_video_csv(csv_path, lift_type=lift_type)
    angle_key = LIFT_PRIMARY_ANGLE[lift_type]
    return np.array([frame["angles"][angle_key] for frame in timeline])


def _tempo_label(normalized_score):
    if normalized_score < 20:
        return "Excellent tempo"
    elif normalized_score < 45:
        return "Good tempo"
    elif normalized_score < 75:
        return "Slightly off tempo"
    else:
        return "Tempo needs work"


def _speed_label(speed_ratio):
    """
    DTW is time-warp invariant so it won't catch speed differences on its own.
    This check compares raw frame counts to flag reps that are too slow or too fast.
    speed_ratio = user_frames / reference_frames
    """
    if speed_ratio > 2.0:
        return "Too slow — you held the position too long compared to the reference."
    elif speed_ratio < 0.5:
        return "Too fast — you rushed through the rep compared to the reference."
    return None


def compare_to_reference(smoothed_csv, lift_type="squat"):
    """
    Compares a user's angle sequence to the reference template using DTW.
    Also checks movement speed via frame count ratio.
    Returns a dict with dtw_score, tempo_label, speed_warning, and detail.
    """
    try:
        from fastdtw import fastdtw
        from scipy.spatial.distance import euclidean
    except ImportError:
        return {"error": "fastdtw is not installed. Run: pip install fastdtw"}

    if lift_type not in LIFT_PRIMARY_ANGLE:
        return {"error": f"Unsupported lift type '{lift_type}'. Choose: {list(LIFT_PRIMARY_ANGLE.keys())}"}

    try:
        reference = _load_reference(lift_type)
    except FileNotFoundError as exc:
        return {"error": str(exc)}

    user_sequence = _extract_angle_sequence(smoothed_csv, lift_type)

    if len(user_sequence) == 0:
        return {"error": "No angle data found in the provided CSV."}

    distance, _ = fastdtw(
        user_sequence.reshape(-1, 1),
        reference.reshape(-1, 1),
        dist=euclidean,
    )

    normalized = round(distance / max(len(user_sequence), len(reference)), 2)
    speed_ratio = round(len(user_sequence) / len(reference), 2)
    speed_warning = _speed_label(speed_ratio)

    return {
        "dtw_score": normalized,
        "tempo_label": _tempo_label(normalized),
        "speed_ratio": speed_ratio,
        "speed_warning": speed_warning,
        "angle_tracked": LIFT_PRIMARY_ANGLE[lift_type],
        "user_frames": len(user_sequence),
        "reference_frames": len(reference),
    }
