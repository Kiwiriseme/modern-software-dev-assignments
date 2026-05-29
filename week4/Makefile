.PHONY: run test format lint seed

run:
	@python -c "import os; os.environ['PYTHONPATH'] = '.'; import subprocess; import sys; host = os.environ.get('HOST', '127.0.0.1'); port = os.environ.get('PORT', '8000'); sys.exit(subprocess.run(['uvicorn', 'backend.app.main:app', '--reload', '--host', host, '--port', port]).returncode)"

test:
	@python -c "import os; os.environ['PYTHONPATH'] = '.'; import subprocess; import sys; sys.exit(subprocess.run(['pytest', '-q', 'backend/tests']).returncode)"

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	@python -c "import os; os.environ['PYTHONPATH'] = '.'; from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
