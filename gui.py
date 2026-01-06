import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from typing import List, Optional
from models import Question
from gemini_client import GeminiClient


class QuizDialog(simpledialog.Dialog):
    """Dialog to get quiz subject and number of questions."""
    
    def __init__(self, parent):
        self.subject = None
        self.num_questions = None
        super().__init__(parent, title="New Quiz")
    
    def body(self, master):
        """Create dialog body."""
        tk.Label(master, text="Subject:").grid(row=0, sticky=tk.W, pady=5)
        tk.Label(master, text="Number of Questions:").grid(row=1, sticky=tk.W, pady=5)
        
        self.subject_entry = tk.Entry(master, width=30)
        self.num_questions_entry = tk.Entry(master, width=30)
        
        self.subject_entry.grid(row=0, column=1, pady=5, padx=5)
        self.num_questions_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Set default value for number of questions
        self.num_questions_entry.insert(0, "5")
        
        return self.subject_entry  # initial focus
    
    def validate(self):
        """Validate the input."""
        subject = self.subject_entry.get().strip()
        num_questions = self.num_questions_entry.get().strip()
        
        if not subject:
            messagebox.showerror("Error", "Please enter a subject.")
            return False
        
        try:
            num = int(num_questions)
            if num <= 0:
                messagebox.showerror("Error", "Number of questions must be positive.")
                return False
        except ValueError:
            messagebox.showerror("Error", "Number of questions must be a valid integer.")
            return False
        
        self.subject = subject
        self.num_questions = num
        return True
    
    def apply(self):
        """Called when OK is pressed."""
        pass


class QuizGUI:
    """Main quiz GUI application."""
    
    def __init__(self, root, subject: str, num_questions: int):
        self.root = root
        self.subject = subject
        self.num_questions = num_questions
        self.gemini = GeminiClient()
        
        self.questions: List[Question] = []
        self.user_answers: List[Optional[int]] = [None] * num_questions
        self.current_question_index = 0
        self.selected_answer = tk.IntVar(value=-1)
        
        self.root.title(f"Quiz - {subject}")
        self.root.geometry("700x500")
        
        self._create_widgets()
        self._load_questions()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Question counter label
        self.counter_label = tk.Label(
            self.root, 
            text="", 
            font=("Arial", 12, "bold")
        )
        self.counter_label.pack(pady=10)
        
        # Question panel
        question_frame = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=2)
        question_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=False)
        
        self.question_label = tk.Label(
            question_frame,
            text="",
            font=("Arial", 14),
            wraplength=650,
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        self.question_label.pack()
        
        # Answer panel
        answer_frame = tk.Frame(self.root)
        answer_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Create 4 radio buttons (matching the expected number of choices from Gemini)
        self.answer_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(
                answer_frame,
                text="",
                variable=self.selected_answer,
                value=i,
                font=("Arial", 12),
                wraplength=600,
                justify=tk.LEFT,
                padx=10,
                pady=5,
                command=self._on_answer_selected
            )
            rb.pack(anchor=tk.W, pady=5)
            self.answer_buttons.append(rb)
        
        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=20)
        
        self.back_button = tk.Button(
            nav_frame,
            text="← Back",
            command=self._go_back,
            font=("Arial", 11),
            width=10
        )
        self.back_button.pack(side=tk.LEFT, padx=10)
        
        self.forward_button = tk.Button(
            nav_frame,
            text="Forward →",
            command=self._go_forward,
            font=("Arial", 11),
            width=10
        )
        self.forward_button.pack(side=tk.LEFT, padx=10)
        
        # Progress bar for loading questions
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=5, padx=20, fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(pady=5)
        
        self.status_label = tk.Label(
            progress_frame,
            text="Loading questions...",
            font=("Arial", 10),
            fg="gray"
        )
        self.status_label.pack(pady=5)
    
    def _load_questions(self):
        """Load all questions from Gemini API."""
        self.progress_bar['maximum'] = self.num_questions
        self.progress_bar['value'] = 0
        self.status_label.config(text="Loading questions from Gemini API...")
        self.root.update()
        
        try:
            for i in range(self.num_questions):
                self.status_label.config(
                    text=f"Loading question {i + 1} of {self.num_questions}..."
                )
                self.progress_bar['value'] = i
                self.root.update()
                
                question = self.gemini.generate_question(self.subject)
                self.questions.append(question)
            
            self.progress_bar['value'] = self.num_questions
            self.status_label.config(text="All questions loaded!")
            self.root.update()
            
            # Hide progress bar and status after loading
            self.root.after(1000, lambda: self.progress_bar.pack_forget())
            self.root.after(1000, lambda: self.status_label.config(text=""))
            
            self._display_question()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unable to load questions. Please check your internet connection and API key.\n\n"
                f"Technical details: {str(e)}"
            )
            self.root.destroy()
    
    def _display_question(self):
        """Display the current question and answers."""
        if not self.questions:
            return
        
        question = self.questions[self.current_question_index]
        
        # Update counter
        self.counter_label.config(
            text=f"{self.current_question_index + 1} of {self.num_questions}"
        )
        
        # Update question
        self.question_label.config(text=question.question)
        
        # Update answer choices
        for i, choice in enumerate(question.choices):
            self.answer_buttons[i].config(text=choice)
        
        # Restore previously selected answer if any
        saved_answer = self.user_answers[self.current_question_index]
        if saved_answer is not None:
            self.selected_answer.set(saved_answer)
        else:
            self.selected_answer.set(-1)
        
        # Update button states
        self.back_button.config(
            state=tk.NORMAL if self.current_question_index > 0 else tk.DISABLED
        )
        
        # Check if this is the last question
        is_last = self.current_question_index == self.num_questions - 1
        if is_last:
            self.forward_button.config(text="Finish", command=self._finish_quiz)
        else:
            self.forward_button.config(text="Forward →", command=self._go_forward)
    
    def _on_answer_selected(self):
        """Called when user selects an answer."""
        self.user_answers[self.current_question_index] = self.selected_answer.get()
    
    def _go_back(self):
        """Go to previous question."""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self._display_question()
    
    def _go_forward(self):
        """Go to next question."""
        if self.current_question_index < self.num_questions - 1:
            self.current_question_index += 1
            self._display_question()
    
    def _finish_quiz(self):
        """Calculate score and display results."""
        # Calculate score
        correct = 0
        for i, question in enumerate(self.questions):
            user_answer = self.user_answers[i]
            if user_answer is not None and user_answer == question.correct_index:
                correct += 1
        
        # Calculate percentage (num_questions is guaranteed > 0 by dialog validation)
        percentage = (correct / self.num_questions) * 100
        
        # Display results
        result_message = (
            f"Quiz Completed!\n\n"
            f"Correct Answers: {correct} out of {self.num_questions}\n"
            f"Score: {percentage:.0f}%"
        )
        
        messagebox.showinfo("Quiz Results", result_message)
        self.root.destroy()


def launch_gui():
    """Launch the quiz GUI application."""
    root = tk.Tk()
    root.withdraw()  # Hide main window initially
    
    # Show dialog to get quiz parameters
    dialog = QuizDialog(root)
    
    if dialog.subject and dialog.num_questions:
        root.deiconify()  # Show main window
        QuizGUI(root, dialog.subject, dialog.num_questions)
        root.mainloop()
    else:
        root.destroy()


if __name__ == "__main__":
    launch_gui()
