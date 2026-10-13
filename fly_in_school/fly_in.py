import sys

from parser import Parser, ParserError
from simulation_engine import SimulationEngine
from path_finder import PathFinder, PathFinderError
from visual import Visualizer
from menu import run_menu


def build_engine(file_name: str) -> SimulationEngine | None:
    """Parses the map, finds the paths and returns a fresh engine.

    Returns None (after printing the error) if the map is invalid
    or no path can be found.
    """

    try:
        graph = Parser(file_name=file_name).parse()
        best_path_set = PathFinder(graph).run()
    except (ParserError, PathFinderError) as error:
        print(f"Error: {error}")
        return None

    return SimulationEngine(graph, best_path_set)


def run_simulation(file_name: str) -> bool:
    """Runs the whole simulation and prints every turn in the terminal.

    Returns False if the map could not be loaded.
    """

    engine = build_engine(file_name)

    if engine is None:
        return False

    engine.run()
    return True


def run_visualization(file_name: str) -> None:
    """Opens the arcade window on a fresh simulation of the map.

    The engine changes the graph while it runs, so the window gets its
    own engine built from a freshly parsed map.
    """

    engine = build_engine(file_name)

    if engine is not None:
        Visualizer(engine.graph, engine).run()


def main() -> None:
    """Runs a map given as argument, or opens the menu without one."""

    if len(sys.argv) == 1:
        run_menu(run_simulation, run_visualization)

    elif len(sys.argv) == 2:
        file_name = sys.argv[1]

        run_simulation(file_name)

        run_visualization(file_name)

    else:
        print("Usage: python3 fly_in.py [map_file]")


if __name__ == "__main__":
    main()
