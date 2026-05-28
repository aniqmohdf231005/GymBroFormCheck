import cv2
import os

def process_video(input_path):

    cap = cv2.VideoCapture(input_path)

    output_path = os.path.join(
        "outputs",
        "processed.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        cv2.putText(
            frame,
            "Processing...",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        out.write(frame)

    cap.release()
    out.release()

    return output_path