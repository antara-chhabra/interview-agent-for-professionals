# Generative Agent Prototype

## Project Overview
We are building a 3-script Python prototype that simulates a real person 
using LLM-powered agents, inspired by the Stanford paper "Generative Agent 
Simulations of 1,000 People" (Park et al., 2024).

The core idea: conduct a rich text interview with a person → compress the 
transcript into a structured memory → use that memory as an LLM system prompt 
so the agent responds as that person would.

## Team Context
- 4 people, working remotely, each building their own prototype
- All vibe coding with AI assistance
- No frontend needed — terminal only
- Working in Antigravity IDE (Google, VSCode-based)
- Goal: working prototype in ~2 hours

## Tech Stack
- Python 3, plain .py files (no Jupyter)
- Groq API for all LLM calls (free tier)
- groq Python SDK
- python-dotenv for API key management
- No other dependencies unless absolutely necessary

## API Key Setup
- Store in .env file as GROQ_API_KEY=your_key_here
- Load with python-dotenv in every script
- Never hardcode the key

## Models (Groq)
Each script uses a different model based on its needs:

- interview.py  → llama-3.1-8b-instant
  Reason: makes up to 24 API calls per interview (8 questions × 3 follow-ups).
  Needs high RPD (14.4K/day) and speed over quality.

- summarize.py  → meta-llama/llama-4-scout-17b-16e-instruct
  Reason: one call per run, needs to compress a long transcript well.
  Quality matters more than speed.

- agent.py      → meta-llama/llama-4-scout-17b-16e-instruct
  Reason: quality of agent responses is the whole point. High TPM (30K)
  handles a large summary in context.

## File Structure
```
/project-root
  CLAUDE.md
  interview.py
  summarize.py
  agent.py
  /transcripts        # interview.py saves here
  /summaries          # summarize.py saves here
  /prompts            # version-controlled prompt iterations
    interview_prompts.md
    summarizer_prompts.md
    agent_prompts.md
  requirements.txt
  .env
```

## The 3 Scripts

### Script 1 — interview.py
Purpose: Conduct a 15-25 minute structured text interview in the terminal.
Input: None (user types answers live)
Output: /transcripts/transcript_{name}_{timestamp}.txt

Logic:
1. Ask user for participant name
2. Loop through 8 core questions in order
3. After each answer, call LLM to decide: ask a follow-up OR move on
4. Max 3 follow-ups per core question
5. Every Q&A pair appended to transcript list
6. At end, save transcript to /transcripts/

The 8 core questions cover 3 topics:
- Life story & background (3 questions)
  Q1: "Let's start from the beginning. Tell me the story of your life —
       where did you grow up, and what was that like for you?"
  Q2: "Were there any people, experiences, or turning points growing up
       that really shaped who you are today?"
  Q3: "How did you get from where you started to where you are now?
       Walk me through the major chapters."

- Work & career (3 questions)
  Q4: "Tell me about your work. What do you do, and how did you end up
       doing it? Was it something you planned, or did it evolve?"
  Q5: "What does your work mean to you beyond just a job? Does it connect
       to something bigger, or is it more of a means to an end?"
  Q6: "If you imagine yourself five or ten years from now, what does your
       working life look like — and is that something you're actively
       working toward?"

- Values & beliefs (2 questions)
  Q7: "What do you believe in most deeply — the values or principles that
       really guide how you live and make decisions?"
  Q8: "Is there something about the world — the way things are or the
       direction things are heading — that you feel strongly about,
       either hopeful or concerned?"

Follow-up prompt (used after every answer — THIS IS THE KEY TUNING LEVER):
```
You are a warm, curious interviewer conducting a life interview.
The current topic question was: "{core_question}"

Here is the exchange so far on this topic:
{exchange_so_far}

Decide what to do next.

Option A — Reply with ONE follow-up question if:
- The person mentioned something interesting but did not elaborate
- There is a meaningful thread worth pulling on
- The answer felt surface-level or incomplete

Option B — Reply with exactly the word MOVE_ON if:
- The person gave a thorough, rich answer
- The topic feels naturally complete
- Another follow-up would feel forced or repetitive

Rules:
- If following up, write ONLY the question. No preamble, no label.
- Keep follow-ups short, conversational, specific to what they said.
- Stay within the current topic. Do not introduce new subjects.
- Reply with ONLY the question or ONLY the word MOVE_ON.
```

Transcript output format:
```
INTERVIEW TRANSCRIPT
Participant: {name}
Date: {date}
Total exchanges: {n}
=================================================================

[1] INTERVIEWER: {question}
     PARTICIPANT: {answer}

[2] INTERVIEWER: {follow-up}
     PARTICIPANT: {answer}
...
```

### Script 2 — summarize.py
Purpose: Compress a raw transcript into structured agent memory.
Input: path to a transcript .txt file (user provides via terminal prompt
       OR auto-detects the most recent file in /transcripts/)
Output: /summaries/summary_{name}_{timestamp}.txt

Logic:
1. Load the transcript file
2. Send full transcript to LLM with summarizer prompt
3. Save structured summary to /summaries/

Summarizer prompt (THIS IS A KEY TUNING LEVER):
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

### Script 3 — agent.py
Purpose: Load a summary and simulate that person in a terminal chat loop.
Input: path to a summary .txt file (user provides via terminal prompt
       OR auto-detects most recent in /summaries/)
Output: live terminal conversation (nothing saved unless we add logging)

Logic:
1. Load summary file
2. Build system prompt from summary
3. Open a while True chat loop
4. Each user message + full conversation history sent to LLM
5. Type "exit" or "quit" to end session

Agent system prompt (THIS IS THE MOST IMPORTANT TUNING LEVER):
```
You are simulating a real person based on an interview transcript.
You must respond exactly as this person would — using their vocabulary,
their reasoning style, their values, and their personality.

Here is everything known about this person:

{summary}

Rules for staying in character:
- Speak in first person as this person, always
- Match their communication style (formal/casual, how they structure thoughts)
- If asked about something not covered in the summary, say something like
  "I haven't really thought about that" or "I'm not sure" — do NOT invent
- If asked something that contradicts their values, push back as they would
- Do not break character to explain that you are an AI
- Do not add information beyond what the summary contains
- Keep responses conversational, not overly long

You are not an assistant. You are this person. Respond only as they would.
```

Conversation loop behavior:
- Print a short intro when loaded: who the agent is simulating
- Each exchange: user types → agent responds
- Maintain full conversation history for context
- Type "exit" or "quit" to end

## How to Run (in order)
```bash
python interview.py       # Step 1: conduct interview, saves transcript
python summarize.py       # Step 2: summarize transcript, saves summary
python agent.py           # Step 3: chat with the agent
```

## Iteration & Self-Improvement
Prompt versions are tracked in /prompts/:
- interview_prompts.md  — versions of the follow-up prompt
- summarizer_prompts.md — versions of the summarizer prompt
- agent_prompts.md      — versions of the agent system prompt

When changing a prompt, save the old version with a note before replacing.
Format: ## Version N — [date] — [what changed and why]

## What Good Looks Like
The agent is working well when:
- It answers questions in a way the real person would recognize as themselves
- It declines to answer things not covered in the interview rather than inventing
- Its communication style matches the actual person's (not generic AI tone)
- Follow-up questions in the interview feel natural, not robotic

## Known Constraints
- Free Groq tier: 14.4K RPD for llama-3.1-8b-instant, 1K RPD for scout model
- One full interview uses ~20-24 API calls on Script 1
- Scout model RPD limit (1K/day) means limit agent testing sessions
- If hitting rate limits: add time.sleep(2) between API calls in interview.py

## Plan Mode Instructions for Claude Code
When starting this project in plan mode, ask me about:
1. Any changes to the core questions before building
2. Whether to auto-detect most recent file or always prompt for file path
3. Whether to add conversation logging to agent.py
4. Any Groq SDK specifics I should know about my setup
5. Whether requirements.txt should pin versions



Getting Your Groq API Key
On the Groq website, go to the left sidebar and look for "API Keys" — create a new key and copy it. Then in your .env file it's just:
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxx
That's literally the whole file. One line.

What That Playground Code Means
That's Groq showing you exactly how to call their API in Python. It's useful — add this to your CLAUDE.md under a new section so Claude Code knows the exact syntax to use:
markdown## Groq SDK Usage
The Groq API works like this (from their playground):

from groq import Groq

client = Groq()  # automatically reads GROQ_API_KEY from .env
completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "your system prompt here"},
        {"role": "user", "content": "user message here"}
    ],
    temperature=1,
    max_completion_tokens=8192,
    top_p=1,
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
This tells Claude Code exactly what the API calls should look like so it doesn't guess.

Two things to note from that code that matter for your project:
stream=True means the response prints word by word as it generates, which feels much more natural in a terminal chat. Keep that for the agent script especially.
client = Groq() automatically picks up your key from the .env file as long as you load it with python-dotenv first — so the key never appears in your actual code.does the sdk usage not change based on needs and model used11:06 PMYes, good catch. The playground is just showing you a generic template. Here's what actually changes per script:
model — obviously different per script as we decided:

interview.py → "llama-3.1-8b-instant"
summarize.py and agent.py → "meta-llama/llama-4-scout-17b-16e-instruct"

stream — should differ:

interview.py → stream=False — you need the full response back as a string to check if it says MOVE_ON or contains a follow-up question. Streaming makes that harder to parse.
summarize.py → stream=False — same reason, you need the full summary as a string to save to a file.
agent.py → stream=True — this is the one the user actually watches, so word-by-word streaming feels natural.

max_completion_tokens — should differ:

interview.py → small, like 150. Follow-up questions should be short. No reason to allow a 8000 token response for a single question.
summarize.py → larger, like 2000. The summary needs room to be thorough.
agent.py → medium, like 500-800. Conversational responses, not essays.

temperature — worth considering:

interview.py → slightly lower like 0.7 so follow-ups are sensible and on-topic
agent.py → slightly lower like 0.7 so the agent stays consistent in character rather than getting creative

reasoning_effort — that parameter is specific to certain models like the openai/gpt-oss ones in the playground screenshot. The Llama models you're using don't support it, so just leave it out entirely or Claude Code will get an error.
Add all of this to the Groq SDK section in your CLAUDE.md so Claude Code has the full picture.