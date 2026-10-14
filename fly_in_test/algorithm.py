"""A* search for the Fly-in drone network.

Entering a zone costs ``zone.type.movement_cost`` turns (1 for normal and
priority zones, 2 for restricted zones). Blocked zones can never be
entered.
"""

import heapq
from collections import deque
from dataclasses import dataclass, field

from graph import Graph
from path import Path
from zone import Zone, Zone_type


class AStarError(Exception):
    """Custom error for the AStar class."""
    pass


# Safety limit so a huge map can never make the search run forever.
MAX_EXPANSIONS = 200_000


@dataclass
class AStar:
    """A* search over the zone graph.

    Heuristic:
        h(zone) = number of moves from zone to the goal, ignoring costs
        (one reverse BFS from the goal). Every move costs at least one
        turn, so h never overestimates the real cost (admissible) and
        A* returns the cheapest paths first. Map coordinates are not
        used: two zones far apart on the map can be one move apart, so
        a distance heuristic could overestimate.

    Tie-breaks between equal-cost paths:
        1. more priority zones first (the subject says to prefer them);
        2. otherwise the path found first (keeps results deterministic).
    """

    graph: Graph
    adjacency: dict[str, list[Zone]] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Builds the adjacency list once, so each expansion is fast."""

        for zone in self.graph.zones.values():
            self.adjacency[zone.name] = []

        for connection in self.graph.connections:
            self.adjacency[connection.zone_a.name].append(connection.zone_b)
            self.adjacency[connection.zone_b.name].append(connection.zone_a)

    def find_path(self) -> Path:
        """Returns the single cheapest path from start to end.

        Raises:
            AStarError: if the end zone cannot be reached.
        """

        paths = self.cheapest_paths(1)

        if not paths:
            raise AStarError(
                f"No path from '{self.graph.start.name}' "
                f"to '{self.graph.end.name}'"
            )

        return paths[0]

    def cheapest_paths(self, limit: int) -> list[Path]:
        """Returns up to `limit` simple paths from start to end,
        cheapest first.

        Works like A*, but the search state is a whole partial path
        instead of a single zone, so the same zone can be reached by
        several different paths. Paths never visit a zone twice.
        """

        start = self.graph.start
        goal = self.graph.end
        heuristic = self._hop_distances(goal)

        if start.name not in heuristic:
            return []

        found: list[Path] = []
        counter = 0
        # entries: (f, -priority_zones, counter, cost, zones)
        open_heap: list[tuple[int, int, int, int, list[Zone]]] = [
            (heuristic[start.name], 0, counter, 0, [start])
        ]
        expansions = 0

        while open_heap and len(found) < limit:
            _f, neg_priority, _order, cost, zones = heapq.heappop(open_heap)
            current = zones[-1]

            if current is goal:
                found.append(
                    Path(zones=zones, cost=cost, moves=len(zones) - 1)
                )
                continue

            expansions += 1
            if expansions > MAX_EXPANSIONS:
                break

            for neighbor in self.adjacency[current.name]:
                if neighbor.name not in heuristic or neighbor in zones:
                    continue

                new_cost = cost + neighbor.type.movement_cost
                priority = -neg_priority + self._is_priority(neighbor)

                counter += 1
                heapq.heappush(open_heap, (
                    new_cost + heuristic[neighbor.name],
                    -priority,
                    counter,
                    new_cost,
                    zones + [neighbor],
                ))

        return found

    def _hop_distances(self, goal: Zone) -> dict[str, int]:
        """Reverse BFS from the goal: fewest moves from each zone to it.

        Blocked zones and zones that cannot reach the goal are left out.
        """

        distances: dict[str, int] = {goal.name: 0}
        queue: deque[Zone] = deque([goal])

        while queue:
            zone = queue.popleft()

            for neighbor in self.adjacency[zone.name]:
                if neighbor.name in distances:
                    continue
                if neighbor.type is Zone_type.BLOCKED:
                    continue

                distances[neighbor.name] = distances[zone.name] + 1
                queue.append(neighbor)

        return distances

    @staticmethod
    def _is_priority(zone: Zone) -> int:
        """Returns 1 for a priority zone, 0 otherwise."""

        return 1 if zone.type is Zone_type.PRIORITY else 0
