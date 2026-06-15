import pandas as pd
from src.physics.analyzer import analyze_angles

def _extract_frame_landmarks(row):
    """Converts a CSV row into a dictionary of {id: [x, y, z, visibility]}"""
    landmarks = {}
    for i in range(33): # MediaPipe tracks 33 landmarks
        try:
            landmarks[i] = [
                row[f'x_{i}'],
                row[f'y_{i}'],
                row[f'z_{i}'],
                row[f'visibility_{i}']
            ]
        except KeyError:
            pass
    return landmarks

def classify_frame(angle_metrics, lift_type="squat"):
    """
    Takes the raw angles and flags any biomechanical deviations.
    Returns a dictionary summarizing the frame's execution quality.
    """
    report = {
        "is_optimal": True,
        "primary_cue": "Looking solid."
    }

    if lift_type == "squat":
        if angle_metrics["knee_flexion"] > 95.0:
            report["is_optimal"] = False
            report["primary_cue"] = "Keep descending, you haven't hit parallel yet."
        elif angle_metrics["torso_lean"] > 45.0:
            report["is_optimal"] = False
            report["primary_cue"] = "Chest up! You are leaning too far forward."
            
    elif lift_type == "pullup":
        if angle_metrics["elbow_flexion"] > 95.0:
            report["is_optimal"] = False
            report["primary_cue"] = "Pull higher and bend your elbows more at the top."
        elif angle_metrics["torso_lean"] > 35.0:
            report["is_optimal"] = False
            report["primary_cue"] = "Keep your torso controlled and avoid swinging."
            
    elif lift_type == "deadlift":
        if angle_metrics["hip_extension"] < 170.0:
            report["is_optimal"] = False
            report["primary_cue"] = "Drive your hips through to finish the lockout."
        elif angle_metrics["knee_flexion"] > 160.0 and angle_metrics["torso_lean"] > 60.0:
            report["is_optimal"] = False
            report["primary_cue"] = "Bend your knees to use your quads off the floor."

    return report

def process_video_csv(csv_path, lift_type="squat"):
    """
    The master pipeline function. 
    Reads Person A's CSV, processes every frame, and returns a full timeline
    of angles and coaching cues for Person D (LLM).
    """
    df = pd.read_csv(csv_path)
    timeline = []

    # Loop through every frame in the video
    for index, row in df.iterrows():
        
        # 1. Format data from CSV
        landmarks = _extract_frame_landmarks(row)
        
        # 2. Run the Physics Engine
        angles = analyze_angles(landmarks)
        
        # 3. Run the Logic Engine
        coaching = classify_frame(angles, lift_type)
        
        # 4. Save to timeline list
        timeline.append({
            "frame_number": row.get('frame', index),
            # Round the angles so the LLM doesn't get confused
            "angles": {k: round(v, 2) for k, v in angles.items()},
            "feedback": coaching
        })

    return timeline

def generate_set_summary(timeline, lift_type="squat"):
    """
    Takes the full timeline of frames and finds the most important moment 
    to evaluate the lift (e.g., the bottom of the squat).
    """
    if not timeline:
        return {"error": "No frames to analyze."}

    if lift_type == "squat":
        # Find the single frame where the knee angle was the smallest
        deepest_frame = min(timeline, key=lambda x: x["angles"]["knee_flexion"])
        
        # We also want to know if they were leaning forward during that deep frame
        max_lean = deepest_frame["angles"]["torso_lean"]
        
        # Generate a final, intelligent report for the whole set
        report = {
            "lift_evaluated": "Squat",
            "deepest_knee_angle": deepest_frame["angles"]["knee_flexion"],
            "max_torso_lean_at_bottom": max_lean,
            "hit_depth": deepest_frame["angles"]["knee_flexion"] <= 95.0,
            "overall_feedback": "Perfect depth!" if deepest_frame["angles"]["knee_flexion"] <= 95.0 else "Shallow squat. Get lower."
        }
        
        if max_lean > 45.0:
            report["overall_feedback"] += " But watch your chest, you leaned too far forward."
            
        return report

    elif lift_type == "pullup":
        # Find the top position where the elbow is most flexed.
        top_frame = min(timeline, key=lambda x: x["angles"]["elbow_flexion"])
        elbow_angle = top_frame["angles"]["elbow_flexion"]
        torso_lean = top_frame["angles"]["torso_lean"]
        top_reached = elbow_angle <= 95.0
        
        report = {
            "lift_evaluated": "Pull-Up",
            "min_elbow_angle": elbow_angle,
            "torso_lean_at_top": torso_lean,
            "top_reached": top_reached,
            "overall_feedback": "Strong top position with good elbow flexion." if top_reached else "Incomplete pull-up. Pull higher and aim to get your chin closer to the bar."
        }
        if torso_lean > 35.0:
            report["overall_feedback"] += " Also, control the swing and keep your torso tighter."
        return report

    elif lift_type == "deadlift":
        # Find the frame with maximum hip extension (lockout at the top)
        lockout_frame = max(timeline, key=lambda x: x["angles"]["hip_extension"])
        max_hip_extension = lockout_frame["angles"]["hip_extension"]
        has_lockout = max_hip_extension >= 170.0
        
        # Check if they rounded their back/stiff-legged off the floor (knees straight, high torso lean)
        bad_pull_frames = [f for f in timeline if f["angles"]["knee_flexion"] > 160.0 and f["angles"]["torso_lean"] > 60.0]
        back_rounding_warning = len(bad_pull_frames) > 0
        
        report = {
            "lift_evaluated": "Deadlift",
            "max_hip_extension": max_hip_extension,
            "has_lockout": has_lockout,
            "back_rounding_warning": back_rounding_warning,
            "overall_feedback": "Solid lockout at the top!" if has_lockout else "Did not fully lock out at the top. Drive your hips through to finish."
        }
        
        if back_rounding_warning:
            report["overall_feedback"] += " Also, make sure to bend your knees and use your legs off the floor rather than lifting with your back."
            
        return report

    # Fallback for other lifts until we add their summary logic
    return {"info": f"Summary logic not yet built for {lift_type}."}
