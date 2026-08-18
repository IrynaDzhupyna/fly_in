from dataclasses import dataclass, field


@dataclass
class Connection:
    """A link between two zones that drones can travel across."""

    zone1: str
    zone2: str
    max_link_capacity: int = 1
    # current number of drones using this connection right now
    capacity: int = field(default=0, init=False)

    def connects(self, zone_a: str, zone_b: str) -> bool:
        """Return True if this connection links zone_a and zone_b (either order)."""
        return {zone_a, zone_b} == {self.zone1, self.zone2}

    def other_end(self, zone: str) -> str:
        """Given one end of the connection, return the other end."""
        if zone == self.zone1:
            return self.zone2
        if zone == self.zone2:
            return self.zone1
        raise ValueError(f"{zone!r} is not part of this connection")

    def increase_capacity(self, drones_to_move: int = 1) -> bool:
        """Try to add drones_to_move drones onto this connection. Returns success."""
        if self.capacity + drones_to_move <= self.max_link_capacity:
            self.capacity += drones_to_move
            return True
        return False

    def decrease_capacity(self, drones_to_move: int = 1) -> bool:
        """Try to remove drones_to_move drones from this connection. Returns success."""
        if self.capacity - drones_to_move >= 0:
            self.capacity -= drones_to_move
            return True
        return False

    def connection_info(self) -> None:
        print(f"{self.zone1} <-> {self.zone2}")
        print(f"Capacity: {self.capacity}/{self.max_link_capacity}")
