---
name: session-close
description: |
  End-of-session summary and context preservation. Captures what was done, decisions made,
  and next steps so the next session starts with full context. Use when wrapping up work,
  switching context, or ending the day. Also trigger when user says '정리해줘', '세션 끝',
  'wrap up', 'session close', or '오늘 끝'.
user-invocable: true
---

## Quick Start

```
/session-close          → Summarize this session and save
/session-close quiet    → Save without showing output (fast exit)
```

**What happens:** I scan the current conversation, extract what was done, and save a structured log. Takes ~30 seconds.

---

## Workflow

### Step 1: Scan Session Context

Review the current conversation and extract:

1. **Work completed** — files created/edited, skills run, decisions made
2. **Decisions & direction changes** — anything that affects strategy or approach
3. **Open threads** — things started but not finished

### Step 2: Check for Existing Log Today

- Look for `outputs/session-logs/YYYY-MM-DD.md`
- If exists: **append** a new session block (multiple sessions per day is normal)
- If not: create new file

### Step 3: Generate Session Log

**File:** `outputs/session-logs/YYYY-MM-DD.md`

```markdown
# Session Log - YYYY-MM-DD

## Session [N] — [HH:MM]

### Done
- [Concrete outputs: files created, topics discussed, analyses run]

### Decisions
- [Any direction changes, strategic calls, or confirmed approaches]

### Next Up
- [ ] [Specific tasks to continue next session]
- [ ] [Blockers to resolve]
```

**Rules:**
- "Done" = factual, specific. Not "discussed ideas" but "explored X framework, concluded Y approach"
- "Next Up" = actionable checklist, not vague intentions
- Keep each session block under 20 lines. Concise over comprehensive.

### Step 4: Cleanup Check

- If `outputs/session-logs/` has files older than 7 days: flag them
  - "7일 넘은 세션 로그 [N]개 있어. 삭제할까?"
- Don't auto-delete. Always ask.

### Step 5: Confirm

**Default mode:**
Show the session summary to the user, then:
> "세션 로그 저장 완료. (`outputs/session-logs/YYYY-MM-DD.md`)"

**Quiet mode (`/session-close quiet`):**
Save silently, show only:
> "세션 로그 저장 완료 (`outputs/session-logs/YYYY-MM-DD.md`)"

---

## Output Quality Self-Check

- [ ] "Done" items reference specific outputs, not vague activities
- [ ] "Next Up" is a checkable list someone could pick up cold
- [ ] Session block is under 20 lines
