# step4.py — Chain-of-Thought Prompting
# =======================================
# Chain-of-Thought = forcing AI to show step-by-step reasoning
# before arriving at a final answer
# This makes AI MORE accurate on complex problems

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"


def solve_math(problem):
    """
    Chain-of-thought for math/physics problems.
    Forces AI to show every calculation step clearly.
    """
    prompt = f"""You are an academic tutor helping a student solve a problem.

The student needs help with this problem:
{problem}

Before giving the answer, think through this step by step.
Follow this EXACT structure:

UNDERSTANDING THE PROBLEM:
(What is given? What are we trying to find?)

FORMULA/CONCEPT NEEDED:
(What formula or concept applies here?)

STEP BY STEP SOLUTION:
Step 1: [first step with calculation]
Step 2: [second step with calculation]
Step 3: [continue until solved...]

FINAL ANSWER:
(State the answer clearly with units if applicable)

VERIFICATION:
(Quickly check if the answer makes sense)"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def logical_reason(question):
    """
    Chain-of-thought for logical/reasoning questions.
    Forces AI to reason through each possibility systematically.
    """
    prompt = f"""You are an academic tutor helping a student think through a reasoning problem.

Question: {question}

Do NOT jump to the answer. Instead think through this carefully:

BREAKING DOWN THE QUESTION:
(What exactly is being asked? What are the key elements?)

WHAT WE KNOW:
(List every fact or clue given in the question)

REASONING THROUGH IT:
Thought 1: [first logical deduction]
Thought 2: [second logical deduction]  
Thought 3: [continue the chain of reasoning...]

ELIMINATING WRONG OPTIONS (if applicable):
(Why are other answers wrong?)

CONCLUSION:
(Final answer based on the reasoning above)

LESSON:
(What concept or skill does this question test?)"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def analyze_problem(scenario):
    """
    Chain-of-thought for scientific or analytical problems.
    Forces AI to apply scientific method step by step.
    """
    prompt = f"""You are a subject expert helping a student analyze a complex problem.

Problem/Scenario: {scenario}

Analyze this systematically using the following chain of reasoning:

IDENTIFYING THE CORE ISSUE:
(What is the central problem or question here?)

RELEVANT CONCEPTS AND THEORIES:
(What academic concepts apply to this situation?)

ANALYSIS — STEP BY STEP:
Point 1: [first aspect of analysis]
Point 2: [second aspect of analysis]
Point 3: [third aspect of analysis]
(add more points if needed)

CONNECTING THE DOTS:
(How do these points relate to each other?)

CONCLUSION:
(What is the final answer or insight?)

REAL WORLD APPLICATION:
(Where would this analysis be useful in real life?)"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


def main():
    print("=" * 55)
    print("   AI Academic Tutor — Step 4: Chain-of-Thought")
    print("=" * 55)
    print("1. Solve a math/physics problem step by step")
    print("2. Work through a logical reasoning question")
    print("3. Analyze a complex scenario or problem")
    print("4. Quit")
    print("=" * 55)

    while True:
        print()
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            print("Enter your math/physics problem:")
            problem = input("Problem: ").strip()
            print("\nThinking step by step...\n")
            print(solve_math(problem))

        elif choice == "2":
            print("Enter your reasoning/logic question:")
            question = input("Question: ").strip()
            print("\nReasoning through it...\n")
            print(logical_reason(question))

        elif choice == "3":
            print("Enter the scenario or problem to analyze:")
            print("(type END on a new line when done)")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            scenario = "\n".join(lines)
            print("\nAnalyzing...\n")
            print(analyze_problem(scenario))

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()