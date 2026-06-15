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
from src.physics.classifier import process_video_csv, generate_set_summary, detect_lift_type
from src.analysis.dtw_engine import compare_to_reference
from src.ai.coach import generate_feedback
import plotly.express as px

def render_html(html_str):
    # Clean up leading/trailing spaces on each line to prevent Markdown from interpreting indented HTML as code blocks
    clean_html = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(clean_html, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Gym Bro Form Check",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_styles()

    render_html(
        """
        <div class="app-hero">
            <div class="hero-copy">
                <div class="eyebrow">AI-assisted lifting review</div>
                <h1>Gym Bro Form Check</h1>
                <p>Upload a lift, choose the movement, and review a synchronized pose video with frame-level coaching cues and performance metrics.</p>
            </div>
            <div class="hero-panel">
                <div class="hero-stat">
                    <div class="stat-value">3 lifts</div>
                    <div class="stat-label">Squat, deadlift, pull-up</div>
                </div>
                <div class="hero-stat">
                    <div class="stat-value">Pose video</div>
                    <div class="stat-label">Landmarks plus live cues</div>
                </div>
                <div class="hero-stat">
                    <div class="stat-value">AI coach</div>
                    <div class="stat-label">Kinematic feedback</div>
                </div>
            </div>
        </div>
        <div class="workflow">
            <div class="workflow-step"><strong>Upload</strong><span>Add a clear MP4 of your lift.</span></div>
            <div class="workflow-step"><strong>Select</strong><span>Match the analysis to the movement.</span></div>
            <div class="workflow-step"><strong>Review</strong><span>Watch cues and read the coach report.</span></div>
        </div>
        """
    )

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

        render_html('<div class="section-label">Original video</div>')
        st.video(upload_path)

        # Action trigger
        st.write("")
        process_clicked = st.button("Start AI Form Check", use_container_width=True)

        if process_clicked:
            # 1. Custom pulsing loader for Video Processing stage
            loading_placeholder = st.empty()
            loading_placeholder.markdown(
                """
                <div class="loading-container">
                    <div class="loading-pulse"></div>
                    <p class="loading-text">Extracting Pose Landmarks & Smoothing Coordinates...</p>
                    <p class="loading-subtext">Stage 1/3: Computer Vision Tracking</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(progress, message):
                progress_bar.progress(max(0, min(100, int(progress))))
                status_text.write(message)

            try:
                # Perform tracking, smoothing, and automatic lift detection
                result = process_video(upload_path, update_progress, lift_type=None)
                lift_selection = result.detected_lift_type
            except (RuntimeError, ValueError) as error:
                progress_bar.empty()
                status_text.empty()
                loading_placeholder.empty()
                st.error(str(error))
                st.info(
                    "Try another MP4 with the full body visible, brighter lighting, "
                    "and minimal camera shake or obstruction."
                )
                st.stop()

            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()

            # 2. Update pulsing loader for Biomechanics stage
            loading_placeholder.markdown(
                """
                <div class="loading-container">
                    <div class="loading-pulse" style="animation-duration: 1.1s; background-color: #4f8cff; box-shadow: 0 0 15px rgba(79, 140, 255, 0.6);"></div>
                    <p class="loading-text">Analyzing joint angles & temporal DTW alignment...</p>
                    <p class="loading-subtext">Stage 2/3: Biomechanics Engine</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            try:
                # Run Biomechanical Physics Engine
                timeline_report = process_video_csv(result.smoothed_csv, lift_type=lift_selection)
                final_summary = generate_set_summary(timeline_report, lift_type=lift_selection)
                
                # Run Temporal DTW Engine
                dtw_result = compare_to_reference(result.smoothed_csv, lift_type=lift_selection)
            except Exception as e:
                loading_placeholder.empty()
                st.error(f"Kinematic Extraction Error: {e}")
                st.stop()

            # 3. Update pulsing loader for AI Coach stage
            loading_placeholder.markdown(
                """
                <div class="loading-container">
                    <div class="loading-pulse" style="animation-duration: 0.8s; background-color: #fb7185; box-shadow: 0 0 15px rgba(251, 113, 133, 0.6);"></div>
                    <p class="loading-text">Gym Bro AI Coach is analyzing your form...</p>
                    <p class="loading-subtext">Stage 3/3: OpenRouter API Biomechanical Inference</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            try:
                coaching_report = generate_feedback(final_summary, dtw_result, lift_selection)
            except Exception as e:
                coaching_report = f"Sorry, there was a minor error in generating your coaching report: {e}"

            # Remove loading card before rendering layout
            loading_placeholder.empty()

            # Display detection success card
            lift_display_names = {
                "squat": "Squat 🏋️",
                "deadlift": "Deadlift 🏋️",
                "pullup": "Pull-Up 💪"
            }
            detected_name = lift_display_names.get(lift_selection, lift_selection.capitalize())
            st.success(f"Exercise Auto-Detected: **{detected_name}**")

            # 4. REDESIGNED DASHBOARD LAYOUT: Side-by-Side Panels
            col_video, col_report = st.columns([1.1, 0.9])

            with col_video:
                render_html('<div class="section-label">Processed pose video</div>')
                try:
                    with open(result.output_video, "rb") as video_file:
                        processed_video = video_file.read()
                    st.video(processed_video, format="video/mp4")
                    st.download_button(
                        "Download Processed Pose Video",
                        processed_video,
                        file_name=os.path.basename(result.output_video),
                        mime="video/mp4",
                        use_container_width=True
                    )
                except OSError as error:
                    st.warning(f"Processed video could not be displayed: {error}")

                # Display Clean Metrics Grid
                render_html('<div class="section-label">Performance metrics</div>')
                st.markdown("### Kinematic & Temporal Metrics")
                
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
                    elif lift_selection == "pullup":
                        elbow_angle = final_summary.get("min_elbow_angle", 0.0)
                        top_reached = final_summary.get("top_reached", False)
                        
                        depth_class = "status-optimal" if top_reached else "status-deviation"
                        depth_txt = "Strong Top Position" if top_reached else "Needs More Pull"
                        
                        metrics_html += f"""
                            <div class="metric-item">
                                <div class="metric-label">Top Elbow Flexion</div>
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
                    
                    if "error" not in dtw_result and dtw_result.get("speed_warning"):
                        st.warning(f"Tempo Warning: {dtw_result['speed_warning']}")
                else:
                    st.warning("Could not extract summary stats for this lift.")

            with col_report:
                render_html('<div class="section-label">Coach report</div>')
                st.subheader("Gym Bro AI Form Analysis")
                
                # Display Premium AI Coach Card
                render_html(
                    f"""
                    <div class="coach-card">
                        <div class="coach-header">
                            <div class="coach-avatar">AI</div>
                            <div>
                                <div class="coach-title">Gym Bro AI Coach</div>
                                <div class="coach-subtitle">OpenRouter API Powered Kinematic Analysis</div>
                            </div>
                        </div>
                        <p class="coach-feedback">"{coaching_report}"</p>
                    </div>
                    """
                )

                # 5. INTERACTIVE VISUALIZATIONS: Plotly Telemetry Chart
                render_html('<div class="section-label">Joint kinematics telemetry</div>')
                st.markdown("### Joint Angle & Torso Lean Over Time")
                
                angle_keys = {
                    "squat": ("knee_flexion", "Knee Flexion (°)"),
                    "pullup": ("elbow_flexion", "Elbow Flexion (°)"),
                    "deadlift": ("hip_extension", "Hip Extension (°)")
                }
                angle_key, angle_label = angle_keys.get(lift_selection, ("knee_flexion", "Angle (°)"))
                
                try:
                    frames = [f["frame_number"] for f in timeline_report]
                    primary_angles = [f["angles"][angle_key] for f in timeline_report]
                    torso_leans = [f["angles"]["torso_lean"] for f in timeline_report]
                    
                    chart_df = pd.DataFrame({
                        "Frame": frames,
                        angle_label: primary_angles,
                        "Torso Lean (°)": torso_leans
                    })
                    
                    fig = px.line(
                        chart_df,
                        x="Frame",
                        y=[angle_label, "Torso Lean (°)"],
                        labels={"value": "Degrees (°)", "variable": "Metric"},
                        color_discrete_map={
                            angle_label: "#18e6c4",      # Vibrant Cyan
                            "Torso Lean (°)": "#4f8cff"  # Slate Blue
                        }
                    )
                    
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#f8fafc",
                        margin=dict(l=10, r=10, t=10, b=10),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        xaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)"),
                        yaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)"),
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as chart_err:
                    st.warning(f"Could not render Plotly telemetry graph: {chart_err}")

            # Raw Data and Downloads Section
            st.markdown("---")
            with st.expander("View Raw Kinematic Landmark Datasets"):
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
