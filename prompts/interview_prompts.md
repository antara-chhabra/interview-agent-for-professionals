## Version 2 — 2026-03-24 — Professional simulation focus + leakage fix + graceful exit

CORE_QUESTIONS: 8 → 7, rewritten for professional behavioral simulation
- Kept: background, early influence, day-to-day approach, handling 
  difficulty, handling people friction, good work definition, judgment
- Cut: misconceptions (weakest simulation signal)
- Max API calls: 7 questions × 3 follow-ups = 21 worst case (within 14.4K RPD)
- Model stays llama-3.1-8b-instant — 70b/scout are 1K RPD, shared with
  summarize + agent, not worth burning on binary follow-up decisions

Follow-up prompt: removed Option A/B label framing (caused prompt leakage),
added explicit output format enforcement, added disengagement as MOVE_ON trigger,
lowered temperature 0.7 → 0.5

New: is_disengaged() — pre-LLM check, catches "I don't remember / move on /
next question" signals, saves an API call and skips follow-ups immediately

New: save_transcript() extracted as standalone function
New: Ctrl+C handling — saves partial transcript on interrupt




## Version 1 — 2026-03-23 — Initial version

Follow-up decision prompt sent to `llama-3.1-8b-instant` after each participant answer.
Model params: temperature=0.7, max_completion_tokens=150, stream=False.

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
