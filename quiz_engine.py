from rich.console import Console
from rich.prompt import Prompt

console = Console()

class QuizEngine:
    def run_question(self, question):
        console.print(f"\n[bold cyan]{question.question}[/bold cyan]\n")

        for i, choice in enumerate(question.choices):
            console.print(f"{i + 1}. {choice}")

        answer = Prompt.ask(
            "\nYour answer",
            choices=[str(i) for i in range(1, 5)]
        )

        is_correct = int(answer) - 1 == question.correct_index

        if is_correct:
            console.print("[green]✔ Correct![/green]")
        else:
            correct = question.choices[question.correct_index]
            console.print(f"[red]✘ Incorrect[/red] — Correct answer: {correct}")

        return is_correct

