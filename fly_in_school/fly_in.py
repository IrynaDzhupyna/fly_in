import sys

from parser import Parser, ParserError
from simulation_engine import SimulationEngine
from path_finder import PathFinder, PathFinderError
from visual import Visualizer
from menu import run_menu


def run_simulation(file_name: str):
    """Activates the stimulation engine"""
    
    parser = Parser(file_name=file_name)
    try:
        graph = parser.parse()
    except ParserError as error:
        print(f"Error: {error}")
        return

    path_finder = PathFinder(graph)
    try:
        best_path_set = path_finder.run()
    except PathFinderError as error:
        print(f"Error: {error}")
        return

    engine = SimulationEngine(graph, best_path_set)
    engine.run()


def main() -> None:

    if len(sys.argv) == 1:
        run_menu(run_simulation)

    elif len(sys.argv) == 2:
        file_name = sys.argv[1]
        run_simulation(file_name)

    else:
        print("Usage: main.py <map_file>")
        return

    # visual = Visualizer(graph, engine)
    # visual.run()


if __name__ == "__main__":
    main()
