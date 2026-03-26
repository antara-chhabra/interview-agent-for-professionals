import os
import glob
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()

SUMMARIZER_PROMPT = """You are analyzing an interview transcript to build a detailed memory
profile of the person interviewed. Your output will be used as the sole knowledge base
for an AI agent simulating this person — capturing not just what they know, but how they
think, work, and behave.

Extract and structure the following from the transcript. Use their actual words and phrases
wherever possible. If something was not covered in the interview, write "not discussed."
Do NOT invent or infer beyond what they actually said.

---

BACKGROUND
- Where they grew up and key details about their upbringing
- How they got into their field — was it planned or did it evolve?
- Where they are now (role, industry, career stage)
- Any people or moments that pointed them toward this work

---

HOW THEY WORK
- How they actually approach their job day-to-day (their method, not their job description)
- What they prioritize and how they structure their work
- Any recurring habits, rituals, or tendencies they mentioned

---

HOW THEY HANDLE DIFFICULTY
- Specific situations where their work got hard — what happened and what they did
- How they respond under pressure or when things go wrong
- Whether they lean into problems or step back — and how they described it

---

HOW THEY HANDLE PEOPLE
- How they deal with resistance, difficult colleagues, or unresponsive people
- Their approach to giving feedback, managing conflict, or navigating friction
- What they said about working with others who don't meet their expectations

---

DECISION-MAKING & JUDGMENT
- How they make decisions when there's no clear right answer
- What values or principles they said guide their choices
- Any frameworks, instincts, or rules of thumb they mentioned

---

WHAT GOOD LOOKS LIKE TO THEM
- How they define doing their job well
- What they said they're proud of or what gives them satisfaction
- What they said they reject or consider bad work

---

PERSONALITY & COMMUNICATION STYLE
- How they talk: formal or casual, direct or roundabout, verbose or concise
- Their emotional tone: confident, guarded, reflective, enthusiastic, matter-of-fact, etc.
- Recurring phrases or language patterns worth noting
- Anything they were notably vague, evasive, or reluctant about

---

KEY QUOTES
- 3 to 5 direct quotes that best capture how this person sounds and thinks
- Pick quotes that reveal character, not just facts

---

GAPS & LIMITATIONS
- Topics the interview didn't cover that would matter for simulation
- Anything they refused to answer or deflected from
- Areas where the summary is thin and the agent should be cautious about

---

Transcript:
{transcript}"""


def get_most_recent_transcript():
    files = glob.glob("transcripts/transcript_*.txt")
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def extract_name_from_path(path, prefix):
    basename = os.path.basename(path)
    inner = basename[len(prefix):-len(".txt")]
    parts = inner.rsplit("_", 2)
    return "_".join(parts[:-2])


def main():
    print("\n=== SUMMARIZER ===\n")

    most_recent = get_most_recent_transcript()

    if most_recent:
        print(f"Most recent transcript: {most_recent}")
        choice = input("Press Enter to use it, or type a path to use a different file: ").strip()
        transcript_path = choice if choice else most_recent
    else:
        transcript_path = input("No transcripts found. Enter path to transcript file: ").strip()

    if not os.path.exists(transcript_path):
        print(f"Error: File not found: {transcript_path}")
        return

    with open(transcript_path, "r") as f:
        transcript_text = f.read()

    print("\nSummarizing transcript... (this may take a moment)\n")

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "user", "content": SUMMARIZER_PROMPT.format(transcript=transcript_text)},
        ],
        temperature=0.3,
        max_completion_tokens=2000,
        top_p=1,
        stream=False,
    )

    summary = response.choices[0].message.content.strip()

    name_part = extract_name_from_path(transcript_path, "transcript_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("summaries", exist_ok=True)
    filename = f"summaries/summary_{name_part}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(summary)

    print(f"Summary saved to: {filename}")
    print(f"\n--- Preview ---\n{summary[:600]}\n...")


if __name__ == "__main__":
    main()