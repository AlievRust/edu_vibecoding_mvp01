# AGENTS.md — OpenSpec workflow

## Tech proposal first
When the user provides a project idea or feature request in plain language:
1) Propose 2–3 implementation options (tech stack).
2) For each option, list:
   - dependencies (pyproject.toml)
   - pros/cons
   - risks
3) Ask any missing questions.
Do not write code until one option is selected.

## Prime directive
Work spec-first. The source of truth is OpenSpec documents in this repository.

## Agent entrypoint
When starting work in this repository, read documents in this order (if exists):
1. `README.md` - entry point, quick start, and navigation.
2. `docs/technical_overview.md` - architecture, and constraints.
3. `docs/changelog.md` - behavior history and recent project changes.
4. `docs/roadmap.md` - forward-looking direction, if the task touches planning.
5. `openspec/project.md` - project-wide OpenSpec rules.
6. `openspec/changes/<change-id>/proposal.md`, `design.md`, `tasks.md` - active change source of truth.
7. `openspec/archive/README.md` - closed specs and historical context.

## Always read first
You can write code only after the user's direct command.
Before coding, read:
- `openspec/project.md`
- the active change docs in `openspec/changes/<number-change-id>/`:
  - `proposal.md`
  - `design.md`
  - `tasks.md`

## Do not code until
- User give you a command
- Requirements and tasks checklist exist.
- If unclear: ask questions or update proposal/design first.

## Execution protocol
- Implement tasks top-to-bottom.
- Mark tasks in tasks.md:
  - [~] in progress
  - [x] done
- Keep diffs small. Add tests for behavior changes.
- After implementing a task do not forget to update `README.md`, and when the change affects navigation or architecture also update `docs/technical_overview.md` and `docs/roadmap.md`.

## Subagents policy
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
- tasks where coordination cost exceeds benefit

Unless I explicitly ask otherwise, use no more than 2 subagents.
Return concise summaries, not raw logs.

## Planning
For large features or refactors, create or update PLANS.md before implementation.

## Critical rules:
- The code MUST be well structured, human readable, and comply with PEP8 requirements.
- Use detailed comments in the code (docstrings)

## Testing routine after current task is done:
- Use syntax and linter checking for all created/modified files
- Offer/create testing commands or utils after current task is done for testing basic functioning

## Output format
- Plan -> patch-style changes -> commands to run.
- Answer in Russian.

## Project-specific working agreements
- For every meaningful behavior change, create or update a dedicated OpenSpec change in `openspec/changes/<number-change-id>/`.
- Even small operational fixes should be reflected in OpenSpec if they change observable behavior, logging, configuration, or runtime format.
- After implementation, update all relevant project docs, not only `README.md`. By default check:
  - `README.md`
  - `docs/technical_overview.md`
  - `docs/roadmap.md`
  - `docs/changelog.md`
  - `openspec/project.md` when project-wide behavior or preferred entrypoints changed
- Logs must be UTF-8 so Cyrillic text is displayed correctly.
- When diagnosing runtime issues, verify the actual interpreter and environment used by the user, not only the source code.
- If full end-to-end verification was not performed because external systems are involved, state that explicitly as an environment limitation.
- Treat operational log readability as part of the user-facing interface, not as an internal-only concern.
- Do not remove historical artifacts such as notebooks or legacy logs unless the user explicitly requests cleanup.
- When fixing Cyrillic or encoding regressions, verify the real file contents, not only terminal rendering.
