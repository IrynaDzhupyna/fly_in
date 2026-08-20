SRC = .
NAME = test.py
MAP = /home/irdzhupy/Projects/Core/Rank_3/maps/easy/01_linear_path.txt

run: install
	poetry run python3 $(NAME)

install:
	poetry install

debug:
	poetry run python -m pdb $(NAME) $(CONFIG)

clean:
	rm -rf */__pycache__ .mypy_cache .pytest_cache

lint:
	flake8 $(SRC)
	mypy $(SRC) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 $(SRC)
	mypy $(SRC) --strict

.PHONY: run install debug clean lint lint-strict
