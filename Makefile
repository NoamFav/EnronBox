PYTHON := $(shell command -v python3 || command -v python)

install:
	pip install -r requirements.txt
	$(PYTHON) scripts/postinstall.py
