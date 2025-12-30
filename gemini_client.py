import json
import re
from google import genai
from config import MODEL_NAME
from prompts import QUIZ_PROMPT
from models import Question


client = genai.Client()

def extract_json(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty response from Gemini")

    # Remove Markdown code fences if present
    text = text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text)

    # Extract first JSON object found
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in response:\n{text}")

    return json.loads(match.group())


class GeminiClient:
    def __init__(self):
        self.client = genai.Client()

    def generate_question(self, subject, difficulty="medium", retries=3) -> Question:
        prompt = QUIZ_PROMPT.format(subject=subject, difficulty=difficulty)

        for attempt in range(1, retries + 1):
            response = self.client.models.generate_content(
                model=MODEL_NAME, contents=prompt
            )
            raw_text = (response.text or "").strip()

            try:
                data = extract_json(raw_text)

                # validate schema
                if (
                    "question" not in data 
                    or "choices" not in data 
                    or "correct_index" not in data 
                    or len(data["choices"]) != 4
                ):
                    raise ValueError("Invalid quiz schema")
                
                return Question(
                    question=data["question"],
                    choices=data["choices"],
                    correct_index=data["correct_index"],
                )

            except Exception as e:
                if attempt == retries:
                    raise RuntimeError(
                        f"Failed to generate valid quiz question after {retries} attempts.\n"
                        f"Last error: {e}\n"
                        f"Raw response:\n{raw_text}"
                    )
                print(f"Gemini output invalid (attempt {attempt}), retrying...")
