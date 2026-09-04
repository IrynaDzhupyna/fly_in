from dataclasses import dataclass, field

from graph import Graph
from zone import Zone, Zone_role
from connection import Connection
from drone import Drone, Drone_state
from coordinates import Coordinates

@dataclass
class SimulationEngine:
    """ Simulation engine for running drone simulations."""
    graph: Graph
    drones: list[Drone] = field(init=False, default_factory=list)
    turn: int = 0

    def __post_init__(self) -> None:
        """ Create drones at start"""
        self.drones = []

        for drone in range(1, self.graph.nb_drones + 1):
            drone = Drone(
                id=i,
                state=Drone_state.WAITING,
                current_zone=self.graph.start
            )
            self.drones.append(drone)

    def run(self) -> None:
        """ Run the simulation turn by turn until drones are delivered"""

        while not self.all_drones_delivered():
            self.turn += 1
            pass  # TODO: implement the logic for each turn

    def all_drones_delivered(self) -> bool:
        """ Check if all drones have been delivered"""
        return all(drone.state == Drone_state.DELIVERED for drone in self.drones)

    

