import sys

from parser import Parser, ParserError


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: main.py <map_file>")
        return

    parser = Parser(sys.argv[1])
    try:
        graph = parser.parse()
    except ParserError as error:
        print(f"Error: {error}")
        return

    print(f"Parsed {len(graph.zones)} zones and {len(graph.connections)} connections "
          f"for {parser.nb_drones} drones (start={graph.start.name}, end={graph.end.name})")


if __name__ == "__main__":
    main()
