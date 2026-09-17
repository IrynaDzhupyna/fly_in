import sys

from parser import Parser, ParserError
# from simulation_engine import SimulationEngine
from path_finder_adv import PathFinderAdv, PathFinderError


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
          f"for {graph.nb_drones} drones (start={graph.start.name}, end={graph.end.name})\n")

    #   activate simulation engine
    # engine = SimulationEngine(graph)
    # print()
    
    # for drone in engine.drones:
    #     print(f"\nDron ID: {drone.id}")
    #     print(f"Drone state: {drone.state}")
    #     print(f"Current zone: {drone.current_zone.name}")

    # print()
    # engine.run()
    path_find = PathFinderAdv(graph)
    try:
        paths = path_find.find_all_paths()
    except PathFinderError as error:
        print(f"Error: {error}")
        return

    # path_find.info_paths()
    path_find.find_best_paths()

    

if __name__ == "__main__":
    main()