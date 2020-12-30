PYTHON = python3

test:
	pytest

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -depth -type d -name ".pytest_cache" -exec rm -r "{}" +
	find . -depth -type d -name ".ipynb_checkpoints" -exec rm -r "{}" +
