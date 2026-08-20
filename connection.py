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

    def connected(self, zone_a) -> bool:
        pass

    def another_end(self, zone) -> bool:
        pass

    def has_capacity(self) -> bool:
        if self.occupants + 1 < self.max_link_capacity:
            return True
        return False

