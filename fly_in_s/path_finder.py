from dataclasses import dataclass

from graph import Graph
from path import Path
from algorithm import AStar


class PathFinderError:
    """Custom error for PathFinder class"""
    pass


MAX_CANDIDATE_PATHS = 1


@dataclass
class PathFinder:
    """Finds the candidate routes the drones can use.
    
    The PathFinder decides:
        - which routes exists
        - how much they cost
        
    When each drone flies is decided later by Scheduler.
    """

    graph: Graph

    def run(self) -> list[Path]:
        """Returns:
            the cheapest paths from start to end, cheapest first.
        
        Raises:
            PathFinderError: if the end cannot be reached."""

        paths = AStar(self.graph).cheapest_paths(MAX_CANDIDATE_PATHS)

        if not paths:
            raise PathFinderError(
                f"No valid path from '{self.graph.start.name}'"
                f"to '{self.graph.end.name}'"
            )
        return paths