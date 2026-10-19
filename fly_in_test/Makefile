NAME = fly_in.py
SRC = .
MAP = maps/easy/01_linear_path.txt

install:
	@command -v poetry >/dev/null 2>&1 || pipx install poetry
	poetry install

run: install
	poetry run python3 $(NAME)

map:
	poetry run python3 $(NAME) $(MAP)

easy:
	poetry run python3 $(NAME) maps/easy/02_simple_fork.txt

medium:
	poetry run python3 $(NAME) maps/medium/02_circular_loop.txt

hard:
	poetry run python3 $(NAME) maps/hard/01_maze_nightmare.txt

chal:
	poetry run python3 $(NAME) maps/challenger/01_the_impossible_dream.txt

debug:
	poetry run python3 -m pdb $(NAME) $(MAP)

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache

re: clean install

lint:
	poetry run python -m flake8 $(SRC)
	poetry run python -m mypy $(SRC) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	poetry run python -m flake8 $(SRC)
	poetry run python -m mypy $(SRC) --strict

test:
	poetry run python -m pytest

.PHONY: install run map easy medium hard chal debug clean re lint lint-strict test
