MAKEFLAGS = --no-print-directory --always-make --silent
MAKE = make $(MAKEFLAGS)

VENV_NAME = ultimate-card-verification
VENV_PATH = ~/.virtualenvs/$(VENV_NAME)
VENV_ACTIVATE = . $(VENV_PATH)/bin/activate

.PHONY: clean check virtualenv pycodestyle pylint test

clean:
	find . -name "*.pyc" -print -delete
	find . -name "__pycache__" -type d -print -exec rm -rf {} +
	find . \( -name "*.min.js" -o -name "*.min.css" \) -print -delete
	rm -rfv $(VENV_PATH)

check:
	$(MAKE) virtualenv
	$(MAKE) pylint pycodestyle test

virtualenv:
	test -d $(VENV_PATH) || python3 -m venv $(VENV_PATH)
	$(VENV_ACTIVATE) && pip install --upgrade pip
	$(VENV_ACTIVATE) && pip install -e .

pycodestyle:
	@echo "Running pycodestyle..."
	$(VENV_ACTIVATE) && pycodestyle src

pylint:
	@echo "Running pylint..."
	$(VENV_ACTIVATE) && pylint src

test:
	@echo "Running pytest..."
	$(VENV_ACTIVATE) && APP_ENV=test pytest test --tb=short
