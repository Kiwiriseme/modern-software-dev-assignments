Run the test suite (from week4/ directory).

## Steps
1. Run `make test` (from `week4/` directory) and capture full output.
2. If all tests pass, run `python -m coverage run -m pytest -q backend/tests` and `python -m coverage report -m` for coverage summary.
3. Report:
   - Pass/fail counts per test file
   - Any failure details with traceback snippets
   - Coverage percentage and uncovered lines (if coverage was run)
   - Suggested next steps for fixing failures

## Headless mode
When running headless, skip interactive prompts and report results directly.