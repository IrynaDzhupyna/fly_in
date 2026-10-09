SRC = .
NAME = fly_in.py
CUSTOM_MAP = custom_maps/test_branching_conflicts.txt
TESTS = tests/.

run: install
	poetry run python3 $(NAME) $(CUSTOM_MAP) 

easy:
	poetry run python3 $(NAME) ./maps/easy/02_simple_fork.txt

medium:
	poetry run python3 $(NAME) ./maps/medium/02_circular_loop.txt

hard:
	poetry run python3 $(NAME) ./maps/hard/01_maze_nightmare.txt

chal:
	poetry run python3 $(NAME) ./maps/challenger/01_the_impossible_dream.txt

install:
	pipx install poetry
	poetry install

debug:
	poetry run python3 -m pdb $(NAME) $(MAP)

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache

lint:
	poetry run python -m flake8 $(SRC)
	poetry run python -m mypy $(SRC) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 $(SRC)
	mypy $(SRC) --strict

test:
	poetry run python -m pytest

.PHONY: run install debug clean lint lint-strict test
