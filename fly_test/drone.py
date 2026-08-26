from dataclasses import dataclass
from enum import Enum

from zone import Zone, Zone_role

NB_DRONES = 0

class Drone_status(Enum):
    ARRIVED = "arrived"
    IN_PROGESS = "in_progress"
    DELIVERED = "delivered"


@dataclass
class Drone:
    id: int
    current_zone: Zone
    available_zones: list[Zone]
    path: list[Zone]
    status: Drone_status

    def move_forward(self, zone: Zone) -> None:
        if self.current_zone.role is not Zone_role.END:
            self.current_zone = zone
            self.path.append(self.current_zone)
        else:
            self.mark_as_delivered()

    def move_backward(self) -> None:
        if len(self.path) <= 1:
            return
        self.path.pop()
        self.current_zone = self.path[-1]

    def mark_as_delivered(self) -> None:
        self.status = Drone_status.DELIVERED
    

    
