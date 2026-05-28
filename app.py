import streamlit as st
import os
from modules.video_processor import process_video

st.title("Gym Bro Form Check")

uploaded_file = st.file_uploader(
    "Upload Exercise Video",
    type=["mp4"]
)

if uploaded_file is not None:

    upload_path = os.path.join("uploads", uploaded_file.name)

    with open(upload_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("Video uploaded successfully!")

    st.video(upload_path)

    if st.button("Process Video"):

        output_path = process_video(upload_path)

        st.success("Processing complete!")

        st.video(output_path)