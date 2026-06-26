# step2.py — Zero-Shot Prompting
# ================================
# Builds on step1.py — imports the client and MODEL from there
# Adds three academic functions: explain, summarize, simplify

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

# ─────────────────────────────────────────
# ZERO-SHOT PROMPT FUNCTIONS
# Each function crafts a detailed prompt
# but gives the AI ZERO examples
# ─────────────────────────────────────────

def explain_topic(topic):
    """
    Zero-shot: ask AI to explain a topic clearly.
    No examples given — AI uses its training knowledge.
    """
    prompt = f"""You are an academic tutor teaching university students.

Your task is to explain the following topic clearly and simply: {topic}

Structure your explanation exactly like this:
1. Simple Definition (2-3 sentences, no jargon)
2. How It Works (3-5 sentences, step by step)
3. Real Life Example (1 concrete example a student can relate to)
4. Key Takeaway (1 sentence summary)

Rules:
- Use simple language suitable for a first year university student
- If you use a technical term, define it immediately
- Do not use bullet points inside sections, write in flowing sentences"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def summarize_material(study_text):
    """
    Zero-shot: summarize a chunk of study material.
    Student pastes their notes/textbook text, AI condenses it.
    """
    prompt = f"""You are an academic tutor helping a student revise before an exam.

Summarize the following study material concisely: 

{study_text}

Your summary must follow this structure:
1. Main Topic (one line — what is this text about?)
2. Key Points (the 3-5 most important ideas, each in one sentence)
3. Important Terms (list any key vocabulary with a brief definition)
4. What To Remember For Exams (the 1-2 things most likely to be tested)

Keep the entire summary under 200 words."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def simplify_concept(complex_text):
    """
    Zero-shot: take complex/technical text and make it simple.
    Useful when a student reads a textbook and doesn't understand it.
    """
    prompt = f"""You are an academic tutor who is an expert at making 
difficult concepts easy to understand.

A student has read the following text and doesn't understand it:

{complex_text}

Rewrite this in the simplest possible way following these rules:
1. Use everyday language — explain it like the student is 16 years old
2. Replace every technical term with a simple explanation
3. Use a real world analogy to make it click
4. Keep sentences short — maximum 15 words per sentence
5. End with: "In short: [one sentence version of the whole thing]" """

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


# ─────────────────────────────────────────
# MAIN — menu to test all three functions
# ─────────────────────────────────────────

def main():
    print("=" * 50)
    print("   AI Academic Tutor — Step 2: Zero-Shot Prompting")
    print("=" * 50)
    print("1. Explain a topic")
    print("2. Summarize study material")
    print("3. Simplify a difficult concept")
    print("4. Quit")
    print("=" * 50)

    while True:
        print()
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            topic = input("Enter topic to explain: ").strip()
            print("\nGenerating explanation...\n")
            result = explain_topic(topic)
            print(result)

        elif choice == "2":
            print("Paste your study material below.")
            print("When done, type END on a new line and press Enter:")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            study_text = "\n".join(lines)
            print("\nSummarizing...\n")
            result = summarize_material(study_text)
            print(result)

        elif choice == "3":
            print("Paste the complex text you want simplified.")
            print("When done, type END on a new line and press Enter:")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            complex_text = "\n".join(lines)
            print("\nSimplifying...\n")
            result = simplify_concept(complex_text)
            print(result)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()