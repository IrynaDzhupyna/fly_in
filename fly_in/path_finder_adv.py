from dataclasses import dataclass, field
from collections import deque

from graph import Graph
from zone import Zone, Zone_type, Zone_role


@dataclass
class Path:
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


@dataclass
class PathConflict:
    path_a: Path
    path_b: Path
    zones: list[Zone]


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
    chosen_paths: list[Path] = field(init=False, default_factory=list)

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

        chosen_paths: list[Path] = []

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

    def conflicting_paths(self, sorted_paths: list[Path]) -> list[PathConflict]:
        """Compares zones in two paths and detects shared/conflicted ones"""

        conflicts: list[PathConflict] = []

        for i in range(len(sorted_paths)):
            path_a = sorted_paths[i]

            for j in range(i + 1, len(sorted_paths)):
                path_b = sorted_paths[j]

                shared_zones: list[Zone] = []

                for zone_a in path_a.zones:
                    for zone_b in path_b.zones:
                        if zone_a == zone_b:
                            if zone_a.role is Zone_role.START or zone_a.role is Zone_role.END:
                                continue
                            shared_zones.append(zone_a)

                if not shared_zones:
                    continue

                new_conflict = PathConflict(path_a=path_a,
                                            path_b=path_b,
                                            zones=shared_zones)
                conflicts.append(new_conflict)

        return conflicts








    def info_paths(self) -> None:

        # debug with 2 ways:
        #   import pdb; pdb.set_trace()
        #   breakpoint()

        for path in self.all_paths:
            path.info_path()
