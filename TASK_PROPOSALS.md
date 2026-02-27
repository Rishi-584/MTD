# Codebase Task Proposals

## 1) Typo Fix Task
**Task:** Fix virtual environment path typo/inconsistency in `LINUX_SETUP.md`.

- The guide creates `.venv` (`python3 -m venv .venv`) but later instructs users to run commands from `venv/bin/...`.
- This is likely a typo/inconsistency that can break copy-paste setup for first-time users.

**Evidence:** `LINUX_SETUP.md` uses `.venv` at lines 32-34, then `venv` at lines 46-50 and 67.  
**Proposed fix:** Standardize all commands to `.venv` (or `venv`) consistently across the document.  
**Acceptance criteria:** A user can follow setup commands line-by-line without path edits and successfully activate/run from the same virtualenv name.

## 2) Bug Fix Task
**Task:** Fix fragile DNS query parsing in `/dns` endpoint of `mtd_controller.py`.

- Current implementation parses query with `p.split('=')[-1]`, which can produce incorrect hostnames if additional query params are added, if ordering changes, or if URL encoding is involved.
- Other handlers already use robust parsing (`parse_qs(urlparse(path).query)`), so `/dns` should do the same.

**Evidence:** `mtd_controller.py` lines 148-151.  
**Proposed fix:** Parse `q` using `urllib.parse.urlparse` + `parse_qs`, validate required parameter, and return a clear 400 on malformed input.  
**Acceptance criteria:** `/dns?q=h2` still works, `/dns?x=1&q=h2` works correctly, and malformed requests produce deterministic errors.

## 3) Code Comment/Documentation Discrepancy Task
**Task:** Reconcile controller module docstring architecture/intervals with actual constants and table layout.

- Docstring says "two-table pipeline" and describes Table 1 as L2/IP forwarding, but constants define three tables (`TABLE_SNAT=0`, `TABLE_DNAT=1`, `TABLE_L2=2`).
- Docstring also states shuffle intervals `90/120/180`, while code uses `80/100/120`.

**Evidence:** `mtd_controller.py` docstring lines 7-9 and 21-24 vs constants at line 70 and table IDs below the imports.  
**Proposed fix:** Update docstring to match real table model and configured intervals, or update constants if doc behavior is intended.  
**Acceptance criteria:** Architecture and interval values in comments/docs exactly match runtime behavior.

## 4) Test Improvement Task
**Task:** Convert `scripts/verify_secure_transfer.py` from print-only script to assertive test that fails CI on regressions.

- The script prints "Assertions" but does not assert or return non-zero on failure paths.
- Exceptions are swallowed and only logged, causing false-green runs in automation.

**Evidence:** `scripts/verify_secure_transfer.py` lines 22-34.  
**Proposed fix:** Implement `pytest`-style assertions (or explicit `sys.exit(1)` on failure), and validate key fields (`status`, trace steps, verification metadata) for both success and expected-failure scenarios.  
**Acceptance criteria:** The test exits non-zero when API behavior regresses and can be integrated into automated checks.
