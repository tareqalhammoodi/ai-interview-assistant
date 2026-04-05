# Generate interview questions from a structured candidate profile.

import json
from pathlib import Path
from utils.json_utils import parse_json_object
from models.candidate import CandidateProfile
from models.question import Question
from services.model_client import call_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "generate_questions.txt"

def generate_questions(
    profile: CandidateProfile,
    job_requirements: str = "",
    evaluation_summary: str = "",
) -> list[Question]:
    # Generate five interview questions for a shortlisted candidate.
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        profile=json.dumps(profile.to_dict(), indent=2),
        job_requirements=job_requirements,
        evaluation_summary=evaluation_summary,
    )
    response = call_model(prompt)
    data = parse_json_object(response, "Questions response must be a JSON object.")

    questions_data = data.get("questions")
    if not isinstance(questions_data, list):
        raise ValueError("Questions response must include a 'questions' list.")

    questions = [Question.from_dict(item) for item in questions_data]
    if len(questions) != 10:
        raise ValueError("Model must return exactly 10 interview questions.")

    return questions
