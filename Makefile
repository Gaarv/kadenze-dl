.PHONY: all

install:
	pip install -r requirements.txt
	pip install -U .

install-dev:
	pip install -r requirements-dev.txt
	pip install -U .

test:
	python -m pytest --cov -v -s

standalone:
	pyinstaller --onefile kadenze-dl.py