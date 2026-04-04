# CLI entrypoint for the ai-based interview tool.

from pathlib import Path
from cv_parser import load_cv
from interview_engine import run_interview
from profile_builder import build_candidate_profile
from question_generator import generate_questions

def main() -> None:
    # Run the interview workflow from CV loading to answer capture.
    base_dir = Path(__file__).resolve().parent
    cv_path = base_dir / "data" / "sample_cv.txt"
    answers_path = base_dir / "data" / "answers.json"

    try:
        cv_text = load_cv(str(cv_path))
        profile = build_candidate_profile(cv_text)
        questions = generate_questions(profile)

        print("Candidate profile loaded.")
        print(f"Name: {profile.name or 'Unknown'}")
        print(f"Roles: {', '.join(profile.roles) if profile.roles else 'Not provided'}")
        print()
        print("Starting interview.")

        completed = run_interview(questions, str(answers_path))

        print()
        if completed:
            print("Interview complete. Answers saved to data/answers.json")
        else:
            print("Interview ended early. Partial answers saved to data/answers.json")
    except Exception as exc:
        print(f"Error: {exc}")

if __name__ == "__main__":
    main()
