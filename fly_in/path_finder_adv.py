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

        print()
        for zone in self.zones:
            print(zone.name)

        print(f"General cost: {self.cost}")
        print(f"General moves: {self.moves}\n")


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

                if current_zone is end_zone:
                    self.all_paths.append(path)
                    continue


    def info_paths(self) -> None:

        for path in self.all_paths:
            print(path.info_path())


            # # proceed the path till the end
            # queue_zones: deque[Zone] = deque([path.zones])
            # visited: set[Zone] = [path.start]
            # come_from: dict[Zone, Zone | None] = {path.start: None}

            # while queue_zones:

            #     current = queue_zones.popleft()

            #     for zone, _connection in self.graph.neighbors(current):

            #         if zone in visited or zone.type is Zone_type.BLOCKED:
            #             continue

            #         queue_zones.append(zone)
            #         visited.add(zone)
            #         come_from[zone] = current

            # if end_zone not in visited:
            #     raise PathFinderError("The path doesn't have 'end' zone")

            # current_zone: Zone | None = end_zone
            # path: list[Zone] = []

            # while current_zone is not None:

            #     path.append(current_zone)
            #     current = come_from[current]

            # path.reverse()
            # self.all_paths.append(path)
            # break
