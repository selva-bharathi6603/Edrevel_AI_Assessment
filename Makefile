.PHONY: docs test agent-setup agent-resetdb agent-smoke agent-test \
        deps-dev lint security test-unit test-ui reports-clean ci

VENV_PYTHON=env/bin/python
VENV_PIP=env/bin/pip
AGENT_TEST_FILES=$(shell git ls-files 'tests/*.py')

help:
	@echo "  env          create a development environment using virtualenv"
	@echo "  deps         install runtime dependencies using pip"
	@echo "  deps-dev     install runtime + dev/CI tooling (ruff, bandit, playwright)"
	@echo "  clean        remove unwanted files like .pyc's"
	@echo "  lint         run Ruff static analysis (writes reports/lint/)"
	@echo "  security     run Bandit security scan (writes reports/security/)"
	@echo "  test-unit    run pytest backend tests with coverage + JUnit XML"
	@echo "  test-ui      run Playwright UI tests (needs 'playwright install')"
	@echo "  test         run test-unit + test-ui"
	@echo "  reports-clean  remove generated report artifacts"
	@echo "  ci           run the full pipeline: lint + security + test"
	@echo "  agent-setup  install dependencies in ./env for AI/code agents"
	@echo "  agent-resetdb reset and seed local development database"
	@echo "  agent-smoke  run fast smoke tests"
	@echo "  agent-test   run full test suite with coverage"

env:
	python3 -m venv env && \
	. env/bin/activate && \
	make deps

deps:
	pip install -r requirements.txt

deps-dev: deps
	pip install ruff bandit pytest-playwright
	playwright install chromium

clean:
	find . | grep -E "(__pycache__|\.pyc|\.DS_Store|\.db|\.pyo$\)" | xargs rm -rf

reports-clean:
	rm -rf reports

# Legacy target kept for anyone still relying on flake8/setup.cfg.
flake8-lint:
	flake8 --exclude=env .

lint:
	mkdir -p reports/lint
	ruff check . --output-format=full | tee reports/lint/ruff-report.txt
	ruff check . --output-format=json > reports/lint/ruff-report.json

security:
	mkdir -p reports/security
	bandit -c .bandit.yml -r appname -f txt -o reports/security/bandit-report.txt
	bandit -c .bandit.yml -r appname -f json -o reports/security/bandit-report.json
	@cat reports/security/bandit-report.txt

test-unit:
	APPNAME_ENV=test python -m pytest --ignore=tests/test_ui_login.py \
		--junitxml=reports/junit/pytest-results.xml

test-ui:
	APPNAME_ENV=test python -m pytest tests/test_ui_login.py \
		--junitxml=reports/junit/playwright-results.xml \
		--cov=appname --cov-append \
		--cov-report=term-missing \
		--cov-report=xml:reports/coverage/coverage.xml \
		--cov-report=html:reports/coverage/html

test: test-unit test-ui

# Simulates the CI pipeline locally: run this after committing to confirm
# the build is green before pushing, or point a GitHub Actions job at it.
ci: lint security test-unit
	@echo ""
	@echo "CI pipeline finished. Reports are under ./reports"

agent-setup:
	python3 -m venv env
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

agent-resetdb:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Run 'make agent-setup' first."; exit 1; fi
	APPNAME_ENV=dev $(VENV_PYTHON) manage.py resetdb

agent-smoke:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Run 'make agent-setup' first."; exit 1; fi
	APPNAME_ENV=test $(VENV_PYTHON) -m pytest -q tests/test_urls.py tests/test_login.py

agent-test:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Run 'make agent-setup' first."; exit 1; fi
	APPNAME_ENV=test $(VENV_PYTHON) -m pytest --cov-report=term-missing --cov=appname $(AGENT_TEST_FILES)
