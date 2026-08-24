import sys
from parser import Parser


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: main.py <map-file-name>")
        return 1

    file_name = sys.argv[1]
    parser = Parser()
    content = parser.read_the_file(file_name)


if __name__ == "__main__":
    main()
