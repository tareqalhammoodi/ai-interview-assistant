## AI Interview Assistant

This is a simple AI tool built in Python that simulates a behavioral HR interview using AI. It reads a candidate CV, evaluate profiles, generates interview questions, and runs an interactive question-and-answer session directly in the command line.

## Config

Create a `.env` file in the project root:

```env
API_KEY=api_key_here
MODEL=llama-3.3-70b-versatile
```

Notes:

- `API_KEY` is required
- `MODEL` is optional. If you do not set it, the default model is `llama-3.3-70b-versatile`

## Run

```bash
python3 main.py
```

Notes:

- Outputs are saved under `data/output/`.
- Update `job_requirements.txt` as needed.
