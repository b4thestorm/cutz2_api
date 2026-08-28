# AGENTS.md

Project harness for **cutz2**, a Django 5 + DRF + Channels application backed by Postgres.

## Project Facts

- **Stack**: Django 5.0, Django REST Framework, Channels 4 (ASGI via daphne), django-eventstream (SSE), psycopg 3, langgraph, langchain.
- **Apps**: `adminprofile`, `chat`, `cuts` (project root), `integrations`.
- **Database**: PostgreSQL on `localhost:5432`, database `cutz2`, user `arnoldsanders`. Credentials live in `cuts/cuts/settings.py` (`DATABASES` block, lines ~103-111). No `.env` DB config — do not refactor this without explicit instruction.
- **Python env**: virtualenv at `cutz2/` (project name). Activate with `source cutz2/bin/activate` or invoke `cutz2/bin/python` directly.
- **WebSockets/SSE**: Channels (`daphne`) for WebSockets; django-eventstream for server-sent events.

## Startup Workflow

Before writing code:

1. **Confirm working directory** with `pwd` — must be the repo root (`/Users/arnoldsanders/workspace/cutz2_api`).
2. **Read this file** completely.
3. **Run `./init.sh`** to verify environment (Postgres reachable, Django checks pass, migrations in sync, tests run).
4. **Read `feature_list.json`** to see the current active feature.
5. **Review recent commits** with `git log --oneline -5`.

If `./init.sh` fails, fix that before touching new scope.

## Working Rules

- **One feature at a time**: `feature_list.json` should have exactly one feature in `not-started` or `in_progress`. Do not start a second.
- **Verification required**: Don't claim done without `./init.sh` exiting 0. Capture the output and reference it in `progress.md`.
- **Stay in scope**: Don't refactor unrelated files, don't reformat unrelated code, don't "improve" settings without being asked.
- **Django conventions**: migrations are mandatory for model changes (`python cuts/manage.py makemigrations`); never edit migration files by hand except to fix a known bad migration.
- **Leave clean state**: Next session must be able to run `./init.sh` immediately and pick up exactly where you stopped.

## Definition of Done

A feature is done only when ALL of the following are true:

- [ ] Target behavior is implemented
- [ ] `./init.sh` exits 0 (Postgres up, `manage.py check` clean, `migrate --check` clean, tests pass)
- [ ] Evidence (test names, command output excerpt) recorded in `feature_list.json` `evidence` field
- [ ] `progress.md` updated with what changed and what's next
- [ ] Working tree contains no unrelated edits (`git status` clean apart from intended changes)

## Required Artifacts

- `feature_list.json` — Feature state tracker (source of truth). **Currently contains exactly one feature.**
- `progress.md` — Session continuity log, append-only.
- `init.sh` — Standard startup and verification path. Must exit non-zero on any failure.
- `session-handoff.md` — Filled in at end of session if work is unfinished.

## Verification Commands

```bash
./init.sh
```

Internally runs:

1. `pg_isready -h localhost -p 5432` — Postgres reachable?
2. `python cuts/manage.py check` — Django configuration valid?
3. `python cuts/manage.py migrate --check` — migrations in sync?
4. `pytest` (or `python cuts/manage.py test` if no `pytest.ini`) — tests pass?

## End of Session

Before ending a session:

1. Update `progress.md` with: what was done, what remains, any blockers.
2. Update `feature_list.json`: change feature `status` (`not-started` → `in_progress` → `done`), fill `evidence` field with concrete output.
3. If work is unfinished, fill `session-handoff.md` with current state, blockers, and exact next step.
4. Commit with a descriptive message once `./init.sh` passes.
5. Leave working tree clean enough for next session to run `./init.sh` immediately.

## Escalation

If you encounter:

- **DB connection errors**: confirm Postgres is running (`pg_isready`, `brew services list` if homebrew, or check Docker if applicable). Do not edit `settings.py` DB credentials without explicit instruction.
- **Migration drift**: run `python cuts/manage.py makemigrations --dry-run --check` to see what's missing, then ask before generating migrations.
- **Channels/ASGI issues**: this app runs under daphne, not the dev runserver. WebSocket routes live in `cuts/cuts/asgi.py` and per-app `routing.py`.
- **Scope ambiguity**: re-read `feature_list.json`. If unclear, ask — don't expand scope.
