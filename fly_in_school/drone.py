from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from zone import Zone, Zone_role
from connection import Connection


class Drone_state(Enum):
    """ Describes the state of drones"""

    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


@dataclass
class Drone:
    """ Singular drone moving through the net"""

    id: int
    state: Drone_state
    current_zone: Zone
    current_connection: Connection | None = None

    turns_taken: int = 0

    def move_to_zone(self, zone: Zone) -> None:
        """Moves drone to the next zone"""

        self.current_zone = zone
        self.current_connection = None
        self.state = Drone_state.AVAILABLE
        self.turns_taken += 1

    def move_to_connection(self, connection: Connection) -> None:
        """Moves drones on connection if the next zone is restricted,
         marks drone as in_transit"""

        self.current_connection = connection
        self.state = Drone_state.IN_TRANSIT
        self.turns_taken += 1

    def mark_delivered(self) -> None:
        """Marks drone as delivered if it arrived to end zone"""

        if self.current_zone.role is Zone_role.END:
            self.state = Drone_state.DELIVERED
