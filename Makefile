PYTHON = python3

.PHONY: data

test:
	pytest

data: 
	${PYTHON} data_factory.py
