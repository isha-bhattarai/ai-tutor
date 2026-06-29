# step7.py — LangChain-style Sequential Chains
# ==============================================
# A chain = connecting multiple AI calls together
# Output of one step automatically becomes input of the next
# This builds a complete study pipeline in one command

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"


# ─────────────────────────────────────────
# INDIVIDUAL CHAIN LINKS
# Each function = one step in the chain
# Takes input, returns output for next step
# ─────────────────────────────────────────

def chain_explain(topic):
    """
    Chain Link 1 — Explain the topic.
    Input: topic (string)
    Output: explanation (string) → feeds into chain_notes()
    """
    print(f"  [Chain 1/4] Explaining: {topic}...")
    prompt = f"""You are an academic tutor.
Explain '{topic}' clearly for a university student.
Cover: definition, how it works, and one real example.
Keep it under 200 words."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def chain_notes(topic, explanation):
    """
    Chain Link 2 — Convert explanation into structured notes.
    Input: topic + explanation from chain_explain()
    Output: notes (string) → feeds into chain_quiz()
    """
    print(f"  [Chain 2/4] Converting to notes...")
    prompt = f"""You are an academic tutor creating revision notes.

Topic: {topic}
Based on this explanation:
{explanation}

Create structured revision notes with:
- 5 key bullet points
- 2 important definitions
- 1 memory tip
Keep it concise."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def chain_quiz(topic, notes):
    """
    Chain Link 3 — Generate quiz from the notes.
    Input: topic + notes from chain_notes()
    Output: quiz (string) → feeds into chain_summary()
    """
    print(f"  [Chain 3/4] Generating quiz...")
    prompt = f"""You are an academic examiner.

Topic: {topic}
Based on these revision notes:
{notes}

Generate exactly 3 multiple choice questions.
Format each as:
Q: [question]
A) [option] B) [option] C) [option] D) [option]
Answer: [correct letter]"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def chain_summary(topic, explanation, notes, quiz):
    """
    Chain Link 4 — Final summary combining everything.
    Input: all previous outputs
    Output: complete study pack (string)
    """
    print(f"  [Chain 4/4] Building final study pack...")
    prompt = f"""You are an academic tutor.
Create a final one-page study summary for: {topic}

You have already prepared:
- Explanation: {explanation[:200]}...
- Notes: {notes[:200]}...
- Quiz: {quiz[:200]}...

Write a final summary that tells the student:
1. What they learned today (2 sentences)
2. The 3 most important things to remember
3. What to study next
Keep it motivating and under 150 words."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


# ─────────────────────────────────────────
# THE CHAIN RUNNER
# This is the "LangChain" part —
# connects all links automatically
# ─────────────────────────────────────────

def run_study_chain(topic):
    """
    Run the full sequential chain for a topic.
    Topic → Explain → Notes → Quiz → Summary
    Each output feeds into the next step automatically.
    """
    print(f"\nStarting study chain for: {topic}")
    print("=" * 50)

    # Link 1: Explain
    explanation = chain_explain(topic)

    # Link 2: Notes — takes explanation as input
    notes = chain_notes(topic, explanation)

    # Link 3: Quiz — takes notes as input
    quiz = chain_quiz(topic, notes)

    # Link 4: Summary — takes ALL previous outputs
    summary = chain_summary(topic, explanation, notes, quiz)

    # Return everything as a structured package
    return {
        "topic": topic,
        "explanation": explanation,
        "notes": notes,
        "quiz": quiz,
        "summary": summary
    }


def display_results(result):
    """Display the chain results in a clean format."""
    print("\n" + "=" * 55)
    print(f"  COMPLETE STUDY PACK: {result['topic'].upper()}")
    print("=" * 55)

    print("\n--- EXPLANATION ---")
    print(result["explanation"])

    print("\n--- REVISION NOTES ---")
    print(result["notes"])

    print("\n--- QUIZ ---")
    print(result["quiz"])

    print("\n--- FINAL SUMMARY ---")
    print(result["summary"])

    print("\n" + "=" * 55)
    print("  Study pack complete!")
    print("=" * 55)


def main():
    print("=" * 55)
    print("   AI Academic Tutor — Step 7: LangChain Chains")
    print("=" * 55)
    print("This runs a full study pipeline automatically:")
    print("Topic → Explain → Notes → Quiz → Summary")
    print("=" * 55)

    while True:
        print()
        topic = input("Enter a topic to study (or 'quit'): ").strip()

        if topic.lower() == "quit":
            print("Goodbye!")
            break

        if not topic:
            continue

        # Run the full chain
        result = run_study_chain(topic)

        # Display everything
        display_results(result)

        # Ask if they want to save
        save = input("\nSave this study pack to a file? (y/n): ").strip().lower()
        if save == "y":
            filename = f"study_pack_{topic.replace(' ', '_')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"STUDY PACK: {result['topic'].upper()}\n")
                f.write("=" * 50 + "\n\n")
                f.write("EXPLANATION:\n" + result["explanation"] + "\n\n")
                f.write("NOTES:\n" + result["notes"] + "\n\n")
                f.write("QUIZ:\n" + result["quiz"] + "\n\n")
                f.write("SUMMARY:\n" + result["summary"] + "\n")
            print(f"Saved to {filename}")


if __name__ == "__main__":
    main()