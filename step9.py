# step9.py — Agents & Tools
# ==========================
# An Agent = AI that decides WHICH tool to use by itself
# You talk naturally — agent figures out the right action
# No menus, no option picking — just conversation

from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"


# ─────────────────────────────────────────
# TOOLS
# Each tool does one specific job
# The agent picks which one to call
# ─────────────────────────────────────────

def tool_explain(topic):
    """Tool: Explain a topic clearly."""
    print(f"  [Tool: Explainer] Running for '{topic}'...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""You are an academic tutor.
Explain '{topic}' clearly for a university student.
Include: definition, how it works, real example.
Keep under 200 words."""
    )
    return response.text


def tool_quiz(topic, num=3):
    """Tool: Generate quiz questions."""
    print(f"  [Tool: Quiz Generator] Running for '{topic}'...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""Generate {num} multiple choice questions about: {topic}
Format each as:
Q: [question]
A) B) C) D) options
Answer: [letter]"""
    )
    return response.text


def tool_calculator(problem):
    """Tool: Solve math problems step by step."""
    print(f"  [Tool: Calculator] Solving '{problem}'...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""Solve this math/physics problem step by step:
{problem}

Show every step clearly.
State the final answer with units."""
    )
    return response.text


def tool_study_planner(topic, days=5):
    """Tool: Create a study plan."""
    print(f"  [Tool: Study Planner] Planning '{topic}' for {days} days...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""Create a {days}-day study plan for: {topic}
Include daily goals, activities, and resources.
Keep it practical and motivating."""
    )
    return response.text


def tool_summarizer(text):
    """Tool: Summarize study material."""
    print(f"  [Tool: Summarizer] Summarizing content...")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"""Summarize this study material concisely:
{text}

Extract:
- Main topic
- 5 key points
- Important terms
- What to remember for exams"""
    )
    return response.text


# ─────────────────────────────────────────
# THE AGENT BRAIN
# This is what makes it an "agent"
# It reads the user message and decides
# which tool to call automatically
# ─────────────────────────────────────────

def agent_decide(user_message):
    """
    Agent brain — decides which tool to use.
    Sends user message to LLM and asks it to pick a tool.
    Returns a JSON decision with tool name and parameters.
    """
    decision_prompt = f"""You are an AI agent for an academic tutor app.
A student said: "{user_message}"

You have these tools available:
1. explain — explains a topic (needs: topic)
2. quiz — generates quiz questions (needs: topic, optional: num questions)
3. calculator — solves math problems (needs: problem)
4. study_planner — creates study plan (needs: topic, optional: days)
5. summarizer — summarizes text (needs: text)
6. none — just chat normally, no tool needed

Decide which tool to use based on the student's intent.

Reply with ONLY a JSON object like this:
{{"tool": "explain", "params": {{"topic": "Newton's Laws"}}}}
or
{{"tool": "quiz", "params": {{"topic": "OOP", "num": 3}}}}
or
{{"tool": "calculator", "params": {{"problem": "find velocity if distance=100m time=5s"}}}}
or
{{"tool": "study_planner", "params": {{"topic": "Data Structures", "days": 5}}}}
or
{{"tool": "summarizer", "params": {{"text": "paste text here"}}}}
or
{{"tool": "none", "params": {{}}}}

Reply with ONLY the JSON. No explanation. No markdown."""

    response = client.models.generate_content(
        model=MODEL,
        contents=decision_prompt
    )

    # Clean the response and parse JSON
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        decision = json.loads(raw)
        return decision
    except json.JSONDecodeError:
        # If parsing fails, default to no tool
        return {"tool": "none", "params": {}}


def agent_execute(decision, user_message):
    """
    Execute the tool the agent decided to use.
    Returns the tool's output.
    """
    tool = decision.get("tool", "none")
    params = decision.get("params", {})

    if tool == "explain":
        topic = params.get("topic", user_message)
        return tool_explain(topic)

    elif tool == "quiz":
        topic = params.get("topic", user_message)
        num = params.get("num", 3)
        return tool_quiz(topic, num)

    elif tool == "calculator":
        problem = params.get("problem", user_message)
        return tool_calculator(problem)

    elif tool == "study_planner":
        topic = params.get("topic", user_message)
        days = params.get("days", 5)
        return tool_study_planner(topic, days)

    elif tool == "summarizer":
        text = params.get("text", user_message)
        return tool_summarizer(text)

    else:
        # No tool — just chat normally
        print("  [Agent: Chatting normally]")
        response = client.models.generate_content(
            model=MODEL,
            contents=f"You are a helpful academic tutor. Student says: {user_message}"
        )
        return response.text


def run_agent(user_message):
    """
    Full agent pipeline:
    1. Read user message
    2. Decide which tool to use
    3. Execute that tool
    4. Return result
    """
    print(f"\n  [Agent thinking...]")

    # Step 1: Agent decides
    decision = agent_decide(user_message)
    print(f"  [Agent decided: {decision['tool']}]")

    # Step 2: Execute the tool
    result = agent_execute(decision, user_message)

    return result, decision["tool"]


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 55)
    print("   AI Academic Tutor — Step 9: Agents & Tools")
    print("=" * 55)
    print("Just talk naturally — the agent picks the right tool!")
    print()
    print("Try saying things like:")
    print("  'Explain recursion to me'")
    print("  'Quiz me on OOP'")
    print("  'Solve: if F=10N and m=2kg, find acceleration'")
    print("  'Help me plan 5 days of study for databases'")
    print("  'What is photosynthesis?' (just a question)")
    print()
    print("Type 'quit' to exit")
    print("=" * 55)

    while True:
        print()
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        # Run the agent
        result, tool_used = run_agent(user_input)

        print(f"\n[Agent used: {tool_used} tool]\n")
        print(result)


if __name__ == "__main__":
    main()