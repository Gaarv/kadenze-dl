.PHONY: all

install:
	pip install pip-tools
	pip-compile requirements.in
	pip install -r requirements.txt
	pip install -U .

install-dev:
	pip install pip-tools
	pip-compile requirements-dev.in
	pip install -r requirements-dev.txt
	pip install -U .

test:
	python -m pytest --cov -v -s