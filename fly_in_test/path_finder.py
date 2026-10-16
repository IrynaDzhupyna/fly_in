from dataclasses import dataclass

from algorithm import AStar
from graph import Graph
from path import Path


class PathFinderError(Exception):
    """Custom error for PathFinder class"""
    pass


# How many of the cheapest paths the scheduler may choose from.
# More paths = more options for spreading drones, but a slower schedule.
MAX_CANDIDATE_PATHS = 2


@dataclass
class PathFinder:
    """Finds the candidate routes the drones can use.

    The PathFinder only decides WHICH routes exist and how much they cost.
    WHEN each drone flies is decided later by the Scheduler.
    """

    graph: Graph

    def run(self) -> list[Path]:
        """Returns the cheapest paths from start to end, cheapest first.

        Raises:
            PathFinderError: if the end zone cannot be reached.
        """

        paths = AStar(self.graph).cheapest_paths(MAX_CANDIDATE_PATHS)

        if not paths:
            raise PathFinderError(
                f"No valid path from '{self.graph.start.name}' "
                f"to '{self.graph.end.name}'"
            )

        return paths
