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
        """
            - manage turns
            - ask pathfinder for desired move
            - check whether desired move is legal
            - engine executes legal move / drone waits
            - update drone, zone, connection state
            - repeat until all drones are delivered """
        
        while not self._all_drones_delivered():
            self.turn += 1

            for drone in self.drones:
                if drone.state is Drone_state.DELIVERED:
                    continue

                self._process_drone(drone)
                self.info(drone)

    def _process_drone(self, drone: Drone) -> None:
        """Process one drone during the current turn."""

        neighbors = self.graph.neighbors(drone.current_zone)

        # testing engine (movment decision)
        for zone, connection in neighbors:
            if not self._can_move_to(zone, connection):
                continue

            if zone is Zone_role.START:
                continue

            self._move_drone(drone, zone)
            break

    def _can_move_to(self,
                     zone: Zone,
                     connection: Connection) -> bool:
        """Checks if the turn is allowed"""

        if not zone.has_capacity():
            return False

        if not connection.has_capacity():
            return False

        return True

    def _move_drone(self, drone: Drone, zone_to: Zone) -> None:
        """ Executes one-turn movemet of drone from one zone to next"""
        # now for one-turn movement only

        zone_from = drone.current_zone

        zone_from.decrease_capacity()
        zone_to.increase_capacity()
        drone.move_forward(zone_to)
        drone.mark_delivered()

    def _all_drones_delivered(self) -> bool:
        """ Checks if every drone was delivered"""

        for drone in self.drones:
            if drone.state is not Drone_state.DELIVERED:
                return False

        return True


    # remove when it is not needed
    def info(self, drone: Drone) -> None:
        # """ Prints the info about every drone"""
        # for drone in self.drones:
        #     print(f"Drone id: {drone.id}")
        #     print(f"Drone state: {drone.state}")
        #     print(f"Current zone: {drone.current_zone}")
        #     print()

        print(
            f"Turn {self.turn}: "
            f"D{drone.id} at {drone.current_zone.name}, "
            f"state={drone.state.value}, "
            f"path={drone.path}"
        )


