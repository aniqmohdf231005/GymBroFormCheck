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
from src.physics.classifier import process_video_csv, generate_set_summary
from src.analysis.dtw_engine import compare_to_reference
from src.ai.coach import generate_feedback

def render_html(html_str):
    # Clean up leading/trailing spaces on each line to prevent Markdown from interpreting indented HTML as code blocks
    clean_html = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(clean_html, unsafe_allow_html=True)

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

        lift_selection = st.selectbox("Select Lift Type", ["squat", "bench", "deadlift"])

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
            
            # FIXED THE ALIGNMENT HERE
            st.subheader("🧠 Gym Bro AI Form Analysis")
            
            with st.spinner("Analyzing joint kinematics and tempo..."):
                try:
                    # 1. Run Biomechanical Physics Engine
                    timeline_report = process_video_csv(result.smoothed_csv, lift_type=lift_selection)
                    final_summary = generate_set_summary(timeline_report, lift_type=lift_selection)
                    
                    # 2. Run Temporal DTW Engine
                    dtw_result = compare_to_reference(result.smoothed_csv, lift_type=lift_selection)
                    
                except Exception as e:
                    st.error(f"Kinematic Extraction Error: {e}")
                    st.stop()
            
            # 3. Fetch Coaching Feedback from OpenRouter
            with st.spinner("🤖 Gym Bro Coach is reviewing your video..."):
                try:
                    coaching_report = generate_feedback(final_summary, dtw_result, lift_selection)
                except Exception as e:
                    coaching_report = f"Sorry, there was a minor error in generating your coaching report: {e}"

            # 4. Display Premium AI Coach Card
            render_html(
                f"""
                <div class="coach-card">
                    <div class="coach-header">
                        <div class="coach-avatar">💪</div>
                        <div>
                            <div class="coach-title">Gym Bro AI Coach</div>
                            <div class="coach-subtitle">OpenRouter Powered Kinematic Analysis</div>
                        </div>
                    </div>
                    <p class="coach-feedback">"{coaching_report}"</p>
                </div>
                """
            )

            # 5. Display Clean Metrics Grid
            st.markdown("### 📊 Kinematic & Temporal Metrics")
            
            if "error" not in final_summary:
                metrics_html = '<div class="metrics-grid">'
                
                # Render specific lift metrics
                if lift_selection == "squat":
                    knee_angle = final_summary.get("deepest_knee_angle", 0.0)
                    torso_lean = final_summary.get("max_torso_lean_at_bottom", 0.0)
                    depth_ok = final_summary.get("hit_depth", False)
                    lean_ok = torso_lean <= 45.0
                    
                    depth_class = "status-optimal" if depth_ok else "status-deviation"
                    depth_txt = "Optimal Depth" if depth_ok else "Shallow Depth"
                    
                    lean_class = "status-optimal" if lean_ok else "status-deviation"
                    lean_txt = "Optimal Posture" if lean_ok else "Excessive Lean"
                    
                    metrics_html += f"""
                        <div class="metric-item">
                            <div class="metric-label">Deepest Knee Angle</div>
                            <div class="metric-value">{knee_angle:.1f}°</div>
                            <span class="metric-status {depth_class}">{depth_txt}</span>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Max Torso Lean</div>
                            <div class="metric-value">{torso_lean:.1f}°</div>
                            <span class="metric-status {lean_class}">{lean_txt}</span>
                        </div>
                    """
                elif lift_selection == "bench":
                    elbow_angle = final_summary.get("min_elbow_angle", 0.0)
                    depth_ok = final_summary.get("hit_depth", False)
                    
                    depth_class = "status-optimal" if depth_ok else "status-deviation"
                    depth_txt = "Optimal Depth" if depth_ok else "Shallow Depth"
                    
                    metrics_html += f"""
                        <div class="metric-item">
                            <div class="metric-label">Min Elbow Flexion</div>
                            <div class="metric-value">{elbow_angle:.1f}°</div>
                            <span class="metric-status {depth_class}">{depth_txt}</span>
                        </div>
                    """
                elif lift_selection == "deadlift":
                    hip_ext = final_summary.get("max_hip_extension", 0.0)
                    has_lock = final_summary.get("has_lockout", False)
                    back_warning = final_summary.get("back_rounding_warning", False)
                    
                    lock_class = "status-optimal" if has_lock else "status-deviation"
                    lock_txt = "Fully Locked Out" if has_lock else "Partial Lockout"
                    
                    back_class = "status-deviation" if back_warning else "status-optimal"
                    back_txt = "Back Rounding Alert" if back_warning else "Flat Back (Good)"
                    
                    metrics_html += f"""
                        <div class="metric-item">
                            <div class="metric-label">Max Hip Extension</div>
                            <div class="metric-value">{hip_ext:.1f}°</div>
                            <span class="metric-status {lock_class}">{lock_txt}</span>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Spine & Knee Check</div>
                            <div class="metric-value">{"Warning" if back_warning else "Clean"}</div>
                            <span class="metric-status {back_class}">{back_txt}</span>
                        </div>
                    """
                
                # Render DTW Tempo metrics
                if "error" not in dtw_result:
                    dtw_score = dtw_result.get("dtw_score", 0.0)
                    tempo_label = dtw_result.get("tempo_label", "N/A")
                    speed_ratio = dtw_result.get("speed_ratio", 1.0)
                    
                    # Color class based on dtw score
                    if dtw_score < 20:
                        tempo_class = "status-optimal"
                    elif dtw_score < 45:
                        tempo_class = "status-info"
                    else:
                        tempo_class = "status-deviation"
                        
                    metrics_html += f"""
                        <div class="metric-item">
                            <div class="metric-label">DTW Tempo Score</div>
                            <div class="metric-value">{dtw_score:.2f}</div>
                            <span class="metric-status {tempo_class}">{tempo_label}</span>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Rep Speed Ratio</div>
                            <div class="metric-value">{speed_ratio:.2f}x</div>
                            <span class="metric-status status-info">{"Normal Speed" if 0.5 <= speed_ratio <= 2.0 else "Tempo Issue"}</span>
                        </div>
                    """
                else:
                    metrics_html += f"""
                        <div class="metric-item">
                            <div class="metric-label">Tempo Analysis (DTW)</div>
                            <div class="metric-value">N/A</div>
                            <span class="metric-status status-deviation">Unavailable</span>
                        </div>
                    """
                    
                metrics_html += '</div>'
                render_html(metrics_html)
                
                # Inform about speed warnings if any
                if "error" not in dtw_result and dtw_result.get("speed_warning"):
                    st.warning(f"⚠️ **Tempo Warning:** {dtw_result['speed_warning']}")
            
            else:
                st.warning("Could not extract summary stats for this lift.")

            # Raw Data and Downloads Section
            st.markdown("---")
            with st.expander("📂 View Raw Kinematic Landmark Datasets"):
                preview = pd.read_csv(result.raw_csv).head()
                st.dataframe(preview)

                col1, col2 = st.columns(2)
                with col1:
                    with open(result.raw_csv, "rb") as file:
                        st.download_button(
                            "Download Raw Landmark CSV",
                            file,
                            file_name=os.path.basename(result.raw_csv),
                            mime="text/csv",
                            use_container_width=True
                        )

                with col2:
                    with open(result.smoothed_csv, "rb") as file:
                        st.download_button(
                            "Download Smoothed Landmark CSV",
                            file,
                            file_name=os.path.basename(result.smoothed_csv),
                            mime="text/csv",
                            use_container_width=True
                        )

main()