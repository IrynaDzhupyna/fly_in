from dataclasses import dataclass, field

from graph import Graph
from zone import Zone, Zone_role, Zone_type
from connection import Connection
from drone import Drone, Drone_state


@dataclass
class SimulationEngine:
    """ Enforses the simulation rules.
    Simulation engine for running drone simulations."""

    graph: Graph
    drones: list[Drone] = field(init=False, default_factory=list)
    turn: int = 0


    def __post_init__(self) -> None:
        """Initiates the list of drones, add drone to start on each iteration"""

        # initiate drones
        for i in range(1, self.graph.nb_drones + 1):
            drone = Drone(
                id=i,
                state=Drone_state.AVAILABLE,
                current_zone=self.graph.start
            )

            self.drones.append(drone)
            # adds drone to start zone
            self.graph.start.increase_capacity()

    def run(self) -> None:
        """Starts the engine"""
        
        while not self._all_drones_delivered():
            self.turn += 1

            for drone in self.drones:
                if drone.state is not Drone_state.DELIVERED:
                    self._process_drone(drone)

    def _process_drone(self, drone: Drone, next_zone: Zone) -> None:
        # modify later
        neighbors = self.graph.neighbors(drone.current_zone)
        
        for zone, connection in neighbors:
            # check if can be moved to
            # self._can_move_to(drone: Drone, zone: Zone, connection: Connection)
            pass

    def _move_drone(self, drone: Drone, zone_from: Zone, zone_to: Zone) -> bool:
        # move from/to zone.START/END
        pass

    def _can_move_to(self, drone: Drone, zone: Zone, connection: Connection) -> bool:
        """Checks if the turn is allowed"""

        if zone.type is Zone_type.BLOCKED:
            return False

        if not zone.has_capacity():
            return False

        if not connection.has_capacity():
            return False

        return True

        # movement cost 
        # conflicts with other drones

    # executes move OR makes drone wait

    # later we can separate drones that are delivered and others 
    def _all_drones_delivered(self) -> bool:
        all_delivered = True

        for drone in self.drones:
            if drone.state is not Drone_state.DELIVERED:
                all_delivered = False

        return all_delivered
    
    # remove when it is not needed
    def info(self) -> None:
        """ Prints the info about every drone"""
        for drone in self.drones:
            print(f"Drone id: {drone.id}")
            print(f"Drone state: {drone.state}")
            print(f"Current zone: {drone.current_zone}")
            print()
