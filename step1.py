# step1.py — LLM API Integration using Google Gemini (new SDK)
# =============================================================

from google import genai                # new SDK — replaces google.generativeai
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

# Create the client — new SDK uses this pattern
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Model to use — gemini-2.0-flash is free and current
MODEL = "gemini-3.1-flash-lite"

# System instruction — the AI's personality/role
SYSTEM = "You are a helpful and friendly academic tutor."

# Conversation history — we manage this manually with the new SDK
# Each message is a dict with "role" and "parts"
conversation_history = []


def send_message(user_message):
    """
    Send a message and get a reply.
    We manually append to conversation_history so the model has full context.
    """
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # Call the API with full history
    response = client.models.generate_content(
        model=MODEL,
        contents=conversation_history,
        config={
            "system_instruction": SYSTEM,
            "temperature": 0.7,
            "max_output_tokens": 500
        }
    )

    reply = response.text

    # Add AI reply to history too — both sides must be saved!
    conversation_history.append({
        "role": "model",        # Gemini uses "model" instead of "assistant"
        "parts": [{"text": reply}]
    })

    return reply


def show_history():
    """Print the full conversation so you can see what's being sent to the API."""
    print("\n--- Conversation History So Far ---")
    if not conversation_history:
        print("(empty)")
    for message in conversation_history:
        role = "You" if message["role"] == "user" else "Tutor"
        print(f"{role}: {message['parts'][0]['text']}")
    print("-----------------------------------\n")


def main():
    print("=" * 45)
    print("   AI Academic Tutor — Step 1")
    print("   Powered by Google Gemini (Free!)")
    print("=" * 45)
    print("Commands:")
    print("  'history' — see the full conversation")
    print("  'clear'   — start a fresh session")
    print("  'quit'    — exit")
    print("=" * 45 + "\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye! Keep studying!")
            break

        if user_input.lower() == "history":
            show_history()
            continue

        if user_input.lower() == "clear":
            conversation_history.clear()
            print("[Session cleared — fresh start]\n")
            continue

        reply = send_message(user_input)
        print(f"\nTutor: {reply}\n")


if __name__ == "__main__":
    main()