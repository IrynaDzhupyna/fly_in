import sys

from parser import Parser, ParserError
from simulation_engine import SimulationEngine


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: main.py <map_file>")
        return

    file_name = sys.argv[1]

    parser = Parser(file_name=file_name)
    try:
        graph = parser.parse()
    except ParserError as error:
        print(f"Error: {error}")
        return

    print(f"Parsed {len(graph.zones)} zones and {len(graph.connections)} connections "
          f"for {graph.nb_drones} drones (start={graph.start.name}, end={graph.end.name})")

    # we got the graph and need to activate simulation engine
    engine = SimulationEngine(graph)
    engine.info()

    # engine.run()


if __name__ == "__main__":
    main()