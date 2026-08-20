from dataclasses import dataclass, field
from enum import Enum
from zone import Zone, Zone_type, Zone_role
from connection import Connection


class Drone_state(Enum):
    """ Describes the state of drones"""

    WAITING = "waiting"
    ARRIVED = "arrived"
    TRANSIT = "transit"
    DELIVERED = "delivered"

@dataclass
class Drone:
    """ Singular drone moving through the net"""

    id: int
    state: Drone_state
    available_zones: list[str]
    current_zone: Zone
    path: list[str] = field(default_factory=list, init=False)
    turns_taken: int = 0

    def move_forward(self, zone) -> None:
        self.current_zone = zone
        self.path.append(zone)
        self.turns_taken += 1

    # should we have it?
    def move_backwards(self) -> None:
        pass

    def mark_delivered(self) -> None:
        if self.current_zone.role is Zone_role.END:
            self.Drone_state = Drone_state.DELIVERED

    def drone_info(self) -> str:
        print(f"Drone: D{self.id}\nState: {self.state}"
              f"Current zone: {self.current_zone}")