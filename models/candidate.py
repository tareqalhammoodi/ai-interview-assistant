# Candidate profile data model.

from dataclasses import dataclass, field
from typing import Any

@dataclass
class CandidateProfile:
    # Structured profile extracted from a CV.
    name: str
    roles: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    years_experience: str = ""
    summary: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateProfile":
        # Create a profile object from a dictionary.
        return cls(
            name=str(data.get("name", "")).strip(),
            roles=[str(item).strip() for item in data.get("roles", []) if str(item).strip()],
            skills=[str(item).strip() for item in data.get("skills", []) if str(item).strip()],
            years_experience=str(data.get("years_experience", "")).strip(),
            summary=str(data.get("summary", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        # Convert the profile back to a dictionary.
        return {
            "name": self.name,
            "roles": self.roles,
            "skills": self.skills,
            "years_experience": self.years_experience,
            "summary": self.summary,
        }
