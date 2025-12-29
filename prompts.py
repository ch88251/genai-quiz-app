QUIZ_PROMPT = """
Generate ONE multiple-choice quiz question about the following subject:

Subject: {subject}
Difficulty: {difficulty}

Rules:
- Provide exactly 4 answer choices
- Only one answer is correct
- Do NOT explain the answer
- Return JSON ONLY in this format:

{{
  "question": "...",
  "choices": ["A", "B", "C", "D"],
  "correct_index": 0
}}
"""
