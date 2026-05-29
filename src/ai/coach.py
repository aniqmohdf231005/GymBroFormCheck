import os
from pathlib import Path
import requests
from src.ai.prompts import SYSTEM_PROMPT, get_user_prompt

# Pure Python .env loader to avoid python-dotenv dependency issues in the demo
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_feedback(metrics: dict, dtw_result: dict, lift_type: str) -> str:
    """
    Sends the biomechanical metrics and DTW temporal results to OpenRouter's LLM API 
    and gets a structured, professional, conversational coaching report.
    If the API call fails or is unavailable, it falls back to a high-quality local template.
    """
    if not API_KEY:
        # Fallback to local template if API key is not configured
        return _local_coaching_fallback(metrics, dtw_result, lift_type)

    user_prompt = get_user_prompt(metrics, dtw_result, lift_type)

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "timeout": 8.0  # Safe timeout for quick presentation feedback
            }
        )

        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                report = result["choices"][0]["message"]["content"].strip()
                if report:
                    return report

        # If HTTP request succeeds but body doesn't match or other issues
        return _local_coaching_fallback(metrics, dtw_result, lift_type)

    except Exception:
        # Fallback to offline rule-based coaching if there is any network / api error
        return _local_coaching_fallback(metrics, dtw_result, lift_type)


def _local_coaching_fallback(metrics: dict, dtw_result: dict, lift_type: str) -> str:
    """Provides a high-quality fallback coaching report in case the API is offline."""
    tempo_label = dtw_result.get("tempo_label", "tempo needs attention")
    overall = metrics.get("overall_feedback", "")
    
    if lift_type == "squat":
        depth_val = metrics.get("deepest_knee_angle", 0)
        lean_val = metrics.get("max_torso_lean_at_bottom", 0)
        return (
            f"Looking at your squat, you reached a maximum knee flexion of {depth_val:.1f} degrees at the bottom. "
            f"Your chest was at an angle of {lean_val:.1f} degrees, and your tempo was classified as {tempo_label.lower()}. "
            f"Focus on keeping your chest high during the descent and drive up explosively."
        )
    elif lift_type == "bench":
        elbow_angle = metrics.get("min_elbow_angle", 0)
        return (
            f"On the bench press, your minimum elbow flexion reached {elbow_angle:.1f} degrees. "
            f"With a {tempo_label.lower()}, you did an excellent job controlling the bar's path. "
            f"Keep maintaining tight shoulder retraction and drive through your legs to stabilize the lift."
        )
    else:
        max_hip = metrics.get("max_hip_extension", 0)
        return (
            f"For your deadlift, you achieved a peak hip extension of {max_hip:.1f} degrees at lockout. "
            f"Your temporal rhythm indicates a {tempo_label.lower()}. "
            f"Remember to pull your shoulders back and engage your lats right from the floor for maximum power."
        )
