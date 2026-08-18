from dataclasses import dataclass, field


@dataclass
class Drone:
    """A single drone moving through the hub network."""

    id: int
    current_zone: str
    path: list[str] = field(default_factory=list)
    delivered: bool = False
    turns_taken: int = 0

    def move_to(self, zone: str) -> None:
        """Move the drone to a new zone and record the turn."""
        self.current_zone = zone
        self.path.append(zone)
        self.turns_taken += 1

    def mark_delivered(self) -> None:
        self.delivered = True

    def drone_info(self) -> None:
        status = "delivered" if self.delivered else "in transit"
        print(f"D{self.id}: {status} at {self.current_zone} (turn {self.turns_taken})")
