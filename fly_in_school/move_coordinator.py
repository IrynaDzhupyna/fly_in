
from dataclasses import dataclass

from graph import Graph
from zone import Zone, Zone_role, Zone_type
from connection import Connection
from drone import Drone, Drone_state
from drone_route import DroneRoute


@dataclass
class NextMove:
    """Represents one intended drone movement."""

    drone: Drone
    zone: Zone
    connection: Connection


@dataclass
class MoveCoordinator:
    """Plans legal drone movements for one simulation turn.

    Does not change zone occupancy or execute movements.
    """

    graph: Graph
    drone_routes: list[DroneRoute]

    def run(
        self,
        excluded_drones: set[int] | None = None
    ) -> list[NextMove]:
        """Returns approved movements for the current turn.

        excluded_drones contains IDs of drones that have
        already completed a movement during this turn.
        """

        if excluded_drones is None:
            excluded_drones = set()

        next_moves = self._intended_movements(
            excluded_drones
        )

        approved_moves: list[NextMove] = []

        for move in next_moves:

            if move in approved_moves:
                continue

            possible_moves = self._can_move_recursive(
                move,
                next_moves,
                approved_moves
            )

            if possible_moves is None:
                continue

            for possible_move in possible_moves:

                if possible_move not in approved_moves:
                    approved_moves.append(possible_move)

        approved_ids = {
            move.drone.id for move in approved_moves
        }

        for move in next_moves:

            if move.drone.id in approved_ids:
                move.drone.state = Drone_state.AVAILABLE
            else:
                move.drone.state = Drone_state.WAITING

        return approved_moves

    def _intended_movements(
        self,
        excluded_drones: set[int]
    ) -> list[NextMove]:
        """Finds the next desired movement of eligible drones."""

        next_moves: list[NextMove] = []

        for route in self.drone_routes:

            drone = route.drone

            # Drone already moved during this turn.
            if drone.id in excluded_drones:
                continue

            # Delivered and in-transit drones cannot start
            # another movement.
            if (
                drone.state is Drone_state.DELIVERED
                or drone.state is Drone_state.IN_TRANSIT
            ):
                continue

            if route.position + 1 >= len(route.path.zones):
                continue

            next_zone = route.path.zones[
                route.position + 1
            ]

            if next_zone.type is Zone_type.BLOCKED:
                continue

            for zone, connection in self.graph.neighbors(
                drone.current_zone
            ):

                if zone is not next_zone:
                    continue

                next_moves.append(
                    NextMove(
                        drone=drone,
                        zone=zone,
                        connection=connection
                    )
                )

                break

        return next_moves

    def _can_move_recursive(
        self,
        move: NextMove,
        next_moves: list[NextMove],
        approved_moves: list[NextMove],
        visited: set[int] | None = None
    ) -> list[NextMove] | None:
        """Finds departures needed to make movement possible."""

        if visited is None:
            visited = set()

        if move.drone.id in visited:
            return None

        visited.add(move.drone.id)

        if move in approved_moves:
            return []

        possible_moves = [move]

        if self._plan_is_legal(
            approved_moves + possible_moves
        ):
            return possible_moves

        for other_move in next_moves:

            if other_move.drone.current_zone is not move.zone:
                continue

            if other_move in approved_moves:
                continue

            if other_move.drone.id in visited:
                continue

            required_moves = self._can_move_recursive(
                other_move,
                next_moves,
                approved_moves + possible_moves,
                visited.copy()
            )

            if required_moves is None:
                continue

            candidate = required_moves + possible_moves

            if self._plan_is_legal(
                approved_moves + candidate
            ):
                return candidate

        return None

    def _plan_is_legal(
        self,
        moves: list[NextMove]
    ) -> bool:
        """Checks capacities after simultaneous movements."""

        departures: dict[int, int] = {}
        arrivals: dict[int, int] = {}
        connections: dict[int, int] = {}

        zones: dict[int, Zone] = {}
        links: dict[int, Connection] = {}

        drone_ids: set[int] = set()

        for move in moves:

            drone = move.drone
            current_zone = drone.current_zone
            next_zone = move.zone
            connection = move.connection

            if drone.id in drone_ids:
                return False

            drone_ids.add(drone.id)

            if next_zone.type is Zone_type.BLOCKED:
                return False

            if current_zone is next_zone:
                return False

            current_id = id(current_zone)
            next_id = id(next_zone)
            connection_id = id(connection)

            zones[current_id] = current_zone
            zones[next_id] = next_zone
            links[connection_id] = connection

            departures[current_id] = (
                departures.get(current_id, 0) + 1
            )

            arrivals[next_id] = (
                arrivals.get(next_id, 0) + 1
            )

            connections[connection_id] = (
                connections.get(connection_id, 0) + 1
            )

        for connection_id, count in connections.items():

            connection = links[connection_id]

            occupied = len(connection.occupants)

            if (
                occupied + count
                > connection.max_link_capacity
            ):
                return False

        for zone_id, zone in zones.items():

            if (
                zone.role is Zone_role.START
                or zone.role is Zone_role.END
            ):
                continue

            occupied = zone.occupants
            reserved = zone.reserved

            leaving = departures.get(zone_id, 0)
            arriving = arrivals.get(zone_id, 0)

            final_occupancy = (
                occupied
                + reserved
                - leaving
                + arriving
            )

            if final_occupancy > zone.max_drones:
                return False

            if final_occupancy < 0:
                return False

        return True
