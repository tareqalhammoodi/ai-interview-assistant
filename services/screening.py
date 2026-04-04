# Minimal candidate screening helpers.

import json
from pathlib import Path
from models.candidate import CandidateProfile
from model_client import call_model
from utils.json_utils import parse_json_object

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "evaluate_candidate.txt"

def load_job_requirements(file_path: str) -> str:
    # Read a plain-text job requirements file.
    return Path(file_path).read_text(encoding="utf-8").strip()

def evaluate_candidate(
    profile: CandidateProfile,
    job_requirements: str,
    interview_threshold: int = 70,
) -> dict:
    # Score how well a candidate matches the target job.
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        profile=json.dumps(profile.to_dict(), indent=2),
        job_requirements=job_requirements,
        interview_threshold=interview_threshold,
    )
    response = call_model(prompt)
    data = parse_json_object(response, "Candidate evaluation response must be a JSON object.")

    required_fields = {"score", "matched_requirements", "missing_requirements", "summary"}
    missing_fields = required_fields - data.keys()
    if missing_fields:
        missing_list = ", ".join(sorted(missing_fields))
        raise ValueError(f"Candidate evaluation is missing required fields: {missing_list}")

    score = _normalize_score(data.get("score", 0))

    return {
        "score": score,
        "matched_requirements": _clean_list(data.get("matched_requirements", [])),
        "missing_requirements": _clean_list(data.get("missing_requirements", [])),
        "summary": str(data.get("summary", "")).strip(),
        "should_interview": score >= interview_threshold,
    }

def _clean_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]

def _normalize_score(value: object) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))
