.PHONY: build clean test

build: .venv
	$(CURDIR)/.venv/bin/pip install -r requirements.txt

.venv:
	pyvenv $(CURDIR)/.venv

clean:
	rm -rf $(CURDIR)/.venv

test: build
	$(CURDIR)/.venv/bin/python -m unittest discover
