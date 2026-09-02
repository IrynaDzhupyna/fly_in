from sys import argv

from parser import Parser

def main() -> None:
    """ Main controller of fly_in program."""
    if len(argv) != 2:
        print("Usage: python main.py <input_file>")
        return

    input_file = argv[1]
    
    parser = Parser()
    content = parser.parse(input_file)
    for line in content:
        print(line)

if __name__ == "__main__":
    main()