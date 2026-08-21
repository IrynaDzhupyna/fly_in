from dataclasses import dataclass
from zone import Zone

@dataclass
class Connection:
    """ Link between zone_a and zone_b"""

    zone_a: Zone
    zone_b: Zone
    occupants: list [Zone]
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        if self.zone_a == self.zone_b:
            raise ValueError("Start and finish should have different coordinates")

        if self.max_link_capacity < 1:
            raise ValueError("Max link capacity should be 1 or more")

    def connected(self, zone: Zone) -> bool:
        return zone is self.zone_a or zone is self.zone_b

    def another_end(self, zone: Zone) -> Zone:
        if zone is self.zone_a:
            return self.zone_b
        if zone is self.zone_b:
            return self.zone_a
        raise ValueError(f"'{zone.name}' is not part of this connection")

    def has_capacity(self) -> bool:
        return len(self.occupants) < self.max_link_capacity

