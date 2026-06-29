# step10.py — Final Integration
# ==============================
# All 9 modules combined into one complete console application
# This is the finished AI Academic Tutor

from google import genai
from dotenv import load_dotenv
import os
import json
from datetime import date

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"
MEMORY_FILE = "memory.json"


# ════════════════════════════════════════
# MEMORY SYSTEM (Step 8)
# ════════════════════════════════════════

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {
        "name": None,
        "sessions": 0,
        "topics_studied": [],
        "weak_topics": [],
        "strong_topics": [],
        "last_seen": None,
        "total_questions_asked": 0
    }


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def get_greeting(memory):
    if memory["sessions"] == 1:
        return f"Welcome, {memory['name']}! This is your first session. Let's start learning!"
    msg = f"Welcome back, {memory['name']}! Session #{memory['sessions']}. "
    if memory["topics_studied"]:
        msg += f"Last studied: {', '.join(memory['topics_studied'][-3:])}."
    if memory["weak_topics"]:
        msg += f" Topics to revisit: {', '.join(memory['weak_topics'])}."
    return msg


# ════════════════════════════════════════
# CORE CHAT (Step 1)
# ════════════════════════════════════════

def send_prompt(prompt, system=None):
    """Base function — sends any prompt to Gemini."""
    config = {"system_instruction": system} if system else {}
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config
    )
    return response.text


# ════════════════════════════════════════
# ZERO-SHOT (Step 2)
# ════════════════════════════════════════

def explain_topic(topic):
    prompt = f"""You are an academic tutor.
Explain '{topic}' clearly for a university student.
Structure: Definition → How it works → Real example → Key takeaway.
Keep under 250 words."""
    return send_prompt(prompt)


def summarize_text(text):
    prompt = f"""Summarize this study material:
{text}
Give: main topic, 5 key points, important terms, exam tips."""
    return send_prompt(prompt)


# ════════════════════════════════════════
# FEW-SHOT (Step 3)
# ════════════════════════════════════════

def generate_quiz(topic, num=3, difficulty="medium"):
    prompt = f"""Generate {num} MCQ questions about {topic}.
Difficulty: {difficulty}

Format each as:
Q[n]: [question]
A) B) C) D) [options]
Correct Answer: [letter]
Explanation: [one sentence]
---"""
    return send_prompt(prompt)


def evaluate_answer(question, answer):
    prompt = f"""Evaluate this student answer:
Question: {question}
Answer: {answer}

Give:
Category: Excellent/Good/Needs Work
Score: X/10
What was correct:
What was missing:
Feedback:"""
    return send_prompt(prompt)


# ════════════════════════════════════════
# CHAIN-OF-THOUGHT (Step 4)
# ════════════════════════════════════════

def solve_problem(problem):
    prompt = f"""Solve this step by step:
{problem}

Structure:
UNDERSTANDING: what is given, what to find
FORMULA/CONCEPT: what applies
STEP BY STEP SOLUTION: numbered steps
FINAL ANSWER: clear answer with units
VERIFICATION: quick check"""
    return send_prompt(prompt)


# ════════════════════════════════════════
# ROLE PROMPTING (Step 5)
# ════════════════════════════════════════

ROLES = {
    "1": {"name": "Teacher",
          "system": "You are a warm patient university teacher. Explain with analogies, simple language, and end with a key takeaway."},
    "2": {"name": "Examiner",
          "system": "You are a strict academic examiner. Give exam questions, model answers, common mistakes, and practice questions."},
    "3": {"name": "Study Coach",
          "system": "You are a motivational study coach. Give study plans, techniques, resources, and encouragement."},
    "4": {"name": "Subject Expert",
          "system": "You are a PhD expert. Give advanced, technical, in-depth responses with research connections."}
}


def ask_with_role(message, role_key, history):
    role = ROLES[role_key]
    contents = history + [{"role": "user", "parts": [{"text": message}]}]
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config={"system_instruction": role["system"]}
    )
    reply = response.text
    history.append({"role": "user", "parts": [{"text": message}]})
    history.append({"role": "model", "parts": [{"text": reply}]})
    if len(history) > 20:
        history = history[-20:]
    return reply, history


# ════════════════════════════════════════
# LANGCHAIN PIPELINE (Step 7)
# ════════════════════════════════════════

def run_study_chain(topic):
    """Full pipeline: Topic → Explain → Notes → Quiz → Summary"""
    print("\n  Running study pipeline...")

    print("  [1/4] Explaining topic...")
    explanation = send_prompt(
        f"Explain '{topic}' clearly for a university student in 150 words.")

    print("  [2/4] Creating notes...")
    notes = send_prompt(
        f"Convert this explanation into 5 bullet revision notes:\n{explanation}")

    print("  [3/4] Generating quiz...")
    quiz = send_prompt(
        f"Generate 2 MCQ questions based on these notes:\n{notes}")

    print("  [4/4] Final summary...")
    summary = send_prompt(
        f"Write a 3-sentence motivating summary of what was learned about {topic}.")

    return explanation, notes, quiz, summary


# ════════════════════════════════════════
# AGENT (Step 9)
# ════════════════════════════════════════

def run_agent(user_message):
    """Agent decides which tool to use automatically."""
    decision_prompt = f"""You are an AI agent for an academic tutor.
Student said: "{user_message}"

Available tools:
- explain: explain a topic
- quiz: generate quiz questions
- calculator: solve math/physics
- study_planner: create study plan
- summarizer: summarize text
- chat: general conversation

Reply with ONLY JSON:
{{"tool": "explain", "topic": "recursion"}}
or {{"tool": "quiz", "topic": "OOP", "num": 3}}
or {{"tool": "calculator", "problem": "find speed"}}
or {{"tool": "study_planner", "topic": "databases", "days": 5}}
or {{"tool": "chat"}}"""

    raw = send_prompt(decision_prompt)
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        decision = json.loads(raw)
    except:
        decision = {"tool": "chat"}

    tool = decision.get("tool", "chat")
    print(f"  [Agent selected: {tool}]")

    if tool == "explain":
        return send_prompt(f"Explain '{decision.get('topic', user_message)}' clearly.")
    elif tool == "quiz":
        return generate_quiz(decision.get("topic", user_message), decision.get("num", 3))
    elif tool == "calculator":
        return solve_problem(decision.get("problem", user_message))
    elif tool == "study_planner":
        return send_prompt(
            f"Create a {decision.get('days', 5)}-day study plan for: {decision.get('topic', user_message)}")
    elif tool == "summarizer":
        return summarize_text(user_message)
    else:
        return send_prompt(f"You are a helpful academic tutor. {user_message}")


# ════════════════════════════════════════
# MAIN APPLICATION
# ════════════════════════════════════════

def main():
    print("=" * 55)
    print("   AI ACADEMIC TUTOR — Complete System")
    print("   Powered by Google Gemini")
    print("=" * 55)

    # Load memory
    memory = load_memory()

    # First time setup
    if memory["name"] is None:
        name = input("Hello! What's your name? ").strip()
        memory["name"] = name

    # Update session
    memory["sessions"] += 1
    memory["last_seen"] = str(date.today())
    save_memory(memory)

    # Greeting
    print(f"\n{get_greeting(memory)}\n")

    # Main menu
    while True:
        print("\n" + "=" * 55)
        print("  MAIN MENU")
        print("=" * 55)
        print("  1. Smart Agent    — just talk, AI picks the tool")
        print("  2. Explain Topic  — zero-shot explanation")
        print("  3. Generate Quiz  — few-shot quiz generation")
        print("  4. Solve Problem  — chain-of-thought reasoning")
        print("  5. Role Mode      — choose tutor personality")
        print("  6. Study Pipeline — full topic study chain")
        print("  7. Evaluate Answer— get feedback on your answer")
        print("  8. My Profile     — view learning history")
        print("  9. Quit")
        print("=" * 55)

        choice = input("\nChoose (1-9): ").strip()

        # ── Option 1: Smart Agent ──
        if choice == "1":
            print("\n[Smart Agent Mode — just talk naturally]\n")
            while True:
                msg = input("You: ").strip()
                if msg.lower() in ["back", "menu"]:
                    break
                if not msg:
                    continue
                result = run_agent(msg)
                print(f"\nTutor: {result}\n")
                memory["total_questions_asked"] += 1
                save_memory(memory)

        # ── Option 2: Explain ──
        elif choice == "2":
            topic = input("Topic to explain: ").strip()
            print("\nGenerating explanation...\n")
            print(explain_topic(topic))
            # Log to memory
            if topic.title() not in memory["topics_studied"]:
                memory["topics_studied"].append(topic.title())
                save_memory(memory)

        # ── Option 3: Quiz ──
        elif choice == "3":
            topic = input("Quiz topic: ").strip()
            num = input("Number of questions (default 3): ").strip()
            num = int(num) if num.isdigit() else 3
            diff = input("Difficulty easy/medium/hard (default medium): ").strip() or "medium"
            print("\nGenerating quiz...\n")
            print(generate_quiz(topic, num, diff))

        # ── Option 4: Solve ──
        elif choice == "4":
            print("Enter your problem:")
            problem = input("Problem: ").strip()
            print("\nSolving step by step...\n")
            print(solve_problem(problem))

        # ── Option 5: Role Mode ──
        elif choice == "5":
            print("\nSelect role:")
            for k, v in ROLES.items():
                print(f"  {k}. {v['name']}")
            role_choice = input("Choose (1-4): ").strip()
            if role_choice not in ROLES:
                print("Invalid choice.")
                continue
            role_name = ROLES[role_choice]["name"]
            print(f"\n[Role: {role_name}] Type 'back' to return to menu\n")
            history = []
            while True:
                msg = input("You: ").strip()
                if msg.lower() in ["back", "menu"]:
                    break
                if not msg:
                    continue
                reply, history = ask_with_role(msg, role_choice, history)
                print(f"\n[{role_name}]: {reply}\n")

        # ── Option 6: Study Pipeline ──
        elif choice == "6":
            topic = input("Topic for full study pipeline: ").strip()
            explanation, notes, quiz, summary = run_study_chain(topic)
            print("\n" + "=" * 55)
            print(f"  STUDY PACK: {topic.upper()}")
            print("=" * 55)
            print("\nEXPLANATION:\n" + explanation)
            print("\nNOTES:\n" + notes)
            print("\nQUIZ:\n" + quiz)
            print("\nSUMMARY:\n" + summary)
            # Save to file
            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == "y":
                fname = f"study_pack_{topic.replace(' ', '_')}.txt"
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(f"STUDY PACK: {topic.upper()}\n\n")
                    f.write("EXPLANATION:\n" + explanation + "\n\n")
                    f.write("NOTES:\n" + notes + "\n\n")
                    f.write("QUIZ:\n" + quiz + "\n\n")
                    f.write("SUMMARY:\n" + summary)
                print(f"Saved to {fname}")
            if topic.title() not in memory["topics_studied"]:
                memory["topics_studied"].append(topic.title())
                save_memory(memory)

        # ── Option 7: Evaluate Answer ──
        elif choice == "7":
            question = input("Enter the question: ").strip()
            answer = input("Enter your answer: ").strip()
            print("\nEvaluating...\n")
            print(evaluate_answer(question, answer))

        # ── Option 8: Profile ──
        elif choice == "8":
            print("\n" + "=" * 45)
            print("  YOUR LEARNING PROFILE")
            print("=" * 45)
            print(f"  Name:            {memory['name']}")
            print(f"  Sessions:        {memory['sessions']}")
            print(f"  Last seen:       {memory['last_seen']}")
            print(f"  Questions asked: {memory['total_questions_asked']}")
            print(f"  Topics studied:  {len(memory['topics_studied'])}")
            if memory["topics_studied"]:
                print(f"  → {', '.join(memory['topics_studied'])}")
            if memory["weak_topics"]:
                print(f"  Need revision:   {', '.join(memory['weak_topics'])}")
            print("=" * 45)

        # ── Option 9: Quit ──
        elif choice == "9":
            save_memory(memory)
            print(f"\nGoodbye {memory['name']}! Keep studying! 🎓")
            break

        else:
            print("Invalid choice. Enter 1-9.")


if __name__ == "__main__":
    main()