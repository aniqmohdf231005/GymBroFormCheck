import numpy as np

def _calculate_angle(a, b, c):
    """Calculates the 3D angle at vertex 'b'."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    
    # Avoid division by zero if points overlap
    if np.linalg.norm(ba) == 0 or np.linalg.norm(bc) == 0:
        return 0.0
        
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    # Clip to handle floating point inaccuracies before arccos
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    return float(np.degrees(np.arccos(cosine_angle)))

def _calculate_vertical_angle(shoulder, hip):
    """Calculates torso lean relative to a pure vertical line."""
    spine = np.array(shoulder) - np.array(hip)
    vertical = np.array([0, -1, 0]) # Assuming Y is vertical in your space
    
    # Avoid division by zero
    if np.linalg.norm(spine) == 0:
        return 0.0
        
    cosine_angle = np.dot(spine, vertical) / (np.linalg.norm(spine) * np.linalg.norm(vertical))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    return float(np.degrees(np.arccos(cosine_angle)))

def _get_active_side(landmarks):
    """
    Compares the visibility of the left vs right side.
    Returns a dictionary of the correct landmark IDs to use.
    """
    # MediaPipe IDs for Left Side
    left_ids = {"shoulder": 11, "elbow": 13, "wrist": 15, "hip": 23, "knee": 25, "ankle": 27}
    # MediaPipe IDs for Right Side
    right_ids = {"shoulder": 12, "elbow": 14, "wrist": 16, "hip": 24, "knee": 26, "ankle": 28}

    # Extract the visibility score (index 3) for major joints
    left_vis = sum([
        landmarks.get(left_ids["shoulder"], [0,0,0,0])[3],
        landmarks.get(left_ids["hip"], [0,0,0,0])[3],
        landmarks.get(left_ids["knee"], [0,0,0,0])[3]
    ])
    
    right_vis = sum([
        landmarks.get(right_ids["shoulder"], [0,0,0,0])[3],
        landmarks.get(right_ids["hip"], [0,0,0,0])[3],
        landmarks.get(right_ids["knee"], [0,0,0,0])[3]
    ])

    return left_ids if left_vis > right_vis else right_ids

def analyze_angles(landmarks):
    """
    Takes a dictionary of landmarks for a SINGLE frame.
    Automatically detects the facing side and returns the core biomechanical angles.
    """
    # 1. Figure out which side of the body we are tracking
    active_ids = _get_active_side(landmarks)

    # 2. Extract those specific coordinates (slice only the [x, y, z] for the math)
    shoulder = landmarks.get(active_ids["shoulder"], [0,0,0,0])[:3]
    elbow = landmarks.get(active_ids["elbow"], [0,0,0,0])[:3]
    wrist = landmarks.get(active_ids["wrist"], [0,0,0,0])[:3]
    hip = landmarks.get(active_ids["hip"], [0,0,0,0])[:3]
    knee = landmarks.get(active_ids["knee"], [0,0,0,0])[:3]
    ankle = landmarks.get(active_ids["ankle"], [0,0,0,0])[:3]

    # 3. Calculate all metrics
    angle_metrics = {
        "knee_flexion": _calculate_angle(hip, knee, ankle),
        "hip_extension": _calculate_angle(shoulder, hip, knee),
        "elbow_flexion": _calculate_angle(shoulder, elbow, wrist),
        "torso_lean": _calculate_vertical_angle(shoulder, hip)
    }
    
    return angle_metrics