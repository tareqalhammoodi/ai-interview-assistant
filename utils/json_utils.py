import json
from typing import Any

def parse_json_object(response: str, error_message: str) -> dict[str, Any]:
    # Parse a JSON object from plain or fenced model output.
    json_text = response.strip()

    if json_text.startswith("```"):
        lines = json_text.splitlines()
        if len(lines) >= 3:
            json_text = "\n".join(lines[1:-1]).strip()

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        start = json_text.find("{")
        end = json_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError(error_message) from None
        data = json.loads(json_text[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError(error_message)

    return data
