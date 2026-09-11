from dataclasses import dataclass

from graph import Graph


class PathFinder:
    """Finds valid route from start to end without
    getting trapped in loops or blocked zones"""

    graph: Graph

    def find_path(self):
        """Finds the path from start to end"""

        start = graph.start
        end = graph.end