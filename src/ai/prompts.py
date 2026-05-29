SYSTEM_PROMPT = """You are a professional powerlifting and biomechanics coach giving real-time feedback after watching a lift.
You will receive a set of biomechanical metrics, joint angles, classifications, and Dynamic Time Warping (DTW) tempo results in JSON format.

Your job is to write a short, highly engaging, and conversational coaching report. Follow these rules strictly:
1. Write EXACTLY 3-4 sentences.
2. Speak directly to the lifter ("you", "your").
3. Be specific and reference the actual numbers (e.g., specific joint angles or speed ratios) directly in your sentences.
4. Provide continuous feedback (e.g., referencing what happened at the bottom, top/lockout, or tempo).
5. Be encouraging but honest about form deviations.
6. DO NOT use bullet points, lists, or headers. Write as a single, fluid paragraph.
7. Avoid generic advice; tailor it directly to the metrics provided.
"""

def get_user_prompt(metrics: dict, dtw_result: dict, lift_type: str) -> str:
    """Generates the user prompt detailing the lift metrics and tempo results."""
    
    # Clean up and combine metrics
    lift_name = lift_type.capitalize()
    if lift_type == "bench":
        lift_name = "Bench Press"
        
    user_prompt = f"""Here are the lifter's metrics and tempo analysis for their {lift_name} set:

--- BIOMECHANICAL METRICS ---
{metrics}

--- TEMPORAL & TEMPO ANALYSIS (DTW) ---
{dtw_result}

Please analyze the data and generate your 3-4 sentence direct coaching report based on the rules. Keep it professional, encouraging, and rich in biomechanics insights!"""
    
    return user_prompt
