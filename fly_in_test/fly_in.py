import sys

from parser import Parser, ParserError
from simulation_engine import SimulationEngine, EngineError
from path_finder import PathFinder, PathFinderError
from scheduler import Scheduler, SchedulerError
from visual import Visualizer
from menu import run_menu


def build_engine(file_name: str) -> SimulationEngine | None:
    """Parses the map, plans every drone's timetable and returns a fresh
    engine ready to play it.

    Pipeline: Parser -> Graph -> PathFinder (candidate paths)
              -> Scheduler (timetables) -> SimulationEngine (replay).

    Returns None (after printing the error) if the map is invalid
    or no path can be found.
    """

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

    Returns False if the map could not be loaded.
    """

    engine = build_engine(file_name)

    if engine is None:
        return False

    try:
        engine.run()
    except EngineError as error:
        print(f"Error: {error}")
        return False

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

    try:
        dispatch(sys.argv[1:])
    except Exception as error:
        # last-resort handler: the program must never crash in review
        print(f"Unexpected error: {error}")


def dispatch(arguments: list[str]) -> None:
    """Chooses between the menu and running one map file."""

    if len(arguments) == 0:
        run_menu(run_simulation, run_visualization)

    elif len(arguments) == 1:
        file_name = arguments[0]

        if run_simulation(file_name):
            run_visualization(file_name)

    else:
        print("Usage: python3 fly_in.py [map_file]")


if __name__ == "__main__":
    main()
