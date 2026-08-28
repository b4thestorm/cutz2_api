# Session Handoff

Fill this in at the end of any session that didn't complete its feature. Delete it (or leave the empty template) when the session ends cleanly.

## Session Restart Markers

- **Last Updated**: never (template only — no session has completed yet)
- **Current Objective**: get `./init.sh` green end-to-end, then complete feat-001 (pytest + /chat smoke test)
- **Recommended Next Step**: run `./init.sh` and observe output

---

## Current state

- **Active feature**: feat-001 — Setup pytest and smoke test for /chat
- **Feature status**: not-started
- **Working directory**: `/Users/arnoldsanders/workspace/cutz2_api`

## What was done this session

- (none yet — first session)

## What's left to do

- Confirm `./init.sh` runs end-to-end in this environment (Postgres reachable? `manage.py check` clean? `migrate --check` clean?).
- Install `pytest` and `pytest-django` (already in `requirements.txt` as `pytest`; add `pytest-django` if not present).
- Add pytest config — either `pytest.ini` at repo root or a `[tool.pytest.ini_options]` block in `pyproject.toml` — with `DJANGO_SETTINGS_MODULE = cuts.cuts.settings`.
- Add `conftest.py` at repo root if needed for pytest-django bootstrap.
- Add a `tests.py` (or `tests/` package) inside the `chat` app with a smoke test that hits `/chat` and asserts a 2xx response.
- Re-run `./init.sh` and capture the passing test names in `feature_list.json` `evidence` field.
- Update `progress.md` and mark feat-001 `done`.

## Blockers

- None identified yet. First action is to run `./init.sh` and see what fails.

## Files touched (planned)

- `requirements.txt` — possibly add `pytest-django` (check first; don't duplicate)
- `pytest.ini` OR `pyproject.toml` — pytest config
- `conftest.py` — pytest-django bootstrap (if not auto-handled by pytest.ini)
- `chat/tests.py` — smoke test

## Next session: first action

Run `./init.sh` from `/Users/arnoldsanders/workspace/cutz2_api` and report which of the four checks fails first.
