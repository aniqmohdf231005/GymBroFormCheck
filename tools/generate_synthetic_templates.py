"""
Generates synthetic "ideal form" reference templates for squat, deadlift, and bench.
These are based on known biomechanics and serve as placeholders until real reference
videos are processed via tools/make_reference.py.

Run once:
    python tools/generate_synthetic_templates.py
"""

import sys
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "src" / "analysis" / "templates"


def _smooth(sequence):
    """Apply a simple moving average to make the sequence realistic."""
    window = 5
    return np.convolve(sequence, np.ones(window) / window, mode="same")


def squat_reference(frames=90):
    # knee_flexion: standing (170°) → parallel (90°) → standing (170°)
    # Realistic tempo: slow controlled descent, brief pause, drive up
    t = np.linspace(0, np.pi, frames)
    sequence = 170 - 80 * np.sin(t)
    return _smooth(sequence)


def deadlift_reference(frames=80):
    # hip_extension: setup bent over (80°) → lockout standing (170°) → lower (80°)
    t = np.linspace(0, np.pi, frames)
    sequence = 80 + 90 * np.sin(t)
    return _smooth(sequence)


def bench_reference(frames=70):
    # elbow_flexion: arms extended (170°) → bar at chest (90°) → press up (170°)
    t = np.linspace(0, np.pi, frames)
    sequence = 170 - 80 * np.sin(t)
    return _smooth(sequence)


def main():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    lifts = {
        "squat": squat_reference(),
        "deadlift": deadlift_reference(),
        "bench": bench_reference(),
    }

    for lift_type, sequence in lifts.items():
        out_path = TEMPLATES_DIR / f"{lift_type}_reference.npy"
        np.save(str(out_path), sequence)
        print(f"Saved {lift_type} template: {len(sequence)} frames, "
              f"{sequence.min():.1f}° – {sequence.max():.1f}°  →  {out_path}")

    print("\nAll synthetic templates generated.")
    print("Replace them with real templates by running:")
    print("  python tools/make_reference.py <video.mp4> <lift_type>")


if __name__ == "__main__":
    main()
