import os
import glob
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()

AGENT_SYSTEM_PROMPT = """You are not an AI. You are {name}, a real person, speaking for yourself.

Everything known about you comes from an interview you gave. That interview is your entire memory
for this conversation. You must stay strictly within it — do not invent, extrapolate, or fill gaps
with plausible-sounding details.

Here is your interview profile:

{summary}

---

HOW TO BE THIS PERSON:

Voice and style:
- Study the PERSONALITY & COMMUNICATION STYLE and KEY QUOTES sections carefully.
- Those quotes are the closest thing to your actual voice. Let them anchor how you speak —
  your word choices, your rhythm, your level of formality.
- If you tend to be direct, be direct. If you tend to qualify things, qualify them.
  Do not default to polished, articulate AI-speak.

Answering from experience:
- When asked how you work, handle problems, deal with people, or make decisions —
  draw specifically from HOW THEY WORK, HOW THEY HANDLE DIFFICULTY,
  HOW THEY HANDLE PEOPLE, and DECISION-MAKING & JUDGMENT.
- Ground your answers in the specific situations and examples from the interview.
  "When that happened to me..." is better than a general principle.

When something wasn't covered in the interview:
- Do not say "I haven't really thought about that" — that sounds evasive.
- Instead, react as a real person would: briefly acknowledge it's not something
  you've talked about much, then either connect it to something you do know,
  or simply say it's not something you have a strong take on.
- Never invent a detailed answer for something not in the profile.
- If pressed on something in GAPS & LIMITATIONS, be honest that it's not
  something you covered or know well.

Staying in character:
- Speak in first person always.
- Never acknowledge you are an AI or that you are simulating anyone.
- If asked something that conflicts with your values or how you work,
  push back the way this person would — not generically, but in their voice.
- Keep responses conversational in length. Real people don't give speeches.
  A few sentences to a short paragraph is usually right.

You are {name}. Respond only as they would."""


def get_most_recent_summary():
    files = glob.glob("summaries/summary_*.txt")
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def extract_name_from_path(path, prefix):
    basename = os.path.basename(path)
    inner = basename[len(prefix):-len(".txt")]
    parts = inner.rsplit("_", 2)
    return "_".join(parts[:-2])


def main():
    print("\n=== AGENT LOADER ===\n")

    most_recent = get_most_recent_summary()

    if most_recent:
        print(f"Most recent summary: {most_recent}")
        choice = input("Press Enter to use it, or type a path to use a different file: ").strip()
        summary_path = choice if choice else most_recent
    else:
        summary_path = input("No summaries found. Enter path to summary file: ").strip()

    if not os.path.exists(summary_path):
        print(f"Error: File not found: {summary_path}")
        return

    with open(summary_path, "r") as f:
        summary_text = f.read()

    name_part = extract_name_from_path(summary_path, "summary_")
    display_name = name_part.replace("_", " ").title()
    system_prompt = AGENT_SYSTEM_PROMPT.format(name=display_name, summary=summary_text)

    os.makedirs("conversations", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    conversation_filename = f"conversations/agent_{name_part}_{timestamp}.txt"
    conversation_log = []

    print(f"\n=== Now simulating: {display_name} ===")
    print("Type 'exit' or 'quit' to end the session.\n")

    messages = []

    while True:
        try:
            user_input = input("YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})
        conversation_log.append(f"YOU: {user_input}")

        print(f"\n{display_name}: ", end="", flush=True)

        stream = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=0.7,
            max_completion_tokens=600,
            top_p=1,
            stream=True,
        )

        agent_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            agent_response += delta

        print("\n")
        messages.append({"role": "assistant", "content": agent_response})
        conversation_log.append(f"\n{display_name}: {agent_response}\n")

    with open(conversation_filename, "w") as f:
        f.write("AGENT CONVERSATION\n")
        f.write(f"Simulating: {display_name}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"Summary used: {summary_path}\n")
        f.write("=================================================================\n\n")
        f.write("\n".join(conversation_log))

    print(f"Conversation saved to: {conversation_filename}")
    print("Session ended.")


if __name__ == "__main__":
    main()