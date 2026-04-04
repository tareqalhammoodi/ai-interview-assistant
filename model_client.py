# Minimal model client built on top of urllib.

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

def _load_dotenv() -> None:
    # Load key values from local .env file if present.
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value

_load_dotenv()

API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

def call_model(prompt: str, model: Optional[str] = None) -> str:
    # Send a prompt to the model and return the response text.
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY is not set.")

    selected_model = model or DEFAULT_MODEL
    payload = {
        "model": selected_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.2,
    }

    last_error = ""

    for attempt in range(2):
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ai-interview-assistant/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 403 and "1010" in error_body:
                last_error = (
                    "Model request was blocked by Cloudflare (error 1010)."
                    "Try again without a VPN or proxy, or from a different network."
                )
            else:
                last_error = f"Model HTTP {exc.code}: {error_body}"
        except urllib.error.URLError as exc:
            last_error = f"Model connection error: {exc}"
        except json.JSONDecodeError:
            last_error = "Model returned invalid JSON."
        else:
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError):
                last_error = f"Unexpected Model response format: {data}"

        if attempt == 0:
            time.sleep(1)

    raise RuntimeError(last_error or "Unknown Model API error.")
