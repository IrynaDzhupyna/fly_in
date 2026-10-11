from dataclasses import dataclass

from graph import Graph
from zone import Zone
from drone import Drone, Drone_state
from connection import Connection
from drone_route import DroneRoute


@dataclass
class NextMove:
    drone: Drone
    zone: Zone
    connection: Connection


@dataclass
class MoveCoordinator:
    """Decide which drones should enter first zone"""
    
    graph: Graph
    # drones position on/and assigned path
    drone_routes: list[DroneRoute]

    def run(self) -> list[NextMove]:
        """Activates the movement coordinator"""

        next_moves: list[NextMove] = self._intended_movements()
        
        departures: dict[Zone, list[NextMove]] = {}

        planned_arrivals: dict[Zone, int] = {}

        approved_moves: list[NextMove] = []

        for move in next_moves:
            current_zone = move.drone.current_zone

            if current_zone not in departures:
                departures[current_zone] = []
            
            departures[current_zone].append(move)

        for move in next_moves:
            can_move = self._can_move_recursive(move, departures)

            if not can_move:
                continue

            approved_moves.append(move)

        return approved_moves

    def _intended_movements(self) -> list[NextMove]:
        """Checks and future moves of all drones
        and returns the list of them"""

        zones_to: list[NextMove] = []

        for route in self.drone_routes:

            drone = route.drone
            
            if (drone.state is Drone_state.DELIVERED
                or drone.state is Drone_state.IN_TRANSIT):
                continue

            next_to = route.path.zones[route.position + 1]
            neighbours = self.graph.neighbors(
                drone.current_zone
            )

            for zone, connection in neighbours:
                if zone is not next_to:
                    continue

                next_zone = NextMove(
                    drone=drone,
                    zone=next_to,
                    connection=connection
                )

                zones_to.append(next_zone)

        return zones_to

    def _can_move_to(
        self,
        drone: Drone,
        zone: Zone,
        connection: Connection) -> bool:
        """Checks if the turn is allowed"""

        if not zone.has_capacity() or not connection.has_capacity():

            drone.state = Drone_state.WAITING
            return False

        drone.state = Drone_state.AVAILABLE
        return True

    def _can_move_recursive(
            self,
            move: NextMove,
            departures: dict[Zone, list[NextMove]],
            visited: set[int] | None = None) -> bool:
        """Checks if intended zone has capacity and
        if not check drone in intended drone
        if his intended zone has capacity"""

        if visited is None:
           visited = set()

        drone_id = move.drone.id

        if drone_id in visited:
            return False

        visited.add(drone_id)

        if not move.connection.has_capacity():
            return False

        if move.zone.has_capacity():
            return True

        leaving_moves = departures.get(move.zone, [])

        for leaving_move in leaving_moves:
            if self._can_move_recursive(
                leaving_move,
                departures,
                visited.copy()
            ):
               return True

        return False

