import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ai.coach import generate_feedback

def run_test():
    print("====================================================")
    print("Gym Bro AI Coach End-to-End API Integration Test")
    print("====================================================\n")

    test_scenarios = [
        {
            "lift_type": "squat",
            "metrics": {
                "lift_evaluated": "Squat",
                "deepest_knee_angle": 88.4,
                "max_torso_lean_at_bottom": 32.1,
                "hit_depth": True,
                "overall_feedback": "Perfect depth!"
            },
            "dtw_result": {
                "dtw_score": 15.42,
                "tempo_label": "Excellent tempo",
                "speed_ratio": 1.05,
                "speed_warning": None
            }
        },
        {
            "lift_type": "bench",
            "metrics": {
                "lift_evaluated": "Bench Press",
                "min_elbow_angle": 96.5,
                "hit_depth": False,
                "overall_feedback": "Shallow press. Focus on bringing the bar all the way down to touch your chest."
            },
            "dtw_result": {
                "dtw_score": 38.12,
                "tempo_label": "Good tempo",
                "speed_ratio": 0.85,
                "speed_warning": None
            }
        },
        {
            "lift_type": "deadlift",
            "metrics": {
                "lift_evaluated": "Deadlift",
                "max_hip_extension": 164.2,
                "has_lockout": False,
                "back_rounding_warning": True,
                "overall_feedback": "Did not fully lock out at the top. Drive your hips through to finish. Also, make sure to bend your knees and use your legs off the floor rather than lifting with your back."
            },
            "dtw_result": {
                "dtw_score": 82.5,
                "tempo_label": "Tempo needs work",
                "speed_ratio": 2.45,
                "speed_warning": "Too slow — you held the position too long compared to the reference."
            }
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        lift_type = scenario["lift_type"]
        metrics = scenario["metrics"]
        dtw_result = scenario["dtw_result"]

        print(f"[{i}] Testing {lift_type.upper()}...")
        print(f"Metrics Sent: {metrics}")
        print(f"DTW Sent: {dtw_result}")
        print("\nRequesting coaching report from OpenRouter...")
        
        try:
            report = generate_feedback(metrics, dtw_result, lift_type)
            print(f"AI Coach Report:\n{report}")
        except Exception as e:
            print(f"Error calling AI Coach: {e}")
            
        print("-" * 52 + "\n")

if __name__ == "__main__":
    run_test()
