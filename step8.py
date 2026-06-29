# step8.py — Memory System
# =========================
# Memory = storing user identity and learning history permanently
# Uses JSON file as a simple database
# Data persists across sessions — program remembers you next time

from google import genai
from dotenv import load_dotenv
import os
import json
from datetime import date

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"

# Memory file — this is our "database"
MEMORY_FILE = "memory.json"


# ─────────────────────────────────────────
# MEMORY FUNCTIONS
# Load, save, update user memory
# ─────────────────────────────────────────

def load_memory():
    """
    Load memory from JSON file.
    If file doesn't exist, return empty memory (new user).
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    else:
        # New user — empty memory
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
    """
    Save memory to JSON file permanently.
    This is what makes it persist across sessions.
    """
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def update_session(memory):
    """Update session count and last seen date."""
    memory["sessions"] += 1
    memory["last_seen"] = str(date.today())
    return memory


def add_topic(memory, topic, performance=None):
    """
    Add a studied topic to memory.
    performance: 'strong', 'weak', or None
    """
    topic = topic.strip().title()

    # Add to studied topics if not already there
    if topic not in memory["topics_studied"]:
        memory["topics_studied"].append(topic)

    # Track performance
    if performance == "weak" and topic not in memory["weak_topics"]:
        memory["weak_topics"].append(topic)
    elif performance == "strong" and topic not in memory["strong_topics"]:
        memory["strong_topics"].append(topic)

    return memory


def get_greeting(memory):
    """
    Generate a personalized greeting based on memory.
    New user gets welcome message.
    Returning user gets personalized summary.
    """
    if memory["sessions"] == 1:
        return f"Welcome to AI Tutor, {memory['name']}! This is your first session. Let's start learning!"

    greeting = f"Welcome back, {memory['name']}! "
    greeting += f"Session #{memory['sessions']}. "

    if memory["topics_studied"]:
        recent = memory["topics_studied"][-3:]  # last 3 topics
        greeting += f"Last studied: {', '.join(recent)}. "

    if memory["weak_topics"]:
        greeting += f"Topics to revisit: {', '.join(memory['weak_topics'])}. "

    return greeting


# ─────────────────────────────────────────
# AI CHAT WITH MEMORY CONTEXT
# ─────────────────────────────────────────

def chat_with_memory(user_message, memory, conversation_history):
    """
    Send message to AI with full memory context injected.
    AI knows who the student is and what they've studied.
    """
    # Build memory context — this is injected into every prompt
    memory_context = f"""You are a personalized AI academic tutor.

STUDENT PROFILE:
- Name: {memory['name']}
- Total sessions: {memory['sessions']}
- Topics studied: {', '.join(memory['topics_studied']) if memory['topics_studied'] else 'None yet'}
- Strong topics: {', '.join(memory['strong_topics']) if memory['strong_topics'] else 'None yet'}
- Topics needing revision: {', '.join(memory['weak_topics']) if memory['weak_topics'] else 'None'}

Use this profile to personalize your responses:
- Address the student by name occasionally
- Reference topics they've already studied when relevant
- If they ask about a weak topic, be extra supportive
- Track their progress and encourage them"""

    # Build full message list
    contents = conversation_history + [
        {"role": "user", "parts": [{"text": user_message}]}
    ]

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config={"system_instruction": memory_context}
    )

    return response.text


def show_memory(memory):
    """Display current memory/profile to the student."""
    print("\n" + "=" * 45)
    print(f"  YOUR LEARNING PROFILE")
    print("=" * 45)
    print(f"  Name:          {memory['name']}")
    print(f"  Sessions:      {memory['sessions']}")
    print(f"  Last seen:     {memory['last_seen']}")
    print(f"  Topics studied: {len(memory['topics_studied'])}")
    if memory["topics_studied"]:
        print(f"  → {', '.join(memory['topics_studied'])}")
    if memory["strong_topics"]:
        print(f"  Strong:        {', '.join(memory['strong_topics'])}")
    if memory["weak_topics"]:
        print(f"  Need revision: {', '.join(memory['weak_topics'])}")
    print("=" * 45 + "\n")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 45)
    print("   AI Academic Tutor — Step 8: Memory")
    print("=" * 45)

    # Load existing memory
    memory = load_memory()

    # First time user — ask for name
    if memory["name"] is None:
        name = input("Hello! What's your name? ").strip()
        memory["name"] = name
        save_memory(memory)

    # Update session
    memory = update_session(memory)
    save_memory(memory)

    # Personalized greeting
    print(f"\n{get_greeting(memory)}\n")

    print("Commands:")
    print("  'profile'  — see your learning profile")
    print("  'topic'    — log a topic you just studied")
    print("  'clear'    — start fresh (reset memory)")
    print("  'quit'     — exit")
    print()

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            save_memory(memory)
            print(f"\nGoodbye {memory['name']}! Keep studying!")
            break

        if user_input.lower() == "profile":
            show_memory(memory)
            continue

        if user_input.lower() == "topic":
            topic = input("What topic did you just study? ").strip()
            performance = input("How did it go? (strong/weak/ok): ").strip().lower()
            perf = "strong" if performance == "strong" else "weak" if performance == "weak" else None
            memory = add_topic(memory, topic, perf)
            save_memory(memory)
            print(f"[Added '{topic}' to your learning history]\n")
            continue

        if user_input.lower() == "clear":
            confirm = input("Reset ALL memory? This cannot be undone. (yes/no): ")
            if confirm.lower() == "yes":
                os.remove(MEMORY_FILE)
                print("Memory cleared. Restart the program.")
                break
            continue

        # Normal chat with memory context
        memory["total_questions_asked"] += 1
        reply = chat_with_memory(user_input, memory, conversation_history)

        # Update conversation history
        conversation_history.append({"role": "user", "parts": [{"text": user_input}]})
        conversation_history.append({"role": "model", "parts": [{"text": reply}]})

        # Keep history manageable
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

        save_memory(memory)
        print(f"\nTutor: {reply}\n")


if __name__ == "__main__":
    main()