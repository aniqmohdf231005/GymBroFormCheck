import os
from dataclasses import dataclass
from pathlib import Path

import cv2
import pandas as pd

from src.vision.processor import smooth_coordinates
from src.vision.tracker import VideoNotSuitableError, extract_pose


POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15),
    (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20),
    (16, 22), (18, 20), (11, 23), (12, 24),
    (23, 24), (23, 25), (24, 26), (25, 27),
    (26, 28), (27, 29), (28, 30), (29, 31),
    (30, 32), (27, 31), (28, 32),
]


@dataclass
class VideoProcessingResult:
    output_video: str
    raw_csv: str
    smoothed_csv: str
    frame_count: int
    detected_frames: int
    detection_rate: float


def _safe_stem(path):
    return "".join(char if char.isalnum() else "_" for char in Path(path).stem)


def _point(row, index, width, height):
    x = row.get(f"x_{index}")
    y = row.get(f"y_{index}")
    if pd.isna(x) or pd.isna(y):
        return None
    return int(float(x) * width), int(float(y) * height)


def _notify(progress_callback, progress, message):
    if progress_callback:
        progress_callback(progress, message)


def render_wireframe_video(input_path, coordinates_csv, output_path, progress_callback=None):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None
    progress_step = max(1, (total_frames or 100) // 100)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    if not out.isOpened():
        cap.release()
        raise RuntimeError("Could not create the processed video output file.")

    coordinates = pd.read_csv(coordinates_csv).set_index("frame")
    frame_number = 0
    _notify(progress_callback, 72, "Rendering wireframe video...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number in coordinates.index:
            row = coordinates.loc[frame_number]
            points = {index: _point(row, index, width, height) for index in range(33)}

            for start, end in POSE_CONNECTIONS:
                if points[start] and points[end]:
                    cv2.line(frame, points[start], points[end], (0, 255, 0), 3)

            for point in points.values():
                if point:
                    cv2.circle(frame, point, 4, (0, 180, 255), -1)

        out.write(frame)
        frame_number += 1
        if total_frames and frame_number % progress_step == 0:
            progress = 70 + min(30, int((frame_number / total_frames) * 30))
            _notify(
                progress_callback,
                progress,
                f"Rendering wireframe: {frame_number}/{total_frames} frames",
            )

    cap.release()
    out.release()
    _notify(progress_callback, 100, "Wireframe video ready.")

    return output_path


def process_video(input_path, progress_callback=None):
    os.makedirs("data/outputs", exist_ok=True)
    stem = _safe_stem(input_path)

    raw_csv = os.path.join("data", "outputs", f"{stem}_pose_coordinates.csv")
    smoothed_csv = os.path.join("data", "outputs", f"{stem}_smoothed_pose_coordinates.csv")
    output_path = os.path.join("data", "outputs", f"{stem}_wireframe.mp4")

    _notify(progress_callback, 0, "Starting video processing...")
    try:
        pose_result = extract_pose(input_path, raw_csv, progress_callback)
    except VideoNotSuitableError:
        raise

    smooth_coordinates(raw_csv, smoothed_csv, progress_callback=progress_callback)
    render_wireframe_video(input_path, smoothed_csv, output_path, progress_callback)

    return VideoProcessingResult(
        output_video=output_path,
        raw_csv=raw_csv,
        smoothed_csv=smoothed_csv,
        frame_count=pose_result["frame_count"],
        detected_frames=pose_result["detected_frames"],
        detection_rate=pose_result["detection_rate"],
    )
