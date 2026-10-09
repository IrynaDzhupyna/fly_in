from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from zone import Zone

if TYPE_CHECKING:
    from drone import Drone

class ConnectionError(Exception):
    """Custom errors from Connection class."""
    pass


@dataclass
class Connection:
    """ Link between zone_a and zone_b"""

    zone_a: Zone
    zone_b: Zone

    occupants: list[Drone] = field(default_factory=list)
    max_link_capacity: int = 1

    @property
    def name(self) -> str:
        return f"{self.zone_a.name}-{self.zone_b.name}"

    def __post_init__(self) -> None:
        # i think this should be in the parser, not here
        if self.zone_a == self.zone_b:
            raise ConnectionError(
                "Connection cannot link a zone to itself")

        if self.max_link_capacity < 1:
            raise ConnectionError("Max link capacity should be 1 or more")

    def connected(self, zone: Zone) -> bool:
        return zone is self.zone_a or zone is self.zone_b

    def another_end(self, zone: Zone) -> Zone:
        if zone is self.zone_a:
            return self.zone_b
        if zone is self.zone_b:
            return self.zone_a
        raise ConnectionError(f"'{zone.name}' is not part of this connection")

    def has_capacity(self) -> bool:
        return len(self.occupants) < self.max_link_capacity

    def increase_capacity(self, drone: Drone) -> None:
        """Add a drone to the connection."""

        if not self.has_capacity():
            raise ConnectionError("Connection is full")

        if drone in self.occupants:
            raise ConnectionError("Drone already occupies connection")

        self.occupants.append(drone)

    def decrease_capacity(self, drone: Drone) -> None:
        """Remove a drone from the connection."""

        if drone not in self.occupants:
            raise ConnectionError("Drone is not on connection")

        self.occupants.remove(drone)