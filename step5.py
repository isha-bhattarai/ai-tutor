# step5.py — Role Prompting
# ==========================
# Role prompting = giving the AI a persona through the system prompt
# Same question gets completely different answers depending on active role
# The role lives in the system instruction — invisible to user but shapes everything

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"
# ─────────────────────────────────────────
# ROLE DEFINITIONS
# Each role has a name and a system prompt
# The system prompt is the "character brief"
# ─────────────────────────────────────────

ROLES = {
    "1": {
        "name": "Teacher",
        "description": "explains concepts clearly and simply",
        "system": """You are a warm, patient and encouraging university teacher.
Your goal is to TEACH, not just answer.

When a student asks about a topic:
1. Start with a simple real-world analogy to build intuition
2. Explain the concept clearly, step by step
3. Use simple language — define any technical terms immediately
4. End with a KEY TAKEAWAY in one sentence
5. Offer to explain further if anything is unclear

Tone: Friendly, supportive, never condescending."""
    },

    "2": {
        "name": "Examiner",
        "description": "gives exam-style questions and model answers",
        "system": """You are a strict but fair academic examiner preparing students for exams.

When a student asks about a topic:
1. Present the topic as an exam question with marks allocated
2. Give a complete model answer showing exactly what gets marks
3. List 3 common mistakes students make on this topic
4. Give 2 practice questions at the end
5. State the difficulty: Easy / Medium / Hard

Tone: Formal, precise, exam-focused. Use academic language."""
    },

    "3": {
        "name": "Study Coach",
        "description": "gives study plans and motivation",
        "system": """You are an energetic and motivational study coach.

When a student asks about a topic or learning goal:
1. Acknowledge their effort positively
2. Break the topic into a clear 3-5 day study plan
3. Suggest specific study techniques (Pomodoro, spaced repetition, mind maps)
4. Recommend specific resources (YouTube channels, websites, books)
5. End with a short motivational message

Tone: Energetic, positive, action-oriented. Use bullet points and short sentences."""
    },

    "4": {
        "name": "Subject Expert",
        "description": "gives advanced, in-depth explanations",
        "system": """You are a PhD-level subject matter expert in academia.

The student has a strong foundation and wants depth.

When a student asks about a topic:
1. Skip basic definitions — assume they know the fundamentals
2. Dive into nuances, edge cases and advanced applications
3. Connect the concept to real research or modern industry use cases
4. Use precise technical terminology
5. Mention limitations, open problems or ongoing debates in the field

Tone: Academic, thorough, intellectually rigorous."""
    }
}


# ─────────────────────────────────────────
# CORE FUNCTION
# ─────────────────────────────────────────

def ask_role(user_message, role_key, conversation_history):
    """
    Send a message using the selected role's system prompt.
    The role shapes everything — same question, different answer.
    """
    role = ROLES[role_key]

    contents = conversation_history + [
        {"role": "user", "parts": [{"text": user_message}]}
    ]

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config={"system_instruction": role["system"]}
    )

    reply = response.text
    return reply


def show_roles():
    """Display the role selection menu."""
    print("\n" + "=" * 50)
    print("  Select your tutor role:")
    print("=" * 50)
    for key, role in ROLES.items():
        print(f"  {key}. {role['name']} — {role['description']}")
    print("=" * 50)


def select_role():
    """Let user pick a role and return the key."""
    show_roles()
    while True:
        choice = input("Enter 1-4: ").strip()
        if choice in ROLES:
            selected = ROLES[choice]
            print(f"\n[Role set to: {selected['name']}]\n")
            return choice
        print("Invalid. Enter 1, 2, 3 or 4.")


def main():
    print("=" * 50)
    print("   AI Academic Tutor — Step 5: Role Prompting")
    print("=" * 50)
    print("Commands:")
    print("  'role'    — switch to a different role")
    print("  'clear'   — clear conversation history")
    print("  'quit'    — exit")
    print("=" * 50)

    current_role = select_role()
    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye! Keep studying!")
            break

        if user_input.lower() == "role":
            current_role = select_role()
            conversation_history = []
            print("[History cleared for new role]\n")
            continue

        if user_input.lower() == "clear":
            conversation_history = []
            print("[Conversation cleared]\n")
            continue

        reply = ask_role(user_input, current_role, conversation_history)

        conversation_history.append({"role": "user", "parts": [{"text": user_input}]})
        conversation_history.append({"role": "model", "parts": [{"text": reply}]})

        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

        role_name = ROLES[current_role]["name"]
        print(f"\n[{role_name}]: {reply}\n")


if __name__ == "__main__":
    main()