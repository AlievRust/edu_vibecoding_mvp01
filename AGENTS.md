# AGENTS.md — OpenSpec Workflow

> This file is an instruction for the agent. Follow it exactly and in order.

---

## 1. Prime directive: spec-first

**Core rule:** the source of truth is OpenSpec documents in this repository, not your assumptions.

Never guess if the answer should be in the spec. If the spec has no answer — **stop and ask**.

---

## 2. When the user describes an idea (tech proposal)

If the task is described in free form without a technical solution:

1. Propose 2–3 implementation options (tech stack).
2. For each option list:
   - dependencies (pyproject.toml or equivalent)
   - pros and cons
   - risks
3. Ask clarifying questions if anything is missing.

**Do not write code until the user has selected an option.**

---

## 3. File reading order at startup

Read documents in this order (if the file exists):

1. `README.md` — entry point, quick start, navigation.
2. `docs/technical_overview.md` — architecture and constraints.
3. `docs/changelog.md` — behavior change history.
4. `docs/roadmap.md` — forward direction (read if the task touches planning).
5. `openspec/project.md` — project-wide rules, constraints, and goals.
6. `openspec/changes/<change-id>/proposal.md`, `design.md`, `tasks.md` — source of truth for the active change.
7. `openspec/archive/README.md` — closed specs and historical context.

---

## 4. Conditions to start coding

Do not write code until **all** conditions are met:

- [ ] User has explicitly given the command to start implementation.
- [ ] `tasks.md` with a task checklist exists.
- [ ] `design.md` contains answers to all technical questions.
- [ ] All ambiguities are resolved — by asking the user or updating proposal/design.

---

## 5. When to stop and ask

**Stop and ask the user** if:

- `design.md` has no explicit answer to a technical question.
- The task requires choosing between two equally valid solutions.
- The change affects behavior not described in the spec.
- It is unclear whether something is in scope for the current change.

**Do not make architectural decisions on your own.** Guessing causes spec drift.

---

## 6. Task execution protocol

- Implement tasks top-to-bottom following `tasks.md`.
- Update task status in `tasks.md` as you work:
  - `[~]` — in progress
  - `[x]` — done
- Keep diffs small. One task — one logical commit.
- Add tests for any behavior change.
- After each task update documentation (see section 9).

---

## 7. Planning

For large features or refactors: create or update `PLANS.md` **before** starting implementation.

---

## 8. Subagents policy

Default to a single agent.

Use subagents only for bounded parallel tasks:
- repo exploration
- independent test runs
- log analysis
- summarization of separate modules

Avoid subagents for:
- small fixes
- overlapping edits
- refactors touching shared files

No more than 2 subagents at a time unless the user asks otherwise.
Return concise summaries, not raw logs.

---

## 9. Documentation update after a task

After implementing a task, check and update (if needed):

- `README.md` — always
- `docs/technical_overview.md` — if architecture or navigation changed
- `docs/roadmap.md` — if planning is affected
- `docs/changelog.md` — always when observable behavior changes
- `openspec/project.md` — if project-wide rules or entrypoints changed

---

## 10. Code requirements

- Code must be readable, structured, and PEP8-compliant.
- Docstrings and inline comments — in Russian.
- Every observable behavior change must be reflected in OpenSpec.

---

## 11. Testing after a task

- Run syntax check and linter on all created/modified files.
- Provide commands for manual verification of basic functionality.

---

## 12. Response format

- Structure: **plan → patch-style changes → commands to run**.
- Answers, comments, and documentation — in Russian.

---

## 13. Project working agreements

- For every meaningful behavior change, create or update an OpenSpec change in `openspec/changes/<number-change-id>/`.
- Reflect even small operational fixes in OpenSpec if they change observable behavior, logging, configuration, or data format.
- If full end-to-end verification is impossible due to external systems — state that explicitly as an environment limitation.
- Do not delete historical artifacts (logs, notebooks, etc.) unless the user explicitly requests cleanup.
