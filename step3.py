# step3.py — Few-Shot Prompting
# ================================
# Few-shot = we give the AI examples INSIDE the prompt
# so it learns the exact format/style we want
# and replicates it consistently

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"


def generate_quiz(topic, num_questions=3):
    """
    Few-shot: generate MCQ quiz questions.
    We show 2 example questions first so AI copies the format exactly.
    """
    prompt = f"""You are an academic tutor creating quiz questions for university students.

Here are examples of the EXACT format I want:

EXAMPLE 1:
Q: What is the powerhouse of the cell?
A) Nucleus
B) Mitochondria
C) Ribosome
D) Vacuole
Correct Answer: B) Mitochondria
Difficulty: Easy
Explanation: Mitochondria produce ATP energy through cellular respiration.

EXAMPLE 2:
Q: Which law states that force equals mass times acceleration?
A) Newton's First Law
B) Newton's Third Law
C) Newton's Second Law
D) Law of Gravitation
Correct Answer: C) Newton's Second Law
Difficulty: Easy
Explanation: F=ma is Newton's Second Law, where F is force, m is mass, a is acceleration.

EXAMPLE 3:
Q: What type of bond holds the two strands of DNA together?
A) Covalent bond
B) Ionic bond
C) Hydrogen bond
D) Metallic bond
Correct Answer: C) Hydrogen bond
Difficulty: Medium
Explanation: Hydrogen bonds between complementary base pairs hold the DNA double helix together.

Now generate {num_questions} quiz questions about: {topic}
Follow the EXACT same format as the examples above.
Make sure all 4 options are plausible — not obviously wrong."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def categorize_answer(question, student_answer):
    """
    Few-shot: evaluate a student's answer and categorize it.
    We show examples of how to grade so AI is consistent.
    """
    prompt = f"""You are a fair academic examiner evaluating student answers.

Here are examples of how to evaluate and categorize answers:

EXAMPLE 1:
Question: What is photosynthesis?
Student Answer: It's when plants make food using sunlight and water.
Evaluation:
Category: Good
Score: 7/10
What was correct: Correctly identified sunlight and water as inputs.
What was missing: Did not mention CO2 as input or O2 as output, or chlorophyll.
Feedback: Good basic understanding! Add CO2 absorption and oxygen release to make it complete.

EXAMPLE 2:
Question: What is photosynthesis?
Student Answer: Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen using chlorophyll in chloroplasts.
Evaluation:
Category: Excellent
Score: 10/10
What was correct: All components mentioned — sunlight, water, CO2, glucose, oxygen, chlorophyll.
What was missing: Nothing significant.
Feedback: Perfect answer! You've covered all key components clearly.

EXAMPLE 3:
Question: What is photosynthesis?
Student Answer: Plants eat sunlight.
Evaluation:
Category: Needs Work
Score: 2/10
What was correct: Correctly linked plants and sunlight.
What was missing: Almost everything — inputs, outputs, process, location.
Feedback: You're on the right track but need much more detail. Plants don't "eat" — they convert light energy into chemical energy.

Now evaluate this:
Question: {question}
Student Answer: {student_answer}

Follow the EXACT same format as the examples above."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def generate_notes(topic):
    """
    Few-shot: generate structured revision notes.
    We show an example of notes so AI follows consistent structure.
    """
    prompt = f"""You are an academic tutor creating revision notes for university students.

Here is an example of the EXACT format and style I want for revision notes:

EXAMPLE TOPIC: Newton's Laws of Motion
═══════════════════════════════════════
📚 REVISION NOTES: Newton's Laws of Motion
═══════════════════════════════════════

🔑 KEY DEFINITION:
Newton's Laws describe how objects move and respond to forces.

📌 MAIN CONCEPTS:
1. First Law (Inertia): An object stays at rest or in motion unless acted on by a force.
2. Second Law (F=ma): Force equals mass times acceleration.
3. Third Law (Action-Reaction): Every action has an equal and opposite reaction.

⚡ QUICK EXAMPLES:
- First Law: A book stays on a table until you push it.
- Second Law: Pushing a heavy cart needs more force than a light one.
- Third Law: A rocket pushes gas down, gas pushes rocket up.

🧠 MEMORY TIP:
"I Stay, I Change, I React" — one phrase for all three laws.

⚠️ COMMON EXAM MISTAKES:
- Confusing mass (kg) with weight (N)
- Forgetting that F=ma uses NET force, not just any force

📝 LIKELY EXAM QUESTIONS:
- State and explain Newton's Second Law with an example.
- A 10kg object accelerates at 5 m/s². What force acts on it?
═══════════════════════════════════════

Now create revision notes for: {topic}
Follow the EXACT same format, emojis, and structure as the example above."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def main():
    print("=" * 50)
    print("   AI Academic Tutor — Step 3: Few-Shot Prompting")
    print("=" * 50)
    print("1. Generate quiz questions")
    print("2. Evaluate my answer")
    print("3. Generate revision notes")
    print("4. Quit")
    print("=" * 50)

    while True:
        print()
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            topic = input("Enter topic for quiz: ").strip()
            num = input("How many questions? (default 3): ").strip()
            num = int(num) if num.isdigit() else 3
            print("\nGenerating quiz...\n")
            print(generate_quiz(topic, num))

        elif choice == "2":
            question = input("Enter the question: ").strip()
            print("Enter your answer (type END when done):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            student_answer = "\n".join(lines)
            print("\nEvaluating your answer...\n")
            print(categorize_answer(question, student_answer))

        elif choice == "3":
            topic = input("Enter topic for revision notes: ").strip()
            print("\nGenerating notes...\n")
            print(generate_notes(topic))

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()