## Version 2 — 2026-03-24 — Aligned to professional behavioral questions

Sections rewritten to match new interview question set:
- Replaced "Work & Career" with "HOW THEY WORK" (method, not job description)
- Added "HOW THEY HANDLE DIFFICULTY" (specific situations + response patterns)
- Added "HOW THEY HANDLE PEOPLE" (friction, feedback, conflict)
- Replaced "Values & Beliefs" with "DECISION-MAKING & JUDGMENT"
- Added "WHAT GOOD LOOKS LIKE TO THEM" (standards, pride, rejection)
- Added "KEY QUOTES" — direct quotes to preserve voice for agent simulation
- Added "GAPS & LIMITATIONS" — explicit flags for what agent shouldn't invent

temperature: 1.0 → 0.3 (structured extraction needs consistency, not creativity)


## Version 1 — 2026-03-23 — Initial version

Summarizer prompt sent to `meta-llama/llama-4-scout-17b-16e-instruct` as the user message.
Model params: temperature=1, max_completion_tokens=2000, stream=False.

```
You are analyzing an interview transcript to build a detailed memory
profile of the person interviewed. Your output will be used as the
sole knowledge base for an AI agent simulating this person.

Extract and structure the following from the transcript:

BACKGROUND
- Where they grew up, key details about their upbringing
- Major life events and turning points
- How they got to where they are today

WORK & CAREER
- What they do and how they got there
- What their work means to them
- Their ambitions and future plans

VALUES & BELIEFS
- Their core values and principles
- Their worldview and what they care about deeply
- Their concerns or hopes about the world

PERSONALITY SIGNALS
- How they communicate (formal/casual, verbose/concise)
- Recurring themes or phrases in how they talk
- Emotional patterns (optimistic, guarded, reflective, etc.)

KEY OPINIONS
- Specific strong opinions they expressed on any topic
- Things they said they believe, want, or reject

IMPORTANT:
- Use their actual words and phrases where possible
- Note things they were vague or evasive about
- If something wasn't covered in the interview, say "not discussed"
- Do NOT invent or infer beyond what they actually said

Transcript:
{transcript}
```
