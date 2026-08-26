PYTHON := python3
MAP    ?= 01_linear_path.txt

.PHONY: install run test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py $(MAP)

test:
	$(PYTHON) test.py

clean:
	rm -rf __pycache__
