# CLI entrypoint for the ai-based interview tool.

import json
import re
from pathlib import Path
from parsers.cv_parser import load_all_cvs
from services.interview_engine import run_interview
from services.profile_builder import build_candidate_profile
from services.question_generator import generate_questions
from services.screening import evaluate_candidate, load_job_requirements

INTERVIEW_THRESHOLD = 70

def main() -> None:
    # Load all CVs, shortlist strong matches, and interview the best one.
    base_dir = Path(__file__).resolve().parent
    cv_dir = base_dir / "data" / "cvs"
    job_requirements_path = base_dir / "data" / "job_requirements.txt"
    output_dir = base_dir / "data" / "output"

    try:
        job_requirements = load_job_requirements(str(job_requirements_path))
        cv_documents = load_all_cvs(str(cv_dir))
        if not cv_documents:
            raise ValueError("No CV files found in data/cvs")

        candidates: list[dict] = []
        for file_name, cv_text in cv_documents:
            profile = build_candidate_profile(cv_text)
            evaluation = evaluate_candidate(
                profile,
                job_requirements,
                interview_threshold=INTERVIEW_THRESHOLD,
            )
            candidates.append(
                {
                    "file_name": file_name,
                    "profile": profile,
                    "evaluation": evaluation,
                }
            )

        candidates.sort(key=lambda item: item["evaluation"]["score"], reverse=True)
        shortlisted = [
            candidate
            for candidate in candidates
            if candidate["evaluation"]["should_interview"]
        ]

        _save_json(
            output_dir / "screening_results.json",
            {
                "job_requirements": job_requirements,
                "interview_threshold": INTERVIEW_THRESHOLD,
                "candidates": [
                    {
                        "file_name": candidate["file_name"],
                        "profile": candidate["profile"].to_dict(),
                        "evaluation": candidate["evaluation"],
                    }
                    for candidate in candidates
                ],
            },
        )

        print(f"Loaded {len(candidates)} CV(s).")
        print(f"Interview threshold: {INTERVIEW_THRESHOLD}/100")
        print()
        print("Screening results:")
        for candidate in candidates:
            name = candidate["profile"].name or candidate["file_name"]
            score = candidate["evaluation"]["score"]
            status = "SHORTLISTED" if candidate["evaluation"]["should_interview"] else "IGNORED"
            print(f"- {name}: {score}/100 ({status})")

        if not shortlisted:
            print()
            print("No candidate matched the job requirements well enough for interview.")
            return

        best_candidate = shortlisted[0]
        questions = generate_questions(
            best_candidate["profile"],
            job_requirements=job_requirements,
            evaluation_summary=best_candidate["evaluation"]["summary"],
        )

        candidate_name = best_candidate["profile"].name or best_candidate["file_name"]
        candidate_slug = _slugify(candidate_name)
        answers_path = output_dir / f"{candidate_slug}_answers.json"
        questions_path = output_dir / f"{candidate_slug}_questions.json"

        _save_json(
            questions_path,
            {
                "candidate_name": candidate_name,
                "questions": [question.to_dict() for question in questions],
            },
        )

        print()
        print(f"Starting interview for {candidate_name}.")
        print(best_candidate["evaluation"]["summary"])

        completed = run_interview(questions, str(answers_path))

        print()
        if completed:
            print(f"Interview complete. Answers saved to {answers_path.relative_to(base_dir)}")
        else:
            print(f"Interview ended early. Partial answers saved to {answers_path.relative_to(base_dir)}")
    except Exception as exc:
        print(f"Error: {exc}")

def _save_json(file_path: Path, data: dict) -> None:
    # Save JSON output and create the parent directory if needed.
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _slugify(value: str) -> str:
    # Turn text into a safe file name.
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "candidate"

if __name__ == "__main__":
    main()
