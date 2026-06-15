import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.renderer import process_video
from styles import apply_styles
from src.physics.classifier import process_video_csv, generate_set_summary, detect_lift_type
from src.analysis.dtw_engine import compare_to_reference
from src.ai.coach import generate_feedback

def render_html(html_str):
    clean_html = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(clean_html, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Gym Bro AI - Form Check",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_styles()

    # --- Initialize Session State ---
    if 'processing_done' not in st.session_state:
        st.session_state.processing_done = False
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None

    # --- Header Spacer ---
    st.write("")

    # --- File Uploader ---
    uploaded_file = st.file_uploader(
        "Upload Exercise Video (MP4)",
        type=["mp4"]
    )

    # --- Empty State (Hero Section) ---
    if uploaded_file is None:
        # Reset state if user removes file
        st.session_state.processing_done = False
        st.session_state.processed_data = None

        render_html(
            """
            <div class="app-hero" style="margin-top: 20px;">
                <div class="hero-copy">
                    <div class="eyebrow">AI-Assisted Biomechanics</div>
                    <h1>Gym Bro AI Form Check</h1>
                    <p>Upload a video of your lift. Our computer vision engine will automatically detect the exercise, track your spatial coordinates, and an LLM coach will analyze your kinematic data to give you elite-level form corrections.</p>
                </div>
                <div class="hero-panel">
                    <div class="hero-stat">
                        <div class="stat-value">Auto-Detect</div>
                        <div class="stat-label">Squat, deadlift, pull-up</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-value">Computer Vision</div>
                        <div class="stat-label">Frame-by-frame Spatial Tracking</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-value">AI Coach</div>
                        <div class="stat-label">Kinematic & DTW Tempo Feedback</div>
                    </div>
                </div>
            </div>
            """
        )
        return  # Stop execution here until a file is uploaded

    # --- File Uploaded State ---
    os.makedirs("data/uploads", exist_ok=True)
    upload_path = os.path.join("data", "uploads", uploaded_file.name)

    with open(upload_path, "wb") as f:
        f.write(uploaded_file.read())

    # --- Stage 1: Pre-processing (Show Video & Button) ---
    if not st.session_state.processing_done:
        
        col_video, col_action = st.columns([1.5, 1])
        
        with col_video:
            render_html('<div class="section-label">Original Video</div>')
            st.video(upload_path)
            
        with col_action:
            st.write("")
            st.write("")
            st.info("Video successfully loaded. Ready to initialize the computer vision tracking engine.")
            process_clicked = st.button("Initialize AI Form Check", use_container_width=True)

        if process_clicked:
            # Stage 1: Vision Tracking
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
                status_text.write(f"*{message}*")

            try:
                result = process_video(upload_path, update_progress, lift_type=None)
                lift_selection = result.detected_lift_type
            except (RuntimeError, ValueError) as error:
                progress_bar.empty()
                status_text.empty()
                loading_placeholder.empty()
                st.error(str(error))
                st.info("Try another MP4 with the full body visible, brighter lighting, and minimal camera shake.")
                st.stop()

            progress_bar.empty()
            status_text.empty()

            # Stage 2: Biomechanics
            loading_placeholder.markdown(
                """
                <div class="loading-container">
                    <div class="loading-pulse" style="animation-duration: 1.1s; background-color: #4f8cff; box-shadow: 0 0 20px rgba(79, 140, 255, 0.6);"></div>
                    <p class="loading-text">Analyzing joint angles & temporal DTW alignment...</p>
                    <p class="loading-subtext">Stage 2/3: Biomechanics Engine</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            try:
                timeline_report = process_video_csv(result.smoothed_csv, lift_type=lift_selection)
                final_summary = generate_set_summary(timeline_report, lift_type=lift_selection)
                dtw_result = compare_to_reference(result.smoothed_csv, lift_type=lift_selection)
            except Exception as e:
                loading_placeholder.empty()
                st.error(f"Kinematic Extraction Error: {e}")
                st.stop()

            # Stage 3: AI Inference
            loading_placeholder.markdown(
                """
                <div class="loading-container">
                    <div class="loading-pulse" style="animation-duration: 0.8s; background-color: #f59e0b; box-shadow: 0 0 20px rgba(245, 158, 11, 0.6);"></div>
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

            # Save everything to session state to prevent re-running on interaction
            st.session_state.processed_data = {
                "result": result,
                "lift_selection": lift_selection,
                "timeline_report": timeline_report,
                "final_summary": final_summary,
                "dtw_result": dtw_result,
                "coaching_report": coaching_report
            }
            st.session_state.processing_done = True
            
            loading_placeholder.empty()
            st.rerun()

    # --- Stage 2: Results Dashboard ---
    if st.session_state.processing_done:
        data = st.session_state.processed_data
        result = data["result"]
        lift_selection = data["lift_selection"]
        timeline_report = data["timeline_report"]
        final_summary = data["final_summary"]
        dtw_result = data["dtw_result"]
        coaching_report = data["coaching_report"]

        # Success Banner
        lift_display_names = {"squat": "Squat 🏋️", "deadlift": "Deadlift 🏋️", "pullup": "Pull-Up 💪"}
        detected_name = lift_display_names.get(lift_selection, lift_selection.capitalize())
        
        st.success(f"**Exercise Auto-Detected:** {detected_name}")

        # --- Tabs Layout ---
        tab_dash, tab_telemetry = st.tabs(["📊 Main AI Dashboard", "📈 Advanced Telemetry & Raw Data"])

        with tab_dash:
            col_left, col_right = st.columns([1.1, 0.9])

            with col_left:
                render_html('<div class="section-label">Synchronized Pose Video</div>')
                try:
                    with open(result.output_video, "rb") as video_file:
                        processed_video = video_file.read()
                    st.video(processed_video, format="video/mp4")
                    
                    st.download_button(
                        "Download AI Tracked Video",
                        processed_video,
                        file_name=os.path.basename(result.output_video),
                        mime="video/mp4",
                        use_container_width=True
                    )
                except OSError as error:
                    st.warning(f"Processed video could not be displayed: {error}")

                # Metrics Grid
                render_html('<div class="section-label">Key Kinematic Metrics</div>')
                if "error" not in final_summary:
                    metrics_html = '<div class="metrics-grid">'
                    
                    if lift_selection == "squat":
                        knee_angle = final_summary.get("deepest_knee_angle", 0.0)
                        torso_lean = final_summary.get("max_torso_lean_at_bottom", 0.0)
                        depth_ok = final_summary.get("hit_depth", False)
                        lean_ok = torso_lean <= 45.0
                        
                        depth_class = "status-optimal" if depth_ok else "status-deviation"
                        depth_txt = "Optimal Depth" if depth_ok else "Shallow Depth"
                        lean_class = "status-optimal" if lean_ok else "status-deviation"
                        lean_txt = "Optimal Posture" if lean_ok else "Excessive Lean"
                        
                        metrics_html += f'''
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
                        '''
                    elif lift_selection == "pullup":
                        elbow_angle = final_summary.get("min_elbow_angle", 0.0)
                        top_reached = final_summary.get("top_reached", False)
                        depth_class = "status-optimal" if top_reached else "status-deviation"
                        depth_txt = "Strong Top" if top_reached else "Needs More Pull"
                        
                        metrics_html += f'''
                            <div class="metric-item">
                                <div class="metric-label">Top Elbow Flexion</div>
                                <div class="metric-value">{elbow_angle:.1f}°</div>
                                <span class="metric-status {depth_class}">{depth_txt}</span>
                            </div>
                        '''
                    elif lift_selection == "deadlift":
                        hip_ext = final_summary.get("max_hip_extension", 0.0)
                        has_lock = final_summary.get("has_lockout", False)
                        back_warning = final_summary.get("back_rounding_warning", False)
                        
                        lock_class = "status-optimal" if has_lock else "status-deviation"
                        lock_txt = "Fully Locked" if has_lock else "Partial Lockout"
                        back_class = "status-deviation" if back_warning else "status-optimal"
                        back_txt = "Rounding Alert" if back_warning else "Clean Back"
                        
                        metrics_html += f'''
                            <div class="metric-item">
                                <div class="metric-label">Max Hip Extension</div>
                                <div class="metric-value">{hip_ext:.1f}°</div>
                                <span class="metric-status {lock_class}">{lock_txt}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-label">Spine Check</div>
                                <div class="metric-value">{"Warning" if back_warning else "Safe"}</div>
                                <span class="metric-status {back_class}">{back_txt}</span>
                            </div>
                        '''
                    
                    # DTW Tempo
                    if "error" not in dtw_result:
                        dtw_score = dtw_result.get("dtw_score", 0.0)
                        speed_ratio = dtw_result.get("speed_ratio", 1.0)
                        tempo_label = dtw_result.get("tempo_label", "N/A")
                        tempo_class = "status-optimal" if dtw_score < 20 else ("status-info" if dtw_score < 45 else "status-deviation")
                        
                        metrics_html += f'''
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
                        '''
                    metrics_html += '</div>'
                    render_html(metrics_html)

            with col_right:
                render_html('<div class="section-label">AI Coach Report</div>')
                render_html(
                    f"""
                    <div class="coach-card">
                        <div class="coach-header">
                            <div class="coach-avatar">AI</div>
                            <div>
                                <div class="coach-title">Gym Bro Coach</div>
                                <div class="coach-subtitle">Powered by OpenRouter</div>
                            </div>
                        </div>
                        <p class="coach-feedback">"{coaching_report}"</p>
                    </div>
                    """
                )
                
                if "error" not in dtw_result and dtw_result.get("speed_warning"):
                    st.warning(f"**Tempo Warning:** {dtw_result['speed_warning']}")

        with tab_telemetry:
            render_html('<div class="section-label">Joint Kinematics Telemetry</div>')
            
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
                    chart_df, x="Frame", y=[angle_label, "Torso Lean (°)"],
                    labels={"value": "Degrees (°)", "variable": "Metric"},
                    color_discrete_map={angle_label: "#06b6d4", "Torso Lean (°)": "#8b5cf6"}
                )
                
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f8fafc",
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)"),
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as chart_err:
                st.warning(f"Could not render Plotly telemetry graph: {chart_err}")

            st.markdown("### Raw Coordinates Data")
            preview = pd.read_csv(result.raw_csv).head()
            st.dataframe(preview, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                with open(result.raw_csv, "rb") as file:
                    st.download_button("Download Raw Coordinates (CSV)", file, file_name=os.path.basename(result.raw_csv), mime="text/csv", use_container_width=True)
            with c2:
                with open(result.smoothed_csv, "rb") as file:
                    st.download_button("Download Smoothed Coordinates (CSV)", file, file_name=os.path.basename(result.smoothed_csv), mime="text/csv", use_container_width=True)

main()
