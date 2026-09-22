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
    cost: int
    moves: int

    def info_path(self) -> None:
        for zone in self.zones:
            print(zone.name)

        print(f"General cost: {self.cost}")
        print(f"General moves: {self.moves}\n")


@dataclass
class PathAssignment:
    """Assigns a path to a number of drones 
    and calculates the number of turns it will take to finish"""

    path: Path
    drones: int = 0
    turns: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        """Calculates the number of turns it will take to finish"""
        if self.drones == 0:
            return
        self.turns = self.path.cost + self.drones - 1

    def info_assignment(self) -> None:
        print(f"Drones assigned: {self.drones}")


@dataclass
class PathSet:
    """ Represents the set of paths with drones distribution"""

    assignments: list[PathAssignment]
    finishing_turn: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        """Calculates the finishing turns of the set"""
        self.finishing_turn = max(
            assignment.turns for assignment in self.assignments)


@dataclass
class PathConflict:
    path_a: Path
    path_b: Path
    zones: list[Zone]

    def has_paths(self, path_1: Path, path_2: Path) -> bool:
        paths = self.path_a, self.path_b
        return path_1 in paths and path_2 in paths

    def info_conflict(self) -> None:
        print("\nCONFLICTED ZONES\n")
        for zone in self.zones:
            print(zone.name)


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
    # empty now
    chosen_paths: list[Path] = field(init=False, default_factory=list)

    def find_all_paths(self) -> None:
        """Finds all possible paths"""

        start_zone = self.graph.start
        end_zone = self.graph.end

        start = Path(
            zones=[start_zone],
            cost=0,
            moves=0
        )

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
        to end in fewest simulation turns
        - sort paths by cost
        - filter non-conflicted paths from all
        - print debugging info"""

        # one simple path: total_turns = path_cost + nb_drones - 1
        # several independent: simulation_turns= max(each path's finishing turn)

        sorted_by_cost = sorted(self.all_paths, key=lambda path: path.cost)

        if not sorted_by_cost:
            raise PathFinderError("No path from start to end found")

        # print("\nSORTED BY COST\n")

        # for path in sorted_by_cost:
        #     path.info_path()

        """ Filter non-conflicted paths from all and
                stores them in a list from cheapest to more expencive"""

        conflicts = self.conflicting_paths(sorted_by_cost)

        for conf in conflicts:
            conf.info_conflict()

        # non-conflicted paths
        self.chosen_paths = [sorted_by_cost[0]]

        for path in sorted_by_cost[1:]:

            has_conflict = False

            for chosen in self.chosen_paths:

                for conflict in conflicts:
                    if conflict.has_paths(path, chosen):
                        has_conflict = True
                        break

                if has_conflict:
                    break

            if not has_conflict:
                self.chosen_paths.append(path)

        print("\nBEST PATHS\n")
        for path in self.chosen_paths:
            path.info_path()

        assignments = self.drones_assignment()

        # print("\nSORTING BY MOVES\n")
        # sorted_by_move = sorted(sorted_by_cost, key=lambda path: path.moves)
        # for path in sorted_by_move:
        #     path.info_path()
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


    def drones_assignment(self) -> list[PathAssignment]:
        """ Distributes drones between paths"""

        assignments: list[PathAssignment] = []

        for path in self.chosen_paths:
            assignment = PathAssignment(path)
            assignments.append(assignment)

        # distribution
        for i in range(1, self.graph.nb_drones + 1):
            for a in assignments:
                a.turns = a.path.cost + a.drones

            smallest_assignment = min(assignments, key=lambda a: a.turns)
            smallest_assignment.drones += 1

        # finalization
        for a in assignments:
            if a.drones == 0:
                continue
            a.turns = a.path.cost + a.drones - 1

        return assignments

        

