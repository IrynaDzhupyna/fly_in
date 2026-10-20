from dataclasses import dataclass

from zone import Zone, Zone_type


@dataclass
class Path:
    """One route from start zone to end zone.

    Attributes:
        zones: every zone of the route, start and end included
        cost: turns a drone need without waiting
            - normal/priority - 1 turn
            - restricted - 2 turns
        moves: number of hops between zones
    """

    zones: list[Zone]
    cost: int
    moves: int

    @property
    def nb_priority_zones(self) -> int:
        """Number of priority zones on the route"""

        return sum(
            1 for zone in self.zones if zone.type is Zone_type.PRIORITY)

    @property
    def names(self) -> list[str]:
        """Zone names of the route, for printing and debugging."""

        return [zone.name for zone in self.zones]
