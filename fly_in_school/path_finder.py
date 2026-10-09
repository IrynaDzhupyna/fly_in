from dataclasses import dataclass, field
from collections import deque

from zone import Zone, Zone_type
from graph import Graph


class PathFinderError(Exception):
    """Custom error for PathFinder class"""
    pass


@dataclass
class Path:
    """
    DATA OBJECT
    - Represents one discovered route
    - Stores its zones
    - Stores callculated by PathFinder costs """

    zones: list[Zone]
    cost: int
    moves: int

    # REMOVE ME
    # def info_path(self) -> None:
    #     for zone in self.zones:
    #         print(zone.name)

    #     print(f"General cost: {self.cost}")
    #     print(f"General moves: {self.moves}\n")


@dataclass
class PathAssignment:
    """Assigns a path to a number of drones
    and calculates the number of turns it will take to finish"""

    path: Path
    drones: int = 0

    @property
    def turns(self) -> int:
        """Calculates the turns for assigned drones"""

        if self.drones == 0:
            return 0

        return self.path.cost + self.drones - 1

    def info_assignment(self) -> None:
        print(f"Drones assigned: {self.drones}")


@dataclass
class PathSet:
    """ Represents the set of paths (without conflicts)
    with drones distribution"""

    assignments: list[PathAssignment]
    finishing_turn: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        """Calculates the finishing turns of the set"""
        self.finishing_turn = max(
            assignment.turns for assignment in self.assignments)


@dataclass
class PathFinder:
    """Finds the best paths to deliver all drones
    from start to finish in fewest turns"""

    graph: Graph

    def run(self) -> PathSet:
        """The main for all path finding mechanism"""

        all_paths: list[Path] = self._find_all_paths()
        sorted_by_cost: list[Path] = sorted(
            all_paths, key=lambda path: path.cost)

        if not sorted_by_cost:
            raise PathFinderError(
                "No valid paths were found"
            )

        paths_to_use: list[Path] = self._find_paths_to_use(sorted_by_cost)
        return PathSet(
            self._assign_drones(paths_to_use)
        )

    def _find_all_paths(self) -> list[Path]:
        """Finds all possible paths in graph"""

        start = Path(
            zones=[self.graph.start],
            cost=0,
            moves=0
        )

        paths_to_explore: deque[Path] = deque([start])
        all_paths: list[Path] = []

        while paths_to_explore:

            path = paths_to_explore.popleft()
            current_zone = path.zones[-1]

            if current_zone == self.graph.end:
                all_paths.append(path)
                continue

            for zone, _connection in self.graph.neighbors(current_zone):

                if (
                    zone in path.zones or
                        zone.type is Zone_type.BLOCKED):
                    continue

                new_zones = path.zones.copy()
                new_zones.append(zone)

                new_path = Path(
                    zones=new_zones,
                    cost=path.cost + zone.type.movement_cost,
                    moves=path.moves + 1
                )

                paths_to_explore.append(new_path)

        return all_paths

    def _find_paths_to_use(self, sorted_by_cost: list[Path]) -> list[Path]:
        """Finds the most efficient paths to assign drones to"""

        useful_paths: list[Path] = []
        best_finishing_turn: int | None = None

        for path in sorted_by_cost:
            candidate_paths = useful_paths.copy()
            candidate_paths.append(path)

            assignments = self._assign_drones(candidate_paths)
            candidate_set = PathSet(assignments)

            if (best_finishing_turn is None or
                    candidate_set.finishing_turn <= best_finishing_turn):

                useful_paths.append(path)
                best_finishing_turn = candidate_set.finishing_turn

        return useful_paths

    def _assign_drones(
        self, combination: list[Path]
    ) -> list[PathAssignment]:
        """ Distributes drones between paths"""

        assignments: list[PathAssignment] = []

        for path in combination:
            assignment = PathAssignment(path)
            assignments.append(assignment)

        for _ in range(self.graph.nb_drones):

            smallest_assignment = min(
                assignments,
                key=lambda a: a.path.cost + a.drones
                )
            smallest_assignment.drones += 1

        return assignments
