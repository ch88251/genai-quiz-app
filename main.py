from gemini_client import GeminiClient
from quiz_engine import QuizEngine
from rich.prompt import Prompt
from rich.console import Console

console = Console()

def main():
    subject = Prompt.ask("Enter quiz subject")
    num_questions = int(Prompt.ask("How many questions?", default="5"))

    gemini = GeminiClient()
    quiz = QuizEngine()

    score = 0

    for _ in range(num_questions):
        question = gemini.generate_question(subject)
        if quiz.run_question(question):
            score += 1

    console.print(
        f"\n[bold yellow]Final Score: {score}/{num_questions}[/bold yellow]"
    )

if __name__ == "__main__":
    main()

