"""
Run this script once per lift type to generate a reference template from a real video.
The template is saved as a .npy file in src/analysis/templates/.

Usage:
    python tools/make_reference.py path/to/video.mp4 squat
    python tools/make_reference.py path/to/video.mp4 deadlift
    python tools/make_reference.py path/to/video.mp4 bench
"""

import sys
import os
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.vision.tracker import extract_pose
from src.vision.processor import smooth_coordinates
from src.physics.classifier import process_video_csv

TEMPLATES_DIR = PROJECT_ROOT / "src" / "analysis" / "templates"

LIFT_PRIMARY_ANGLE = {
    "squat": "knee_flexion",
    "deadlift": "hip_extension",
    "bench": "elbow_flexion",
}


def make_reference(video_path, lift_type):
    if lift_type not in LIFT_PRIMARY_ANGLE:
        print(f"Error: lift_type must be one of {list(LIFT_PRIMARY_ANGLE.keys())}")
        sys.exit(1)

    video_path = Path(video_path)
    if not video_path.exists():
        print(f"Error: video file not found: {video_path}")
        sys.exit(1)

    print(f"Processing '{video_path.name}' as reference for {lift_type}...")

    raw_csv = PROJECT_ROOT / "data" / "outputs" / f"ref_{lift_type}_raw.csv"
    smoothed_csv = PROJECT_ROOT / "data" / "outputs" / f"ref_{lift_type}_smoothed.csv"
    os.makedirs(raw_csv.parent, exist_ok=True)

    print("  Step 1/3: Extracting pose landmarks...")
    extract_pose(str(video_path), str(raw_csv))

    print("  Step 2/3: Smoothing coordinates...")
    smooth_coordinates(str(raw_csv), str(smoothed_csv))

    print("  Step 3/3: Extracting angle sequence...")
    timeline = process_video_csv(str(smoothed_csv), lift_type=lift_type)

    angle_key = LIFT_PRIMARY_ANGLE[lift_type]
    sequence = np.array([frame["angles"][angle_key] for frame in timeline])

    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TEMPLATES_DIR / f"{lift_type}_reference.npy"
    np.save(str(out_path), sequence)

    print(f"\nDone. Template saved to: {out_path}")
    print(f"  Frames captured: {len(sequence)}")
    print(f"  Angle range: {sequence.min():.1f}° – {sequence.max():.1f}°")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tools/make_reference.py <video.mp4> <lift_type>")
        print("  lift_type: squat | deadlift | bench")
        sys.exit(1)

    make_reference(sys.argv[1], sys.argv[2])
