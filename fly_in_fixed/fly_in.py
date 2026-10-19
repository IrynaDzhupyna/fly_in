import sys

from menu import run_menu
from simulation_engine import SimulationEngine, EngineError
from parser import Parser, ParserError
from path_finder import PathFinder, PathFinderError
from scheduler import Scheduler, SchedulerError
from visual import Visualizer


def build_engine(file_name: str) -> SimulationEngine | None:
    """
    Parses the map, finds the cheapest paths, plans every drone's timetable.

    Pipeline: Parser -> Graph -> PathFinder (candidate paths)
                -> Scheduler (timetables) -> SimulationEngine (replay).

    Returns:
        - None if the map is invalid or no path can be found
        - Engine ready to play"""

    try:
        graph = Parser(file_name=file_name).parse()
        paths = PathFinder(graph).run()
        schedules = Scheduler(graph, paths).run()
    except (ParserError, PathFinderError, SchedulerError) as error:
        print(f"Error: {error}")
        return None

    return SimulationEngine(graph, schedules)


def run_simulation(file_name: str) -> bool:
    """Runs the whole simulation and prints every turn in the terminal.

    Returns:
        - False if the map could not be loaded
        - True if success"""

    engine = build_engine(file_name)

    if not engine:
        return False

    try:
        engine.run()
    except EngineError as error:
        print(f"Error: {error}")
        return False

    return True


def run_visualization(file_name: str) -> None:
    """Opens the arcade window on a simulation of the map.

    The engine changes the graph while it runs, so the window gets its
    own engine built from freshly parsed map."""

    engine = build_engine(file_name)

    if engine is not None:
        Visualizer(engine.graph, engine).run()


USAGE = "Usage: python3 fly_in.py [map_file]"


def main() -> int:
    """Runs a map given as argument, or opens the menu without one.

    Returns:
        - 0 on success
        - 1 if the map is invalid, unsolvable or an error occurred
        - 2 on wrong command line usage"""

    try:
        if len(sys.argv) == 1:
            run_menu(run_simulation, run_visualization)
            return 0

        if len(sys.argv) == 2:
            file_name = sys.argv[1]

            if not run_simulation(file_name):
                return 1

            try:
                run_visualization(file_name)
            except Exception as error:
                print(f"Could not open the visualization: {error}")
            return 0

        print(USAGE)
        return 2

    except KeyboardInterrupt:
        print("\nProgram was terminated. Good bye!")
        return 0

    except Exception as error:
        print(f"Unexpected error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
