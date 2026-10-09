from dataclasses import dataclass

from drone import Drone
from path_finder import Path


@dataclass
class DroneRoute:
    """Assigned drone and path"""
    drone: Drone
    path: Path
    position: int = 0