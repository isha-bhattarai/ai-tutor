# step6.py — Prompt Templates
# ============================
# Prompt Templates = reusable prompt structures with placeholders
# Write the prompt ONCE, reuse it with different inputs forever
# This makes code cleaner, consistent and maintainable

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"


# ─────────────────────────────────────────
# TEMPLATE DEFINITIONS
# ─────────────────────────────────────────

def explanation_template(topic, level="university", style="simple"):
    return f"""You are an academic tutor teaching a {level} student.

Explain the following topic in a {style} way: {topic}

Structure your explanation exactly like this:
1. DEFINITION: What is {topic}? (2-3 sentences)
2. HOW IT WORKS: Step by step explanation (3-5 sentences)
3. REAL WORLD EXAMPLE: One concrete example anyone can relate to
4. WHY IT MATTERS: Why should a student care about this? (2 sentences)
5. KEY TAKEAWAY: One sentence summary

Keep language clear and accessible for a {level} student."""


def quiz_template(topic, num_questions, difficulty="medium"):
    return f"""You are an academic examiner creating a quiz.

Generate exactly {num_questions} multiple choice questions about: {topic}
Difficulty level: {difficulty}

For EACH question use this EXACT format:

Q[number]: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
Correct Answer: [letter]) [answer]
Difficulty: {difficulty}
Explanation: [why this is correct in one sentence]

---

Rules:
- All {num_questions} questions must be about {topic}
- Difficulty must be {difficulty} throughout
- All 4 options must be plausible — no obviously wrong answers
- Number questions Q1, Q2, Q3 etc."""


def revision_note_template(topic, exam_date_days=7):
    return f"""You are an academic tutor creating revision notes.
A student has an exam on {topic} in {exam_date_days} days.

Create concise revision notes using this EXACT structure:

REVISION NOTES: {topic.upper()}
{'=' * 40}

CORE CONCEPT:
[What is {topic} in 2 sentences]

KEY POINTS TO REMEMBER:
1. [most important point]
2. [second most important point]
3. [third most important point]
4. [fourth most important point]
5. [fifth most important point]

IMPORTANT FORMULAS/DEFINITIONS:
[List any key formulas or definitions]

COMMON EXAM QUESTIONS ON {topic.upper()}:
1. [likely exam question 1]
2. [likely exam question 2]
3. [likely exam question 3]

LAST MINUTE TIPS:
- [tip 1]
- [tip 2]
- [tip 3]
{'=' * 40}
Study time recommended: {exam_date_days * 30} minutes total"""


def study_plan_template(topic, available_days, hours_per_day=2):
    return f"""You are a study coach creating a personalized study plan.

Create a {available_days}-day study plan for: {topic}
Available study time: {hours_per_day} hours per day
Total study hours: {available_days * hours_per_day} hours

Format the plan exactly like this:

STUDY PLAN: {topic.upper()}
Total Duration: {available_days} days | {hours_per_day} hrs/day
{'=' * 40}

DAY-BY-DAY BREAKDOWN:
DAY [number] — [focus area for that day]
- Time: {hours_per_day} hours
- Topics: [specific topics to cover]
- Activity: [how to study]
- Goal: [what to achieve by end of day]

{'=' * 40}
RECOMMENDED RESOURCES:
- [resource 1]
- [resource 2]
- [resource 3]

STUDY TIPS FOR {topic.upper()}:
- [specific tip 1]
- [specific tip 2]"""


# ─────────────────────────────────────────
# SEND PROMPT
# ─────────────────────────────────────────

def send_prompt(prompt):
    """Send any prompt to the API and return response."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


# ─────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────

def main():
    print("=" * 55)
    print("   AI Academic Tutor — Step 6: Prompt Templates")
    print("=" * 55)
    print("1. Explain a topic")
    print("2. Generate a quiz")
    print("3. Get revision notes")
    print("4. Get a study plan")
    print("5. Quit")
    print("=" * 55)

    while True:
        print()
        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            topic = input("Topic to explain: ").strip()
            level = input("Student level (default: university): ").strip() or "university"
            style = input("Style — simple/detailed/technical (default: simple): ").strip() or "simple"
            print("\nGenerating explanation...\n")
            prompt = explanation_template(topic, level, style)
            print(send_prompt(prompt))

        elif choice == "2":
            topic = input("Quiz topic: ").strip()
            num = input("Number of questions (default: 3): ").strip()
            num = int(num) if num.isdigit() else 3
            difficulty = input("Difficulty — easy/medium/hard (default: medium): ").strip() or "medium"
            print("\nGenerating quiz...\n")
            prompt = quiz_template(topic, num, difficulty)
            print(send_prompt(prompt))

        elif choice == "3":
            topic = input("Topic for revision notes: ").strip()
            days = input("Days until exam (default: 7): ").strip()
            days = int(days) if days.isdigit() else 7
            print("\nGenerating revision notes...\n")
            prompt = revision_note_template(topic, days)
            print(send_prompt(prompt))

        elif choice == "4":
            topic = input("What do you want to study: ").strip()
            days = input("How many days available (default: 5): ").strip()
            days = int(days) if days.isdigit() else 5
            hours = input("Hours per day (default: 2): ").strip()
            hours = int(hours) if hours.isdigit() else 2
            print("\nCreating your study plan...\n")
            prompt = study_plan_template(topic, days, hours)
            print(send_prompt(prompt))

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Enter 1, 2, 3, 4 or 5.")


if __name__ == "__main__":
    main()