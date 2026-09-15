from dataclasses import dataclass, field
from collections import deque

from graph import Graph
from zone import Zone, Zone_type


@dataclass
class Path():
    """
    DATA OBJECT
    - Represents one discovered route
    - Stores its zones
    - Knows the path capacity
    - Stores callculated by PathFinder costs """
    zones: list[Zone]
    # capacity: int
    cost: int
    moves: int


class PathFinderError(Exception):
    """Raises custom error for PathFinder class"""
    pass

@dataclass
class PathFinderAdv:
    """
    - Searches the Graph
    - Finds all possible ways from start to finish
    - calculate/compare route costs
    - choose useful paths
    - Returns: Path objects """

    # what it needs
    graph: Graph

    # what it returns
    all_paths: list[Path] = field(init=False, default_factory=list)

    def find_all_paths(self) -> None:
        """Finds all possible paths"""

        start = Path(
            zones=[self.graph.start],
            cost=0,
            moves=0
        )

        queue: deque[Path] = deque([start])

        while queue:

            path = queue.popleft()
            

    # def find_path(self) -> Path:
    #     """Finds one path"""

    #     start = self.graph.start
    #     end = self.graph.end

    #     queue: deque[Zone] = deque([start])
    #     visited: set[Zone] = {start}
    #     come_from: dict[Zone, Zone | None] = {start: None}

    #     while queue:

    #         current = queue.popleft()

    #         for zone, _connection in self.graph.neighbors(current):

    #             if zone in visited or zone.type is Zone_type.BLOCKED:
    #                 continue
                
    #             queue.append(zone)
    #             visited.add(zone)
    #             come_from[zone] = current

    #     if end not in come_from:
    #         raise PathFinderError("The path doesn't have 'end'")

    #     current: Zone | None = end
    #     valid_path: list[Zone] = []

    #     while current is not None:

    #         valid_path.append(current)
    #         current = come_from[current]

    #     valid_path.reverse()

    #     path = Path(
    #         zones=valid_path,
    #         cost=sum(
    #             zone.type.movement_cost 
    #             for zone in valid_path[1:]),
    #         moves=len(valid_path) - 1
    #     )

    #     # self.all_paths.append(path)
    #     return path

    # def find_all_paths(self) -> None:
    #     pass
