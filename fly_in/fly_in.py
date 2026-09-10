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

    print(f"\nParsed {len(graph.zones)} zones and {len(graph.connections)} connections "
          f"for {graph.nb_drones} drones (start={graph.start.name}, end={graph.end.name})")

    # we got the graph and need to activate simulation engine
    engine = SimulationEngine(graph)
    print()
    
    for drone in engine.drones:
        print(f"\nDron ID: {drone.id}")
        print(f"Drone state: {drone.state}")
        print(f"Current zone: {drone.current_zone.name}")

    print()
    engine.run()


if __name__ == "__main__":
    main()