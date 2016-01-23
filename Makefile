.PHONY: clean help js test

PYTHON = python
RPYTHON = rpython

OPTS = "--output=bin/js"
TARGET = "js/target.py"

all: clean test build

help:
	@echo "clean    Remove build artifacts"
	@echo "build    Build the interpreter"
	@echo "test     Run unit and integration tests"

clean:
	@rm -rf bin/js

build:
	$(RPYTHON) $(OPTS) $(TARGET)

test:
	$(PYTHON) setup.py test
