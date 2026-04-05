# Build a structured candidate profile from CV text using the ai model.

from pathlib import Path
from utils.json_utils import parse_json_object
from models.candidate import CandidateProfile
from services.model_client import call_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "extract_profile.txt"

def build_candidate_profile(cv_text: str) -> CandidateProfile:
    # Extract a candidate profile from CV text and validate the JSON output.
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(cv_text=cv_text)
    response = call_model(prompt)
    data = parse_json_object(response, "Profile response must be a JSON object.")

    required_fields = {"name", "roles", "skills", "years_experience", "summary"}
    missing_fields = required_fields - data.keys()
    if missing_fields:
        missing_list = ", ".join(sorted(missing_fields))
        raise ValueError(f"Profile JSON is missing required fields: {missing_list}")

    return CandidateProfile.from_dict(data)
