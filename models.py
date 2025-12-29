from dataclasses import dataclass
from typing import List

@dataclass
class Question:
  question: str
  choices: List[str]
  correct_index: int
