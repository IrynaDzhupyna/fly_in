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
    - Stores callculated by PathFinder costs """
    
    zones: list[Zone]
    cost: int
    moves: int

    # REMOVE ME
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
class PathFinder:
    """
    - Searches the Graph
    - Finds all possible ways from start to finish
    - calculate/compare route costs
    - choose useful paths
    - Returns: Path objects """

    # needs
    graph: Graph
    # return
    # path_set: PathSet

    def run(self) -> PathSet:
        # find all paths
        all_paths = self._find_all_paths()

        print("\nALL PATHS\n")
        for path in all_paths:
            path.info_path()

        # sorted by cost
        sorted_by_cost = sorted(
            all_paths, key=lambda path: path.cost
        )

        if not sorted_by_cost:
            raise PathFinderError(
                "Not valid (from start till end) path found"
            )

        # shared zones detection
        conflicts = self._check_conflicts(sorted_by_cost)

        print("\nCONFLICTS\n")
        for conf in conflicts:
            conf.info_conflict()
        
        # build valid combinations between paths
            # valid combination - group of paths without conflicts
        combinations: list[list[Path]] = self._build_valid_combinations(
            sorted_by_cost, conflicts)

        print("\nVALID COMBINATIONS\n")

        for i, comb in enumerate(combinations):
            print(f"--- COMBINATION {i} ---")

            for path in comb:
                path.info_path()

        # allocate drones and create PathSets
        sets: list[PathSet] = []

        for comb in combinations:

            path_set = PathSet(
                self._drones_assignment(comb)
            )
            sets.append(path_set)


        print("\nPATH SETS\n")
        for path_set in sets:
            print(f"Finishing turns: {path_set.finishing_turn}")

            for assignment in path_set.assignments:
                print(f"Drones: {assignment.drones}")
                print(f"Turns: {assignment.turns}\n")

        # compare the resulting PathSets

        best_path_set = min(sets, key=lambda pathset: pathset.finishing_turn)
        print(best_path_set.finishing_turn)

        # return best_path_set
        return best_path_set

    def _find_all_paths(self) -> list[Path]:
        """Finds all possible paths in a graph"""

        start = Path(
            zones=[self.graph.start],
            cost=0,
            moves=0
        )

        queue_paths: deque[Path] = deque([start])
        all_paths: list[Path] = []

        while queue_paths:

            path = queue_paths.popleft()
            current_zone = path.zones[-1]

            if current_zone is self.graph.end:
                all_paths.append(path)
                continue

            for zone, _connection in self.graph.neighbors(
                current_zone):

                if (zone in path.zones) or (
                    zone.type is Zone_type.BLOCKED):
                    continue

                new_zones = path.zones.copy()
                new_zones.append(zone)

                new_path = Path(
                    zones=new_zones,
                    cost=path.cost + zone.type.movement_cost,
                    moves=path.moves + 1
                )

                queue_paths.append(new_path)

        return all_paths

    def _check_conflicts(self, sorted_paths: list[Path]) -> list[PathConflict]:
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

    def _build_valid_combinations(self, 
                                  sorted_by_cost: list[Path],
                                  conflicts: list[PathConflict]) -> list[list[Path]]:
        """Create all useful non-conflicted path combinations"""

        # branching combinations
        # take a or skip?
        valid_combinations: list[list[Path]] = [[]]

        for path in sorted_by_cost:
            for combination in valid_combinations.copy():

                has_conflict = any(
                    conflict.has_paths(path, chosen)
                    for chosen in combination
                    for conflict in conflicts
                )

                if not has_conflict:
                    new_combination = combination.copy()
                    new_combination.append(path)
                    
                    valid_combinations.append(new_combination)

        return valid_combinations[1:]



    def _drones_assignment(
            self, combination: list[Path]) -> list[PathAssignment]:
        """ Distributes drones between paths"""

        assignments: list[PathAssignment] = []

        for path in combination:
            assignment = PathAssignment(path)
            assignments.append(assignment)

        # distribution
        for _ in range(self.graph.nb_drones):

            smallest_assignment = min(
                assignments,
                key=lambda a: a.path.cost + a.drones
                )
            smallest_assignment.drones += 1

        return assignments


# import sys

# from parser import Parser, ParserError
# from path_finder import PathFinder, PathFinderError


# def main() -> None:

#     file_name = "test_two_paths.txt"

#     parser = Parser(file_name=file_name)
#     try:
#         graph = parser.parse()
#     except ParserError as error:
#         print(f"Error: {error}")
#         return
    
#     path_finder = PathFinder(graph)
#     try:
#         path_finder.run()
#     except PathFinderError as error:
#         print(f"Error: {error}")
#         return


# if __name__ == "__main__":
#     main()



