import os
from dataclasses import dataclass
from pathlib import Path

import cv2
import pandas as pd

from src.physics.classifier import process_video_csv
from src.vision.processor import smooth_coordinates
from src.vision.tracker import VideoNotSuitableError, extract_pose


LANDMARK_VISIBILITY_THRESHOLD = 0.45
FOOT_VISIBILITY_THRESHOLD = 0.60
BENCH_VISIBILITY_THRESHOLD = 0.80

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

FOOT_LANDMARKS = {27, 28, 29, 30, 31, 32}

SIDE_LANDMARKS = {
    "left": {
        "shoulder": 11,
        "elbow": 13,
        "wrist": 15,
        "hip": 23,
        "knee": 25,
        "ankle": 27,
        "foot": 31,
    },
    "right": {
        "shoulder": 12,
        "elbow": 14,
        "wrist": 16,
        "hip": 24,
        "knee": 26,
        "ankle": 28,
        "foot": 32,
    },
}


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
    visibility = row.get(f"visibility_{index}", 1.0)
    min_visibility = FOOT_VISIBILITY_THRESHOLD if index in FOOT_LANDMARKS else LANDMARK_VISIBILITY_THRESHOLD
    if (
        pd.isna(x)
        or pd.isna(y)
        or pd.isna(visibility)
        or float(visibility) < min_visibility
        or not 0 <= float(x) <= 1
        or not 0 <= float(y) <= 1
    ):
        return None
    return int(float(x) * width), int(float(y) * height)


def _upper_body_point(row, index, width, height):
    x = row.get(f"x_{index}")
    y = row.get(f"y_{index}")
    visibility = row.get(f"visibility_{index}", 0.0)
    if (
        pd.isna(x)
        or pd.isna(y)
        or pd.isna(visibility)
        or float(visibility) < BENCH_VISIBILITY_THRESHOLD
        or not 0 <= float(x) <= 1
        or not 0 <= float(y) <= 1
    ):
        return None
    return int(float(x) * width), int(float(y) * height)


def _distance(point_a, point_b):
    return ((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2) ** 0.5


def _upper_body_chain_is_reliable(points, connections, frame_size):
    width, height = frame_size
    min_segment_length = min(width, height) * 0.08
    min_total_length = min(width, height) * 0.20
    total_length = 0.0

    for start, end in connections:
        if not points.get(start) or not points.get(end):
            return False

        segment_length = _distance(points[start], points[end])
        if segment_length < min_segment_length:
            return False
        total_length += segment_length

    return total_length >= min_total_length


def _visibility(row, index):
    value = row.get(f"visibility_{index}", 0.0)
    if pd.isna(value):
        return 0.0
    return float(value)


def _active_side(row):
    left_score = sum(_visibility(row, index) for index in (11, 13, 15, 23, 25, 27))
    right_score = sum(_visibility(row, index) for index in (12, 14, 16, 24, 26, 28))
    return "left" if left_score >= right_score else "right"


def _active_side_for_video(coordinates, lift_type=None):
    if lift_type == "pullup":
        left_indexes = (11, 13, 15)
        right_indexes = (12, 14, 16)
    else:
        left_indexes = (11, 13, 15, 23, 25, 27)
        right_indexes = (12, 14, 16, 24, 26, 28)

    left_score = sum(coordinates.get(f"visibility_{index}", pd.Series(dtype=float)).mean() for index in left_indexes)
    right_score = sum(coordinates.get(f"visibility_{index}", pd.Series(dtype=float)).mean() for index in right_indexes)
    return "left" if left_score >= right_score else "right"


def _connections_for_lift(row, lift_type, active_side=None):
    side = SIDE_LANDMARKS[active_side or _active_side(row)]

    if lift_type == "pullup":
        return [
            (side["shoulder"], side["elbow"]),
            (side["elbow"], side["wrist"]),
            (side["shoulder"], side["hip"]),
        ]

    return POSE_CONNECTIONS


def _landmarks_for_connections(connections):
    return sorted({index for pair in connections for index in pair})


def _notify(progress_callback, progress, message):
    if progress_callback:
        progress_callback(progress, message)


def _create_video_writer(output_path, fps, frame_size):
    codec_candidates = ("avc1", "H264", "mp4v")

    for codec in codec_candidates:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        if writer.isOpened():
            return writer, codec

        writer.release()
        if Path(output_path).exists():
            Path(output_path).unlink()

    return None, None


def _build_feedback_by_frame(coordinates_csv, lift_type):
    if not lift_type:
        return {}

    try:
        timeline = process_video_csv(coordinates_csv, lift_type=lift_type)
    except Exception:
        return {}

    feedback_by_frame = {}
    for item in timeline:
        try:
            frame_number = int(item["frame_number"])
        except (KeyError, TypeError, ValueError):
            continue
        feedback_by_frame[frame_number] = item

    return feedback_by_frame


def _angle_summary(angles, lift_type):
    if lift_type == "squat":
        return f"Knee: {angles.get('knee_flexion', 0):.1f} deg | Torso lean: {angles.get('torso_lean', 0):.1f} deg"
    if lift_type == "pullup":
        return f"Elbow: {angles.get('elbow_flexion', 0):.1f} deg | Torso: {angles.get('torso_lean', 0):.1f} deg"
    if lift_type == "deadlift":
        return f"Hip extension: {angles.get('hip_extension', 0):.1f} deg | Knee: {angles.get('knee_flexion', 0):.1f} deg"
    return ""


def _wrap_text(text, max_chars):
    words = text.split()
    lines = []
    current = []

    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) > max_chars and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        lines.append(" ".join(current))

    return lines[:2]


def _draw_feedback_overlay(frame, feedback_item, lift_type):
    if not feedback_item:
        return

    coaching = feedback_item.get("feedback", {})
    angles = feedback_item.get("angles", {})
    is_optimal = coaching.get("is_optimal", True)
    cue = coaching.get("primary_cue", "Looking solid.")
    title = "Good form" if is_optimal else "Needs adjustment"
    color = (52, 211, 153) if is_optimal else (0, 165, 255)

    height, width = frame.shape[:2]
    scale = max(0.85, min(width, height) / 720)
    pad = int(18 * scale)
    box_x = pad
    box_y = pad
    box_w = min(width - (pad * 2), int(width * 0.52))
    box_h = int(142 * scale)
    accent_w = max(6, int(7 * scale))

    overlay = frame.copy()
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_w, box_y + box_h), (18, 24, 38), -1)
    cv2.addWeighted(overlay, 0.84, frame, 0.16, 0, frame)
    cv2.rectangle(frame, (box_x, box_y), (box_x + accent_w, box_y + box_h), color, -1)

    cv2.putText(
        frame,
        title,
        (box_x + pad, box_y + int(38 * scale)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.92 * scale,
        color,
        max(2, int(2 * scale)),
        cv2.LINE_AA,
    )

    angle_text = _angle_summary(angles, lift_type)
    if angle_text:
        cv2.putText(
            frame,
            angle_text,
            (box_x + pad, box_y + int(72 * scale)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.66 * scale,
            (226, 232, 240),
            max(1, int(2 * scale)),
            cv2.LINE_AA,
        )

    max_chars = max(26, int(box_w / (12 * scale)))
    for line_index, line in enumerate(_wrap_text(cue, max_chars)):
        cv2.putText(
            frame,
            line,
            (box_x + pad, box_y + int(106 * scale) + (line_index * int(26 * scale))),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.68 * scale,
            (248, 250, 252),
            max(1, int(2 * scale)),
            cv2.LINE_AA,
        )


def render_wireframe_video(input_path, coordinates_csv, output_path, progress_callback=None, lift_type=None):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None
    progress_step = max(1, (total_frames or 100) // 100)
    out, codec = _create_video_writer(output_path, fps, (width, height))
    if out is None:
        cap.release()
        raise RuntimeError("Could not create the processed video output file.")

    coordinates = pd.read_csv(coordinates_csv).set_index("frame")
    active_side = _active_side_for_video(coordinates, lift_type=lift_type)
    feedback_by_frame = _build_feedback_by_frame(coordinates_csv, lift_type)
    frame_number = 0
    _notify(progress_callback, 72, f"Rendering wireframe video with {codec} codec...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number in coordinates.index:
            row = coordinates.loc[frame_number]
            connections = _connections_for_lift(row, lift_type, active_side=active_side)
            landmark_indexes = _landmarks_for_connections(connections)
            points = {
                index: (
                    _upper_body_point(row, index, width, height)
                    if lift_type == "pullup"
                    else _point(row, index, width, height)
                )
                for index in landmark_indexes
            }
            feedback_item = feedback_by_frame.get(frame_number)
            is_optimal = True
            if feedback_item:
                is_optimal = feedback_item.get("feedback", {}).get("is_optimal", True)
            line_color = (52, 211, 153) if is_optimal else (0, 165, 255)

            should_draw_pose = True
            if lift_type == "pullup":
                should_draw_pose = _upper_body_chain_is_reliable(points, connections, (width, height))

            if should_draw_pose:
                for start, end in connections:
                    if points.get(start) and points.get(end):
                        line_thickness = 5 if lift_type == "pullup" else 3
                        cv2.line(frame, points[start], points[end], line_color, line_thickness)

                for point in points.values():
                    if point:
                        radius = 7 if lift_type == "pullup" else 4
                        cv2.circle(frame, point, radius, (0, 180, 255), -1)

            _draw_feedback_overlay(frame, feedback_item, lift_type)

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


def process_video(input_path, progress_callback=None, lift_type=None):
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
    render_wireframe_video(input_path, smoothed_csv, output_path, progress_callback, lift_type=lift_type)

    return VideoProcessingResult(
        output_video=output_path,
        raw_csv=raw_csv,
        smoothed_csv=smoothed_csv,
        frame_count=pose_result["frame_count"],
        detected_frames=pose_result["detected_frames"],
        detection_rate=pose_result["detection_rate"],
    )
