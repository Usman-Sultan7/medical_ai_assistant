import json
import re

def safe_parse_json(text: str) -> dict:
    """Parses JSON safely and prevents app crashes."""
    try:
        # Strip out Markdown formatting if the LLM includes it
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        return json.loads(text.strip())
    except Exception:
        # Fallback if the LLM fails to return valid JSON
        return {
            "summary": "Error analyzing symptoms.",
            "possible_conditions": [],
            "urgency_level": "UNKNOWN",
            "recommended_next_steps": ["Please consult a doctor immediately."],
            "questions_for_doctor": [],
            "warning_signs": []
        }