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

    def info_path(self) -> None:

        for zone in self.zones:

            print(zone.name)

        print(f"General cost: {self.cost}")
        print(f"General moves: {self.moves}\n")


class PathFinderError(Exception):
    """Custom error for PathFinder class"""
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

        start_zone = self.graph.start
        end_zone = self.graph.end

        # starting point of all paths
        start = Path(
            zones=[start_zone],
            cost=0,
            moves=0
        )

        # queue of all paths, only start at the beginning
        queue_paths: deque[Path] = deque([start])

        while queue_paths:

            path = queue_paths.popleft()
            current_zone = path.zones[-1]

            if current_zone is end_zone:
                self.all_paths.append(path)
                continue

            for zone, _connection in self.graph.neighbors(current_zone):

                if zone in path.zones or zone.type is Zone_type.BLOCKED:
                    continue

                # list concatenation V1
                # new_path: Path = path.zones + [zone]

                new_zones = path.zones.copy()
                new_zones.append(zone)

                new_path = Path(
                    zones=new_zones,
                    cost=path.cost + zone.type.movement_cost,
                    moves=path.moves + 1
                )

                queue_paths.append(new_path)

    def find_best_paths(self) -> None:
        """Decides which paths to use to move all drones
        to end in fewest simulation turns"""

        # sorting by min cost
        print("\nSORTING BY COST\n")
        sorted_by_cost = sorted(self.all_paths, key=lambda path: path.cost)

        for path in sorted_by_cost:
            path.info_path()

        print("\nSORTING BY MOVES\n")
        sorted_by_move = sorted(sorted_by_cost, key=lambda path: path.moves)
        for path in sorted_by_move:
            path.info_path()
        # calls: conflicted_zones(sorted_paths)

    def conflicted_zones(self, sorted_paths: list[Path]) -> None:
        """Compare best zones and detects shared/conflicted ones"""

        conflicted: list[Zone] = []

        # list of list -> list of set
        # path_1, path_2

        i = 0
        
        while sorted_paths:
            path_a = sorted_paths[i]
            path_b = sorted_paths[i + 1]





    def info_paths(self) -> None:

        # debug with 2 ways:
        #   import pdb; pdb.set_trace()
        #   breakpoint()

        for path in self.all_paths:
            path.info_path()
