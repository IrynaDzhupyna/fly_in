import sys

from parser import Parser, ParserError
from simulation_engine import SimulationEngine
from path_finder import PathFinder, PathFinderError


def main() -> None:

    if len(sys.argv) < 2:
        print("Usage: main.py <map_file>")
        return

    file_name = sys.argv[1]
    # Parser
    parser = Parser(file_name=file_name)
    try:
        # graph
        graph = parser.parse()
    except ParserError as error:
        print(f"Error: {error}")
        return
    # path finder
    path_finder = PathFinder(graph)
    try:
        best_path_set = path_finder.run()
    except PathFinderError as error:
        print(f"Error: {error}")
        return

    # engine = SimulationEngine(graph, best_path_set)
    # engine.run()
    visual = GameView()

    

if __name__ == "__main__":
    main()
