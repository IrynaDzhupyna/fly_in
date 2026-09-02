SRC = .
NAME = main.py
MAP = maps/easy/01_linear_path.txt

run: install
	poetry run python3 $(NAME) $(MAP)

install:
	poetry install

debug:
	poetry run python3 -m pdb $(NAME) $(MAP)

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache

lint:
	flake8 $(SRC)
	mypy $(SRC) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 $(SRC)
	mypy $(SRC) --strict

.PHONY: run install debug clean lint lint-strict
