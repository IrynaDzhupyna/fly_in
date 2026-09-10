from dataclasses import dataclass

from graph import Graph


class PathFinder:
    """Finds valid route from start to end"""

    graph: Graph
    # output: one path from START to END

    def find_path(start: Zone, end: Zone):
        queue = [start]
        visited = []
        came_from = []
        