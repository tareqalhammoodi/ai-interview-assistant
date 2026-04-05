# Interactive terminal interview loop.

import json
from pathlib import Path
from utils.json_utils import parse_json_object
from models.interview_state import InterviewState
from models.question import Question
from services.model_client import call_model

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPHRASE_PROMPT_PATH = PROJECT_ROOT / "prompts" / "rephrase_question.txt"
INTENT_PROMPT_PATH = PROJECT_ROOT / "prompts" / "detect_intent.txt"
COMMAND_REPEAT = "repeat"
COMMAND_CLARIFY = "clarify"
COMMAND_SKIP = "skip"
COMMAND_EXIT = "exit"

def run_interview(questions: list[Question], answers_path: str) -> bool:
    # Run the interview loop and persist answers after each step.
    state = InterviewState(questions=questions)
    output_path = Path(answers_path)
    _save_answers(state.answers, output_path)

    while state.has_next_question():
        question = state.current_question()
        if question is None:
            break

        print()
        print(f"Question {state.current_index + 1}/{len(state.questions)}")
        print(question.text)
        while True:
            user_input = input("> ").strip()

            if not user_input:
                print("Please provide an answer to the given question!")
                continue

            command = _detect_intent(user_input)

            if command == COMMAND_REPEAT:
                print(question.text)
                continue

            if command == COMMAND_CLARIFY:
                clarified_question = _clarify_question(question.text)
                print(f"Clarified: {clarified_question}")
                continue

            if command == COMMAND_SKIP:
                state.record_answer("", skipped=True)
                _save_answers(state.answers, output_path)
                break

            if command == COMMAND_EXIT:
                _save_answers(state.answers, output_path)
                return False

            state.record_answer(user_input, skipped=False)
            _save_answers(state.answers, output_path)
            break

    return True

def _clarify_question(question_text: str) -> str:
    # Ask ai model to rewrite a question in simpler language.
    template = REPHRASE_PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(question=question_text)
    response = call_model(prompt)
    return response.strip()

def _detect_intent(user_input: str) -> str | None:
    # Use the model to classify interview input as a command or an answer.
    template = INTENT_PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(user_input=user_input)

    try:
        response = call_model(prompt)
        data = parse_json_object(response, "Intent response must be a JSON object.")
    except Exception:
        return None

    intent = str(data.get("intent", "")).strip().lower()
    if intent in {COMMAND_REPEAT, COMMAND_CLARIFY, COMMAND_SKIP, COMMAND_EXIT}:
        return intent
    return None

def _save_answers(answers: list[dict], answers_path: Path) -> None:
    # Persist answers to a JSON file.
    answers_path.parent.mkdir(parents=True, exist_ok=True)
    answers_path.write_text(json.dumps(answers, indent=2), encoding="utf-8")
