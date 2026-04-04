# State container for interview progress.

from dataclasses import dataclass, field
from typing import Any
from models.question import Question

@dataclass
class InterviewState:
    # Track interview questions, answers, and the current position.

    questions: list[Question]
    answers: list[dict[str, Any]] = field(default_factory=list)
    current_index: int = 0

    def has_next_question(self) -> bool:
        # Return True while there are still questions remaining.
        return self.current_index < len(self.questions)

    def current_question(self) -> Question | None:
        # Return the active question, if one exists.
        if not self.has_next_question():
            return None
        return self.questions[self.current_index]

    def record_answer(self, answer_text: str, skipped: bool = False) -> None:
        # Store the answer for the current question and move forward. 
        question = self.current_question()
        if question is None:
            raise ValueError("There is no active question to answer.")

        self.answers.append(
            {
                "question_id": question.id,
                "question_text": question.text,
                "type": question.type,
                "answer": answer_text,
                "skipped": skipped,
            }
        )
        self.current_index += 1
