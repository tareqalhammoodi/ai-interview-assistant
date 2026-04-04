# Build a structured candidate profile from CV text using the ai model.

import json
from pathlib import Path
from typing import Any
from models.candidate import CandidateProfile
from model_client import call_model

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "extract_profile.txt"

def build_candidate_profile(cv_text: str) -> CandidateProfile:
    # Extract a candidate profile from CV text and validate the JSON output.
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(cv_text=cv_text)
    response = call_model(prompt)
    data = _parse_json_response(response)

    required_fields = {"name", "roles", "skills", "years_experience", "summary"}
    missing_fields = required_fields - data.keys()
    if missing_fields:
        missing_list = ", ".join(sorted(missing_fields))
        raise ValueError(f"Profile JSON is missing required fields: {missing_list}")

    return CandidateProfile.from_dict(data)

def _parse_json_response(response: str) -> dict[str, Any]:
    # Parse JSON from a model response, tolerating fenced or wrapped output.
    json_text = response.strip()

    if json_text.startswith("```"):
        lines = json_text.splitlines()
        if len(lines) >= 3:
            json_text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError:
        start = json_text.find("{")
        end = json_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Model did not return valid JSON.")
        parsed = json.loads(json_text[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Profile response must be a JSON object.")

    return parsed
