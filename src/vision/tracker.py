from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import pandas as pd


LANDMARK_COUNT = 33
MIN_DETECTED_FRAMES = 5
MIN_DETECTION_RATE = 0.2
POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
POSE_MODEL_PATH = Path("data") / "models" / "pose_landmarker_lite.task"


class VideoNotSuitableError(ValueError):
    pass


def _empty_landmark_row(frame_number):
    row = {"frame": frame_number}
    for index in range(LANDMARK_COUNT):
        row[f"x_{index}"] = None
        row[f"y_{index}"] = None
        row[f"z_{index}"] = None
        row[f"visibility_{index}"] = None
    return row


def _ensure_pose_model(model_path=POSE_MODEL_PATH):
    model_path = Path(model_path)
    if model_path.exists():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        urlretrieve(POSE_MODEL_URL, model_path)
    except Exception as exc:
        raise RuntimeError(
            "MediaPipe Tasks needs a pose model file before processing videos. "
            f"Download this file manually: {POSE_MODEL_URL} "
            f"and save it as: {model_path}"
        ) from exc

    return model_path


def _notify(progress_callback, progress, message):
    if progress_callback:
        progress_callback(progress, message)


def _validate_detection_quality(frame_count, detected_frames):
    if frame_count == 0:
        raise VideoNotSuitableError(
            "This video has no readable frames. Please upload another MP4."
        )

    detection_rate = detected_frames / frame_count
    if detected_frames < MIN_DETECTED_FRAMES or detection_rate < MIN_DETECTION_RATE:
        raise VideoNotSuitableError(
            "This video is not suitable for pose processing because the body "
            "was detected in too few frames. Please upload a clearer video "
            "where the full body is visible, the lighting is good, and the "
            "camera is not blocked."
        )


def extract_pose(video_path, output_csv=None, progress_callback=None):
    """Extract MediaPipe pose landmarks from an MP4 and export them to CSV."""
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is not installed in the Python environment running Streamlit. "
            "Run: pip install -r requirements.txt"
        ) from exc

    try:
        from mediapipe.tasks.python.core import base_options
        from mediapipe.tasks.python.vision import pose_landmarker
        from mediapipe.tasks.python.vision.core import image
        from mediapipe.tasks.python.vision.core import vision_task_running_mode
    except ImportError as exc:
        raise RuntimeError(
            "MediaPipe Tasks is not installed in the Python environment running Streamlit. "
            "Run: pip install -r requirements.txt"
        ) from exc

    video_path = Path(video_path)
    output_csv = Path(output_csv or Path("data/outputs") / f"{video_path.stem}_pose_coordinates.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    model_path = _ensure_pose_model()

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None
    rows = []
    frame_number = 0
    detected_frames = 0
    progress_step = max(1, (total_frames or 100) // 100)

    _notify(progress_callback, 0, "Loading pose model...")

    options = pose_landmarker.PoseLandmarkerOptions(
        base_options=base_options.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision_task_running_mode.VisionTaskRunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with pose_landmarker.PoseLandmarker.create_from_options(options) as landmarker:
        _notify(progress_callback, 1, "Extracting pose landmarks...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.ascontiguousarray(rgb_frame)
            mp_image = image.Image(
                image_format=image.ImageFormat.SRGB,
                data=rgb_frame,
            )
            timestamp_ms = int(frame_number * 1000 / fps)
            results = landmarker.detect_for_video(mp_image, timestamp_ms)
            row = _empty_landmark_row(frame_number)

            if results.pose_landmarks and results.pose_landmarks[0]:
                detected_frames += 1
                for index, landmark in enumerate(results.pose_landmarks[0]):
                    row[f"x_{index}"] = landmark.x
                    row[f"y_{index}"] = landmark.y
                    row[f"z_{index}"] = landmark.z
                    row[f"visibility_{index}"] = landmark.visibility

            rows.append(row)
            frame_number += 1
            if total_frames and frame_number % progress_step == 0:
                progress = min(60, int((frame_number / total_frames) * 60))
                _notify(
                    progress_callback,
                    progress,
                    f"Extracting landmarks: {frame_number}/{total_frames} frames",
                )

    cap.release()

    pd.DataFrame(rows).to_csv(output_csv, index=False)
    _validate_detection_quality(frame_number, detected_frames)
    _notify(progress_callback, 60, "Raw landmark CSV exported.")

    return {
        "csv_path": str(output_csv),
        "frame_count": frame_number,
        "detected_frames": detected_frames,
        "detection_rate": detected_frames / frame_number if frame_number else 0,
    }
