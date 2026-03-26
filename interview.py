import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()

CORE_QUESTIONS = [
    # Who they are & how they got here
    "Give me a quick picture of your background — where you grew up, how you got into your field, and where you are now.",
    "Was there a person or a moment early on that pointed you toward the work you do today?",

    # How they work (the core — richest signal for simulation)
    "Walk me through how you actually do your job day-to-day. Not the job description — how do YOU approach it?",
    "Tell me about a time your work got genuinely hard — a situation that tested you. What happened and how did you handle it?",
    "How do you handle it when someone you're working with is resistant, difficult, or just not responding the way you'd hope?",

    # What drives their judgment & values
    "What does good work look like to you? How do you know when you've done something well?",
    "When you hit a situation where there's no clear right answer, how do you decide what to do?",
]

FOLLOW_UP_SYSTEM = "You are a warm, skilled interviewer. Your only job right now is to decide the single best next move in this conversation."

# Phrases that signal the participant is done or unwilling — skip the LLM and move on immediately
DISENGAGEMENT_PHRASES = [
    "i don't know", "i dont know", "i don't remember", "i dont remember",
    "not sure", "can't think", "cant think", "no idea",
    "move on", "next question", "skip", "pass",
    "too much", "too hard", "don't want to", "dont want to",
    "i already answered", "already said",
]


def is_disengaged(answer: str) -> bool:
    """Return True if the answer signals the participant is done or unwilling."""
    lowered = answer.lower().strip()
    # Very short dismissive answers (6 words or fewer)
    if len(lowered.split()) <= 6:
        for phrase in DISENGAGEMENT_PHRASES:
            if phrase in lowered:
                return True
    # Explicit move-on requests regardless of length
    for phrase in ["move on", "next question", "skip", "pass"]:
        if phrase in lowered:
            return True
    return False


def build_follow_up_prompt(core_question, exchange_so_far):
    return f"""You are interviewing someone. The main question being discussed is:
"{core_question}"

Here is the conversation so far on this topic:
{exchange_so_far}

Your task: decide the single best next move.

Ask ONE short follow-up question if:
- The person mentioned something specific but didn't elaborate on it
- There is a concrete thread worth pulling on (a story, a relationship, a decision)
- The answer was vague or general when something specific would reveal more

Reply with exactly the word MOVE_ON if:
- The person gave a full, rich answer
- The topic feels naturally complete
- The last answer was short but definitive — they said what they had to say
- Another question would feel pushy or repetitive
- The person signals they have nothing more to add ("that's it", "not much else", "already said")

Critical rules:
- Do NOT ask about something the participant has already addressed in the
  exchange above, even if their answer was brief — that ground is closed
- Do NOT rephrase or re-ask a question that was already asked above
- If the only threads left are ones already covered, reply MOVE_ON

Output format:
- If asking a follow-up: write ONLY the question, nothing else. No labels, no preamble.
- If moving on: write ONLY the word MOVE_ON, nothing else.
Your entire response must be one of those two things."""


def get_follow_up_or_move_on(core_question, exchange_so_far):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": FOLLOW_UP_SYSTEM},
            {"role": "user", "content": build_follow_up_prompt(core_question, exchange_so_far)},
        ],
        temperature=0.5,
        max_completion_tokens=100,
        top_p=1,
        stream=False,
    )
    return response.choices[0].message.content.strip()


def save_transcript(name, exchanges):
    """Save whatever exchanges exist. Called on both normal exit and Ctrl+C."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    lines = [
        "INTERVIEW TRANSCRIPT",
        f"Participant: {name}",
        f"Date: {date_str}",
        f"Total exchanges: {len(exchanges)}",
        "=================================================================",
        "",
    ]
    for i, (q, a) in enumerate(exchanges, 1):
        lines.append(f"[{i}] INTERVIEWER: {q}")
        lines.append(f"     PARTICIPANT: {a}")
        lines.append("")

    os.makedirs("transcripts", exist_ok=True)
    safe_name = name.lower().replace(" ", "_")
    filename = f"transcripts/transcript_{safe_name}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(lines))

    return filename


def main():
    print("\n=== INTERVIEW START ===")
    print("(Press Ctrl+C at any time to exit and save what you have)\n")

    name = input("Participant name: ").strip()
    if not name:
        name = "Unknown"

    exchanges = []

    try:
        for core_q in CORE_QUESTIONS:
            print(f"\nINTERVIEWER: {core_q}")
            answer = input("YOU: ").strip()
            if not answer:
                answer = "(no answer)"
            exchanges.append((core_q, answer))

            # Don't spend an API call if they're already disengaged
            if is_disengaged(answer):
                continue

            exchange_so_far = f"INTERVIEWER: {core_q}\nPARTICIPANT: {answer}"
            follow_ups_asked = 0

            while follow_ups_asked < 3:
                decision = get_follow_up_or_move_on(core_q, exchange_so_far)

                if "MOVE_ON" in decision.upper():
                    break

                follow_up_q = decision
                print(f"\nINTERVIEWER: {follow_up_q}")
                follow_up_a = input("YOU: ").strip()
                if not follow_up_a:
                    follow_up_a = "(no answer)"

                exchanges.append((follow_up_q, follow_up_a))
                exchange_so_far += f"\nINTERVIEWER: {follow_up_q}\nPARTICIPANT: {follow_up_a}"
                follow_ups_asked += 1

                # Check disengagement after each follow-up too
                if is_disengaged(follow_up_a):
                    break

    except KeyboardInterrupt:
        print("\n\n(Interview interrupted — saving what was captured...)")

    if not exchanges:
        print("No exchanges recorded. Nothing saved.")
        return

    filename = save_transcript(name, exchanges)
    print(f"\n=== INTERVIEW {'COMPLETE' if len(exchanges) > 0 else 'ENDED EARLY'} ===")
    print(f"Transcript saved to: {filename}")
    print(f"Total exchanges: {len(exchanges)}")


if __name__ == "__main__":
    main()