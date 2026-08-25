from dataclasses import dataclass
from zone import Zone


@dataclass
class Connection:
    zone_a: Zone
    zone_b: Zone
    occupants: int = 0
    max_link_capacity: int = 1

    def another_end(self, zone: Zone) -> Zone:
        if zone is self.zone_a:
            return self.zone_b
        elif zone is self.zone_b:
            return self.zone_a
        else:
            raise ValueError(f"'{zone}' is not part of this connecton")

    def has_space_v1(self, drones_to_move: int) -> bool:
        # drones_to_move if not enpough move as much as possible - rest should wait
        if drones_to_move <= 0:
            return False
        
        if self.occupants + drones_to_move >= self.max_link_capacity:
            return False

        return True

    def has_space_v2(self) -> bool:
        if self.occupants + 1 <= self.max_link_capacity:
            return True

        return False
        
