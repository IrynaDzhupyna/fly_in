from dataclasses import dataclass

from zone import Zone, Zone_type


@dataclass
class Path:
    """One route from the start zone to the end zone.

    Attributes:
        zones: every zone on the route, start and end included.
        cost: turns a drone needs to fly the route without waiting
            (1 per normal/priority zone, 2 per restricted zone).
        moves: number of hops between zones.
    """

    zones: list[Zone]
    cost: int
    moves: int

    @property
    def priority_zones(self) -> int:
        """Number of priority zones on the route (used as tie-break)."""

        return sum(
            1 for zone in self.zones if zone.type is Zone_type.PRIORITY
        )

    @property
    def names(self) -> list[str]:
        """Zone names of the route, for printing and debugging."""

        return [zone.name for zone in self.zones]
