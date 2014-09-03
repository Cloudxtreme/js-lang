.PHONY: clean

all: jsc

clean:
	@find . -type f -name '*.pyc' -delete
	@rm -rf build dist *egg-info jsc

jsc:
	@rpython --output=jsc js/target.py
