# Interview question data model.

from dataclasses import dataclass
from typing import Any

@dataclass
class Question:
    #Single interview question.
    id: int
    text: str
    type: str = "behavioral"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Question":
        # Create a question object from a dictionary.
        question_id = int(data.get("id", 0))
        text = str(data.get("text", "")).strip()
        question_type = str(data.get("type", "behavioral")).strip() or "behavioral"

        if not text:
            raise ValueError("Question text cannot be empty.")

        return cls(id=question_id, text=text, type=question_type)

    def to_dict(self) -> dict[str, Any]:
        # Convert the question back to a dictionary.
        return {"id": self.id, "text": self.text, "type": self.type}
