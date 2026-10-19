
from dataclasses import dataclass, field

from graph import Graph
from zone import Zone, Zone_role, Zone_type
from drone import Drone, Drone_state
from path_finder import PathSet
from drone_route import DroneRoute
from move_coordinator import MoveCoordinator, NextMove


class EngineError(Exception):
    """Custom exception of SimulationEngine class."""
    pass


@dataclass
class SimulationEngine:
    """Executes drone movements and manages simulation turns."""

    graph: Graph
    path_set: PathSet

    drones: list[Drone] = field(
        init=False,
        default_factory=list
    )
    drone_routes: list[DroneRoute] = field(
        init=False,
        default_factory=list
    )
    turn: int = field(init=False, default=0)

    coordinator: MoveCoordinator = field(init=False)

    @property
    def is_finished(self) -> bool:
        """Returns True when all drones are delivered."""
        return self._all_drones_delivered()

    def __post_init__(self) -> None:
        """Creates drones and assigns their paths."""

        for i in range(1, self.graph.nb_drones + 1):

            drone = Drone(
                id=i,
                state=Drone_state.AVAILABLE,
                current_zone=self.graph.start
            )

            self.drones.append(drone)
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

        self.coordinator = MoveCoordinator(
            graph=self.graph,
            drone_routes=self.drone_routes
        )

    def run(self) -> None:
        """Runs turns until every drone is delivered."""

        while not self.is_finished:
            self.run_turn()

    def run_turn(self) -> None:

        if self.is_finished:
            return

        self.turn += 1
        print(f"turn {self.turn}")
        movements: list[str] = []
        completed_transit: set[int] = set()

        for route in self.drone_routes:

            if route.drone.state is Drone_state.IN_TRANSIT:

                completed_transit.add(route.drone.id)

                transit_line = self._finish_transit(route)
                movements.append(transit_line)

        approved_moves = self.coordinator.run(
            excluded_drones=completed_transit
        )

        for move in approved_moves:
            move.drone.current_zone.decrease_capacity()

        for move in approved_moves:
            result = self._execute_move(move)
            movements.append(result)

        print(" ".join(movements))

    def _finish_transit(self, route: DroneRoute) -> str:
        """Completes a restricted-zone movement."""

        drone = route.drone
        connection = drone.current_connection

        if connection is None:
            raise EngineError("Drone is not on connection")

        next_zone = route.path.zones[route.position + 1]

        connection.decrease_capacity(drone)
        next_zone.release_reservation()

        if not next_zone.increase_capacity():
            raise EngineError(
                f"Cannot finish transit into {next_zone.name}"
            )

        drone.move_to_zone(next_zone)
        route.position += 1

        self._check_delivery(drone, next_zone)

        return f"D{drone.id}-{next_zone.name}"

    def _execute_move(self, move: NextMove) -> str:
        """Executes one movement approved by the coordinator."""

        drone = move.drone
        next_zone = move.zone
        connection = move.connection

        route = self._find_route(drone)

        if next_zone.type is Zone_type.RESTRICTED:

            if not next_zone.reserve_capacity():
                raise EngineError(
                    f"Cannot reserve {next_zone.name}"
                )

            connection.increase_capacity(drone)
            drone.move_to_connection(connection)

            return f"D{drone.id}-{connection.name}"

        if not next_zone.increase_capacity():
            raise EngineError(
                f"Cannot enter {next_zone.name}"
            )

        drone.move_to_zone(next_zone)
        route.position += 1

        self._check_delivery(drone, next_zone)

        return f"D{drone.id}-{next_zone.name}"

    def _find_route(self, drone: Drone) -> DroneRoute:
        """Finds the assigned route for a drone."""

        for route in self.drone_routes:

            if route.drone is drone:
                return route

        raise EngineError(
            f"Route not found for drone D{drone.id}"
        )

    def _check_delivery(
        self,
        drone: Drone,
        zone: Zone
    ) -> None:
        """Marks a drone delivered when it reaches the end."""

        if zone.role is Zone_role.END:
            drone.mark_delivered()

    def _all_drones_delivered(self) -> bool:
        """Checks whether every drone has been delivered."""

        return all(
            drone.state is Drone_state.DELIVERED
            for drone in self.drones
        )
