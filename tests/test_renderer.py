import cv2
import numpy as np
import pandas as pd

from src.utils.renderer import render_wireframe_video


def test_render_wireframe_video_creates_readable_mp4(tmp_path):
    input_video = tmp_path / "input.mp4"
    coordinates_csv = tmp_path / "coordinates.csv"
    output_video = tmp_path / "output.mp4"

    writer = cv2.VideoWriter(
        str(input_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10,
        (64, 64),
    )
    assert writer.isOpened()
    for _ in range(3):
        writer.write(np.zeros((64, 64, 3), dtype="uint8"))
    writer.release()

    rows = []
    for frame in range(3):
        row = {"frame": frame}
        for index in range(33):
            row[f"x_{index}"] = 0.5
            row[f"y_{index}"] = 0.5
        rows.append(row)
    pd.DataFrame(rows).to_csv(coordinates_csv, index=False)

    render_wireframe_video(str(input_video), str(coordinates_csv), str(output_video))

    assert output_video.exists()
    cap = cv2.VideoCapture(str(output_video))
    assert cap.isOpened()
    ok, _ = cap.read()
    cap.release()
    assert ok
