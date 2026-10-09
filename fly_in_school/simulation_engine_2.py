from dataclasses import dataclass, field

from graph import Graph
from zone import Zone, Zone_role, Zone_type
from connection import Connection
from drone import Drone, Drone_state
from path_finder import Path, PathSet


@dataclass
class DroneRoute:
    """Assigned drone and path"""
    drone: Drone
    path: Path
    position: int = 0


class EngineError(Exception):
    """Custom exception of SimulationEngine class"""
    pass


@dataclass
class SimulationEngine:
    """ Enforses the simulation rules.
    Simulation engine for running drone simulations."""

    graph: Graph
    path_set: PathSet

    drones: list[Drone] = field(init=False, default_factory=list)
    drone_routes: list[DroneRoute] = field(
        init=False,
        default_factory=list)
    turn: int = field(init=False, default=0)

    @property
    def is_finished(self) -> bool:
        return self._all_drones_delivered()

    def __post_init__(self) -> None:
        """Initiates the list of drones,
        add drone to start on each iteration"""

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

        drone_index = 0

        for assignment in self.path_set.assignments:
            for _ in range(assignment.drones):
                drone = self.drones[drone_index]

                route = DroneRoute(
                    drone=drone,
                    path=assignment.path
                )

                self.drone_routes.append(route)
                drone_index += 1

    def run(self) -> None:
        """Checks if not all drones delivered and activates the turn"""
        
        while not self.is_finished:
            self.run_turn()

    def run_turn(self) -> None:
        """Iterates through drones and executes one simulation turn"""

        for route in self.drone_routes:
            
            if route.drone.state is Drone_state.DELIVERED:
                continue

            move = self._process_drone(route)
            if move is not None:
                print(move, end=" ")

        self.turn += 1
        print()

    def _process_drone(self, route: DroneRoute) -> str | None:
        """Decide and execute the next action for each drone"""

        drone: Drone = route.drone

        if drone.state is Drone_state.IN_TRANSIT:
            return self._finish_transit(route)

        return self._move_drone(drone, route)

    def _finish_transit(self, route: DroneRoute) -> str:
            """Complete a restricted-zone movement"""
    
            drone = route.drone
            current_connection = drone.current_connection
    
            if current_connection is None:
                raise EngineError("Drone is not on connection")
            
            move_to = route.path.zones[route.position + 1]
    
            current_connection.decrease_capacity(drone)
            move_to.release_reservation()
            move_to.increase_capacity()
    
            drone.move_to_zone(move_to)
            self._check_delivery(drone, move_to)
            route.position += 1
            return f"D{drone.id}-{move_to.name}"

    def _move_drone(self, drone: Drone, route: DroneRoute) -> str | None:
        """Move drone toward the next zone or connection"""

        next_zone: Zone = route.path.zones[route.position + 1]
        neighbors: list[tuple[Zone, Connection]] = self.graph.neighbors(
            drone.current_zone
        )

        for zone, connection in neighbors:
            if zone is not next_zone:
                continue

            if not self._can_move_to(drone, zone, connection):
                return

            drone.current_zone.decrease_capacity()

            if next_zone.type is Zone_type.RESTRICTED:
                next_zone.reserve_capacity()
                connection.increase_capacity(drone)
                drone.move_to_connection()
                return f"D{drone.id}-{drone.current_connection.name}"

            else:
                next_zone.increase_capacity()
                drone.move_to_zone(next_zone)
                result = self._check_delivery(drone, drone.current_zone)
                route.position += 1
                return f"D{drone.id}-{drone.current_zone.name}"

    def _check_delivery(self, drone: Drone, zone: Zone) -> None:
        """Mark drone as delivered if it reached the end"""

        if zone.role is Zone_role.END:
            drone.state = Drone_state.DELIVERED

    def _all_drones_delivered(self) -> bool:

        return all(
            drone.state is Drone_state.DELIVERED
            for drone in self.drones
        )


            
