from dataclasses import dataclass

from graph import Graph
from zone import Zone, Zone_type


class PathFinderError(Exception):
    pass

@dataclass
class PathFinder:
    """Finds valid route from start to end without
    getting trapped in loops or blocked zones
    
    One the end is reached it returns the path."""
    
    # BUT WHAT IF TWO/MORE PATHES ARE POSSIBLE

    graph: Graph

    def find_path(self) -> list[Zone]:
        """Finds the path from start to end.
            - avoiding revisiting zones
            - avoides blocked zones
            - raises an error if end is unreachable
            
            Returns a forward rout as list[Zone]"""

        start = self.graph.start
        end = self.graph.end

        # FIFO
        queue = [start]
        visited: set[Zone] = {start}
        come_from: dict[Zone, Zone | None] = {start: None}

        while queue:
            # on large graph it is slower because removing index 0 shifts the rest.
            # so later use collections.deque and popleft()
            current = queue.pop(0)
            if current is end:
                break

            for zone, _connection in self.graph.neighbors(current):

                if zone in visited or zone.type is Zone_type.BLOCKED:
                    continue

                queue.append(zone)
                visited.add(zone)
                come_from[zone] = current

        if end not in come_from:
            raise PathFinderError("The path was not found")

        current: Zone | None = end
        path: list[Zone] = []

        while current is not None:
            
            path.append(current)
            current = come_from[current]

        path.reverse()
        return path

