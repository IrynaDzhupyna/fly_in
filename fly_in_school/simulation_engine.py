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
        """
            - manage turns
            - ask pathfinder for desired move
            - check whether desired move is legal
            - engine executes legal move / drone waits
            - update drone, zone, connection state
            - repeat until all drones are delivered """

        while not self._all_drones_delivered():
            self.run_turn()

    def run_turn(self) -> None:
        """Runs one turn of the simulation."""

        # movements = []
        self.turn += 1
        print(f"Turn {self.turn}")

        for route in self.drone_routes:

            drone = route.drone

            if drone.state is not Drone_state.DELIVERED:
                move = self._process_drone(route)
                if move is not None:
                    # movements.append(move)
                    print(move, end=" ")
        print()

    def _process_drone(self, route: DroneRoute) -> str | None:
        """Process one drone during the current turn."""

        # REVIEW ME
        drone = route.drone

        next_zone = route.path.zones[route.position + 1]

        if drone.state is Drone_state.IN_TRANSIT:
            return self._finish_transit(route)

        neighbors = self.graph.neighbors(drone.current_zone)

        for zone, connection in neighbors:

            if zone is not next_zone:
                continue

            if not self._can_move_to(next_zone, connection, drone):
                return

            self._move_drone(drone, next_zone, connection)

            if drone.state is Drone_state.IN_TRANSIT:
                return f"D{drone.id}-{connection.name}"
            
            route.position += 1
            return f"D{drone.id}-{next_zone.name}"

    def _can_move_to(self,
                     zone: Zone,
                     connection: Connection,
                     drone: Drone) -> bool:
        """Checks if the turn is allowed"""

        if not zone.has_capacity() or not connection.has_capacity():

            drone.state = Drone_state.WAITING
            return False

        drone.state = Drone_state.AVAILABLE
        return True

    def _move_drone(
            self,
            drone: Drone,
            zone_to: Zone,
            connection: Connection) -> None:
        """Move drone toward the next zone."""

        drone.current_zone.decrease_capacity()

        if zone_to.type is Zone_type.RESTRICTED:
            zone_to.reserve_capacity()
            connection.increase_capacity(drone)
            drone.move_to_connection(connection)

        else:
            
            zone_to.increase_capacity()
            drone.move_to_zone(zone_to)

            # this should be somewhere else
            if zone_to.role is Zone_role.END:
                drone.mark_delivered()

    def _finish_transit(self, route: DroneRoute) -> str:
        """Move drone from connection to next zone"""

        drone = route.drone
        current_connection = drone.current_connection

        if current_connection is None:
            raise EngineError("Drone is not on connection")
        
        move_to = route.path.zones[route.position + 1]

        current_connection.decrease_capacity(drone)
        move_to.release_reservation()
        move_to.increase_capacity()

        drone.move_to_zone(move_to)
        route.position += 1

        return f"D{drone.id}-{move_to.name}"

    def _all_drones_delivered(self) -> bool:
        """ Returns 'True' if every drone was delivered"""

        for drone in self.drones:
            if drone.state is not Drone_state.DELIVERED:
                return False

        return True

    # remove when it is not needed
    # def info(self, drone: Drone) -> None:
    #     # """ Prints the info about every drone"""
    #     # for drone in self.drones:
    #     #     print(f"Drone id: {drone.id}")
    #     #     print(f"Drone state: {drone.state}")
    #     #     print(f"Current zone: {drone.current_zone}")
    #     #     print()

    #     print(
    #         f"Turn {self.turn}: "
    #         f"D{drone.id} at {drone.current_zone.name}, "
    #         f"state={drone.state.value}, "
    #         f"path={drone.path}"

    def output_info(self) -> None:
        """Outputs the info about every turn.
            Each simulation turn represented by a line.
            A line list all the drones movements, space-separated.
            Format: D<ID>-<zone> or
                    D<ID>-<connection> if in flight towards restricted zone"""

        print(f"Turn {self.turn}:")
        for drone in self.drones:
            if drone.state.value is not Drone_state.DELIVERED:
                if (drone.current_zone.role is not Zone_role.START and
                        drone.current_zone.role is not Zone_role.END):
                    print(f"D{drone.id}-"
                          f"{drone.current_zone.name}", end=" ")
                    print(f"{drone.state}")
        print()
