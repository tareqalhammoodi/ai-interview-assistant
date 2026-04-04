# Generate interview questions from a structured candidate profile.

import json
from pathlib import Path
from typing import Any
from models.candidate import CandidateProfile
from models.question import Question
from model_client import call_model

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "generate_questions.txt"

def generate_questions(profile: CandidateProfile) -> list[Question]:
    # Generate five behavioral interview questions for a candidate profile.
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(profile=json.dumps(profile.to_dict(), indent=2))
    response = call_model(prompt)
    data = _parse_json_response(response)

    questions_data = data.get("questions")
    if not isinstance(questions_data, list):
        raise ValueError("Questions response must include a 'questions' list.")

    questions = [Question.from_dict(item) for item in questions_data]
    if len(questions) != 5:
        raise ValueError("Model must return exactly 5 interview questions.")

    return questions

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
        raise ValueError("Questions response must be a JSON object.")

    return parsed
