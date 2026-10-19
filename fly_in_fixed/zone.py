from dataclasses import dataclass, field
from enum import Enum


class Zone_role(Enum):
    """Role of a zone in the network: where drones start, end or pass."""

    START = "start"
    END = "end"
    HUB = "hub"


class Zone_type(Enum):
    """Zone type from the map metadata, decides the movement cost."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def movement_cost(self) -> int:
        """Turns needed to move into a zone of this type."""

        return 2 if self is Zone_type.RESTRICTED else 1


@dataclass
class Coordinates:
    """Position of a zone on the map, used only for drawing."""

    x: int
    y: int


@dataclass
class Zone:
    """A Zone hub in the drone network"""

    name: str
    coordinates: Coordinates
    role: Zone_role = Zone_role.HUB
    type: Zone_type = Zone_type.NORMAL
    color: str | None = None
    max_drones: int = 1

    occupants: int = field(default=0, init=False)

    def __hash__(self) -> int:
        """Hashes Zone 'name',
        so it could be used as a key in dict or set"""

        return hash(self.name)

    def add_drone(self) -> None:
        """A drone arrives in the zone.

        Capacity is not checked here: the Scheduler already planned
        every move, and the engine verifies all zones after each turn."""

        self.occupants += 1

    def remove_drone(self) -> None:
        """A drone leaves the zone."""

        if self.occupants > 0:
            self.occupants -= 1
