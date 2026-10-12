"""A* search for the Fly-in drone network.

Finds the cheapest route from one zone to another, where entering a zone
costs ``zone.type.movement_cost`` turns (1 for normal and priority zones,
2 for restricted zones) and blocked zones can never be entered.
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field

from graph import Graph
from path_finder import Path
from zone import Zone, Zone_type


class AStarError(Exception):
    """Custom error for the AStar class."""
    pass


@dataclass
class AStar:
    """A* pathfinder over the zone graph.

    Heuristic:
        h(zone) = the number of moves from ``zone`` to the goal, ignoring
        costs (computed once with a reverse BFS from the goal). Every move
        costs at least 1 turn, so h never overestimates the real cost
        (admissible) and drops by at most 1 per move (consistent). This
        means A* returns an optimal path and never has to reopen a zone.
        Map coordinates are not used: they say nothing about how many
        moves separate two zones, so a distance heuristic would not be
        admissible.

    Tie-breaks between equal-cost paths:
        1. the path with more priority zones wins (the subject says they
           should be preferred);
        2. otherwise the path found first wins (insertion counter), which
           keeps the result deterministic.
    """

    graph: Graph
    adjacency: dict[str, list[Zone]] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Builds the adjacency list once, so each expansion is O(degree)."""

        for zone in self.graph.zones.values():
            self.adjacency[zone.name] = []

        for connection in self.graph.connections:
            self.adjacency[connection.zone_a.name].append(connection.zone_b)
            self.adjacency[connection.zone_b.name].append(connection.zone_a)

    def find_path(
            self,
            start: Zone | None = None,
            goal: Zone | None = None,
            excluded: set[str] | None = None) -> Path:
        """Returns the cheapest path from start to goal.

        Args:
            start: zone to leave from (default: the graph's start hub).
            goal: zone to reach (default: the graph's end hub).
            excluded: names of zones the path must not pass through.

        Returns:
            A Path with its zones, total cost in turns and number of moves.

        Raises:
            AStarError: if the goal cannot be reached.
        """

        start_zone = start if start is not None else self.graph.start
        goal_zone = goal if goal is not None else self.graph.end
        banned = excluded if excluded is not None else set()

        heuristic = self._hop_distances(goal_zone, banned)

        if start_zone.name not in heuristic:
            raise AStarError(
                f"No path from '{start_zone.name}' to '{goal_zone.name}'"
            )

        best_cost: dict[str, int] = {start_zone.name: 0}
        best_priority: dict[str, int] = {start_zone.name: 0}
        came_from: dict[str, Zone] = {}
        closed: set[str] = set()

        counter = 0
        # entries: (f, -priority_zones, counter, g, zone)
        open_heap: list[tuple[int, int, int, int, Zone]] = [
            (heuristic[start_zone.name], 0, counter, 0, start_zone)
        ]

        while open_heap:
            _f, neg_priority, _order, cost, zone = heapq.heappop(open_heap)

            if zone.name in closed:
                continue
            closed.add(zone.name)

            if zone is goal_zone:
                return self._build_path(came_from, start_zone, goal_zone,
                                        cost)

            for neighbor in self.adjacency[zone.name]:
                if not self._can_enter(neighbor, banned, goal_zone):
                    continue
                if neighbor.name in closed:
                    continue

                new_cost = cost + neighbor.type.movement_cost
                new_priority = -neg_priority + self._is_priority(neighbor)

                if not self._is_better(neighbor.name, new_cost, new_priority,
                                       best_cost, best_priority):
                    continue

                best_cost[neighbor.name] = new_cost
                best_priority[neighbor.name] = new_priority
                came_from[neighbor.name] = zone

                counter += 1
                heapq.heappush(open_heap, (
                    new_cost + heuristic[neighbor.name],
                    -new_priority,
                    counter,
                    new_cost,
                    neighbor,
                ))

        raise AStarError(
            f"No path from '{start_zone.name}' to '{goal_zone.name}'"
        )

    def find_disjoint_paths(self, max_paths: int) -> list[Path]:
        """Returns up to max_paths paths that share no intermediate zone.

        Runs A* repeatedly and excludes the zones used by the paths found
        so far. Paths come out cheapest first. This is a greedy method:
        it gives good parallel routes quickly, but is not guaranteed to
        find the largest possible set of disjoint paths.
        """

        paths: list[Path] = []
        used: set[str] = set()

        while len(paths) < max_paths:
            try:
                path = self.find_path(excluded=used)
            except AStarError:
                break

            paths.append(path)
            middle = path.zones[1:-1]

            if not middle:
                # start is connected directly to end: no other path
                # can do better, and excluding nothing would loop forever
                break

            used.update(zone.name for zone in middle)

        if not paths:
            raise AStarError("No valid paths were found")

        return paths

    def _hop_distances(
            self,
            goal: Zone,
            banned: set[str]) -> dict[str, int]:
        """Reverse BFS from the goal: fewest moves from each zone to it.

        Zones missing from the result cannot reach the goal at all.
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
                if neighbor.name in banned:
                    continue

                distances[neighbor.name] = distances[zone.name] + 1
                queue.append(neighbor)

        return distances

    @staticmethod
    def _can_enter(zone: Zone, banned: set[str], goal: Zone) -> bool:
        """Checks if a drone may ever enter this zone on the search."""

        if zone.type is Zone_type.BLOCKED:
            return False

        return zone is goal or zone.name not in banned

    @staticmethod
    def _is_priority(zone: Zone) -> int:
        """Returns 1 for a priority zone, 0 otherwise."""

        return 1 if zone.type is Zone_type.PRIORITY else 0

    @staticmethod
    def _is_better(
            name: str,
            cost: int,
            priority: int,
            best_cost: dict[str, int],
            best_priority: dict[str, int]) -> bool:
        """Checks if a new route to a zone beats the best one known."""

        if name not in best_cost or cost < best_cost[name]:
            return True

        return cost == best_cost[name] and priority > best_priority[name]

    @staticmethod
    def _build_path(
            came_from: dict[str, Zone],
            start: Zone,
            goal: Zone,
            cost: int) -> Path:
        """Walks back from the goal to rebuild the found path."""

        zones: list[Zone] = [goal]
        current = goal

        while current is not start:
            current = came_from[current.name]
            zones.append(current)

        zones.reverse()
        return Path(zones=zones, cost=cost, moves=len(zones) - 1)
