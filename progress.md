# Progress

Session continuity log for cutz2. Append-only — do not rewrite history, add new entries at the bottom.

## Session Restart Markers

- **Last Updated**: harness scaffolded (project-specific AGENTS.md, single-feature feature_list.json, Postgres-aware init.sh, reset progress/handoff).
- **Current Objective**: get `./init.sh` passing end-to-end on this machine, then begin feat-001 (pytest + /chat smoke test).
- **Recommended Next Step**: run `./init.sh` from `/Users/arnoldsanders/workspace/cutz2_api` and report which check fails first. Likely candidates: Postgres connectivity, missing pytest-django in requirements, no tests written yet.

---

Format each entry as:

```
## YYYY-MM-DD — short title
- Status: <one of: started | in-progress | done | blocked>
- Feature: <feature_list.json id, or "none">
- What changed: <bullet list of files/concrete edits>
- Verification: <./init.sh result, test names that ran, output excerpt>
- Next step: <single concrete next action for the next session>
- Blockers: <or "none">
```

---

## Harness scaffolded

- Status: started
- Feature: feat-001 (Setup pytest and smoke test for /chat)
- What changed:
  - Wrote project-specific `AGENTS.md` (Django 5 + DRF + Channels + Postgres facts, working rules, escalation)
  - Replaced `feature_list.json` with a single active feature (pytest + /chat smoke test)
  - Replaced `init.sh` with Postgres-aware verification (pg_isready -> manage.py check -> migrate --check -> tests)
  - Reset `progress.md` and `session-handoff.md` for first real session
- Verification: harness validation script scores 100/100 on generic structure (all five subsystems at 5/5). `./init.sh` itself has not been executed end-to-end yet — Postgres may or may not be up; no pytest config exists yet so step 4 will fail until feat-001 lands.
- Next step: confirm `./init.sh` runs end-to-end on this machine; if Postgres isn't reachable, document how to start it; then begin feat-001 (install pytest + pytest-django, write `pytest.ini` or `pyproject.toml` test config, write `conftest.py`, add a `tests.py` or `tests/` in the `chat` app with a smoke test against the `/chat` endpoint).
- Blockers: none identified.

## langchain_qwq import commented out

- Status: in-progress (deferred)
- Feature: none (environment blocker, separate from feat-001)
- What changed:
  - `cuts/chat/models.py`: commented out `from langchain_qwq import ChatQwen` and the two `ChatQwen` usage lines. Left explanatory comments pointing to this progress note.
  - Reason: `langchain-qwq==0.3.4` (installed) imports `Self` from `typing`, which requires Python 3.11+. The venv at `cutz2/bin/python` is 3.10. This crashes `manage.py check` at app-loading time. Downgrading `langchain-qwq` to a 3.10-compatible version (0.2.x) would force a `langchain-core` major-version downgrade, likely breaking other features.
  - Scope note: `ChatQwen` is only used in `CalendarAgent.__init__` in `cuts/chat/models.py`. That class also has other stub-quality smells (unused `calendar` arg, shadowed `messages` import, `hello_world` stub tool, top-level `IPython.display` import). Commenting it out is safe for now because nothing currently routes through `CalendarAgent`.
- Verification: ./init.sh — see next entry.
- Next step: confirm `./init.sh` now passes step 2 (`manage.py check`). Then proceed with feat-001. Defer the real fix (recreate venv on Python 3.11+, or remove `ChatQwen` entirely if it's truly dead) to a future session.
- Blockers: none now.

## integrations/views.py: fixed brittle .env path resolution

- Status: done (environment blocker resolved)
- Feature: none (out of scope, but blocks feat-001 from running green)
- What changed:
  - `cuts/integrations/views.py`: replaced `dotenv_values("../.env")` with `dotenv_values(str(_REPO_ROOT / ".env"))` where `_REPO_ROOT = Path(__file__).resolve().parent.parent.parent`. Removed brittle CWD-relative path; resolves to repo root regardless of where the process is launched from.
  - Added `from pathlib import Path` import.
- Verification: `./init.sh` — all four checks pass. See feat-001 entry below.
- Next step: begin feat-001 (pytest + /chat smoke test).
- Blockers: none. `./init.sh` is green.

## ./init.sh passes end-to-end

- Status: done
- Feature: feat-001 prerequisite
- Verification output:
  - [1/4] Infrastructure check: Postgres at localhost:5432 ... OK
  - [2/4] Static check: 'manage.py check' ... OK
  - [3/4] Build check: 'manage.py migrate --check' ... OK
  - [4/4] Test check: running tests ... Found 0 test(s). OK
- Note: step 4 passes only because Django's test runner returns 0 when no tests exist. Once feat-001 adds the /chat smoke test, this step will actually run something.

## Out-of-band: created Barber account

- Status: done
- Feature: none (user request, not in feat-001 scope)
- What changed:
  - Created `Barber` user `b@b.com` / `necros12` via `manage.py shell`.
  - Required fields supplied: `username="b@b.com"`, `first_name="Barber One"`, `title="Stylist"`, `description="Default barber account."`, `street_address="123 Main St"`, `city="Anytown"`, `state="CA"`, `zip_code="94000"`. `image_url` left blank (nullable).
  - Gotcha encountered: existing users in the DB include a row with `username=''` (id=1, `test@gmail.com`), which collides with the `adminprofile_customuser_username_key` unique constraint because `AbstractUser.username` is still required. Worked around by passing `username="b@b.com"` explicitly in `get_or_create` defaults.
  - Gotcha 2: `/admin/` login returns the form again (200, no redirect) because Django admin requires `is_staff=True` and the new user has `is_staff=False`. The credentials ARE valid — `authenticate()` in shell returns the user. Admin access was not requested.
  - Verification: `user.check_password('necros12')` returned True; `authenticate(username='b@b.com', password='necros12')` returned the user.
- Blockers: none for the account itself. If admin access is needed later, set `user.is_staff=True` and save.
