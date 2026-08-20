import sys


def main() -> None:
    if len(sys.argv) < 2:
        return
    try:
        with open(sys.argv[1], 'r') as file:
            content = file.readlines()
    except FileNotFoundError:
        print("File not found")
        return
    


if __name__ == "__main__":
    main()