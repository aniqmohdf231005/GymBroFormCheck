import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.renderer import process_video
from styles import apply_styles


def main():
    apply_styles()

    st.title("Gym Bro Form Check")

    uploaded_file = st.file_uploader(
        "Upload Exercise Video",
        type=["mp4"]
    )

    if uploaded_file is not None:

        os.makedirs("data/uploads", exist_ok=True)

        upload_path = os.path.join("data", "uploads", uploaded_file.name)

        with open(upload_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("Video uploaded successfully!")

        st.video(upload_path)

        if st.button("Process Video"):

            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(progress, message):
                progress_bar.progress(max(0, min(100, int(progress))))
                status_text.write(message)

            try:
                result = process_video(upload_path, update_progress)
            except (RuntimeError, ValueError) as error:
                progress_bar.empty()
                status_text.empty()
                st.error(str(error))
                st.info(
                    "Try another MP4 with the full body visible, brighter lighting, "
                    "and minimal camera shake or obstruction."
                )
                st.stop()

            progress_bar.progress(100)
            status_text.write("Processing complete.")

            st.success("Processing complete!")

            st.video(result.output_video)

            st.subheader("Video Processing Result")
            st.write(
                f"Detected pose landmarks in {result.detected_frames} of "
                f"{result.frame_count} frames ({result.detection_rate:.0%})."
            )

            preview = pd.read_csv(result.raw_csv).head()
            st.dataframe(preview)

            with open(result.raw_csv, "rb") as file:
                st.download_button(
                    "Download raw landmark CSV",
                    file,
                    file_name=os.path.basename(result.raw_csv),
                    mime="text/csv",
                )

            with open(result.smoothed_csv, "rb") as file:
                st.download_button(
                    "Download smoothed landmark CSV",
                    file,
                    file_name=os.path.basename(result.smoothed_csv),
                    mime="text/csv",
                )


main()
