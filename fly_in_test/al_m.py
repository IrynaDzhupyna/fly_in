from dataclasses import dataclass, field
from collections import deque
import heapq

from graph import Graph
from zone import Zone, Zone_type
from path import Path


# Safety limit so huge map can never make the search run forever
MAX_EXPANSIONS = 200_000


@dataclass(order=True)
class CandidatePath:
    """One partial path waiting to be explored.
    
    Python compares fields from top to bottom,
    so the order of the first three fields is the sorting rule:
        1. lowest estimated total cost (A* rule)
        2. more priority zones (stored negative, so more = smaller)
        3. added earlier (keeps the same every run)"""

    estimated_cost: int
    neg_priority_zones: int
    order: int
    cost: int = field(compare=False)
    zones: list[Zone] = field(compare=False)


class AStarError(Exception):
    """Custom error for the AStar class"""
    pass


@dataclass
class AStar:
    """A* search over the graph.
    
    Tie-breaks between equal-cost paths:
        1. more priority zones first
        2. otherwise the path found first
    """
    
    graph: Graph
    zone_neighbors: dict[str, list[Zone]] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Builds the adjacency list once, so each expansion is fast"""

        for zone in self.graph.zones.values():
            self.zone_neighbors[zone.name] = []

        for connection in self.graph.connections:
            self.zone_neighbors[connection.zone_a.name].append(connection.zone_b)
            self.zone_neighbors[connection.zone_b.name].append(connection.zone_a)

    def find_path(self) -> Path:
        """Returns the single cheapest path from start to end."""

        paths = self.cheapest_paths(1)

        if not paths:
            raise AStarError(
                f"No path from '{self.graph.start.name}'"
                f" to '{self.graph.end.name}'"
            )
        return paths[0]

    def cheapest_paths(self, limit: int) -> list[Path]:
        """Returns up to limit simple paths from start to end,
        cheapest first.
        
        Remembers not only zones but the whole journey"""

        start = self.graph.start
        end = self.graph.end
        if limit <= 0:
            return []

        moves_from_zones: dict[str, int] = self._moves_to_end(end)

        if start.name not in moves_from_zones:
            return []

        # create the priority queue - heap
        found: list[Path] = []

        candidates: list[CandidatePath] = [CandidatePath(
            estimated_cost=moves_from_zones[start.name],
            neg_priority_zones=0,
            order=0,
            cost=0,
            zones=[start])
        ]

        expansions = 0
        order = 0

        while candidates and len(found) < limit:
            current = heapq.heappop(candidates)
            last_zone = candidates.zones[-1]

            if last_zone is end:
                found.append(Path(
                    zones=candidates.zones,
                    cost= current.cost,
                    moves=len(current.zones - 1)
                ))
                continue

            expansions += 1

            if expansions > MAX_EXPANSIONS:
                break

            for neighbor in self.zone_neighbors:
                # ignored blocked
                if neighbor.type is Zone_type.BLOCKED:
                    continue
                # ignore that can not reach the end
                if neighbor.name not in moves_from_zones:
                    continue
                # avoid cycles in the current path
                if neighbor in current.zones:
                    continue

                # g(n): total cost from start
                new_cost = current.cost + neighbor.type.movement_cost

                # f(n) = g(n) + h(n)
                new_estimated_cost = (
                    new_cost + moves_from_zones[neighbor.name]
                )

                # Priority zones with ties
                neg_priority = current.neg_priority_zones

                if neighbor.type is Zone_type.PRIORITY:
                    neg_priority -= 1

                # preserve insertion order for remaining ties
                order += 1

                # adding new partial path to the heap
                heapq.heappush(
                    candidates,
                    CandidatePath(
                        estimated_cost=new_estimated_cost,
                        neg_priority_zones=neg_priority,
                        order=order,
                        cost=new_cost,
                        zones=current.zones + [neighbor]
                    )
                )

        return found

    def _moves_to_end(self, end: Zone) -> dict[str, int]:
        """Reverse BFS from the goal:
        calculates the nb of moves from end to each zone
        ignoring movement cost.
        
        Blocked and zones are not included.
        """

        distances: dict[str, int] = {end.name: 0}
        queue: deque[Zone] = deque([end])

        while queue:
            zone = queue.popleft()

            for neighbor in self.zone_neighbors[zone.name]:
                if neighbor.name in distances:
                    continue
                if neighbor.type is Zone_type.BLOCKED:
                    continue

                distances[neighbor.name] = distances[zone.name] + 1
                queue.append(neighbor)

        return distances
