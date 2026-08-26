import sys

from parser import Parser, ParserError


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: main.py <map-file-name>")
        return 1

    file_name = sys.argv[1]
    parser = Parser(file_name=file_name, nb_drones=0, zones=[], connections=[])

    try:
        parser.parser_engine()
    except ParserError as err:
        print(f"Error: {err}")
        return 1

    print(f"nb_drones: {parser.nb_drones}")
    print(f"zones: {[zone.name for zone in parser.zones]}")
    print(f"connections: {[(c.zone_a.name, c.zone_b.name) for c in parser.connections]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
