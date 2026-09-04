from collections import deque
from dataclasses import dataclass, field

from drone import Drone, Drone_state
from graph import Graph
from zone import Zone, Zone_role, Zone_type
from connection import Connection


class SimulationError(Exception):
    """ Raised when the simulation has no route or cannot make progress"""


@dataclass
class SimulationEngine:
    """ Simulation engine for running drone simulations.
        Referee not strategist:
        - turn counter
        - the current occupancy of each zone and connection
        - in-transit state of restricted zones moves
        - which drones have been delivered

        Design choices (unspecified by the map format,
        adjust if the spec says otherwise):
        - start_hub/end_hub are exempt from max_drones capacity
        - max_link_capacity limits crossings per turn,
          not standing occupancy
        - a drone always advances to its closest-to-end
          available neighbor (greedy, not flow-optimal
          path assignment)"""
    graph: Graph
    drones: list[Drone] = field(init=False, default_factory=list)
    turn: int = 0
    distances: dict[str, int] = field(init=False, default_factory=dict)
    busy_until: dict[int, int] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """ Create drones at start, precompute distance-to-end"""
        self.drones = [
            Drone(
                id=i,
                state=Drone_state.WAITING,
                current_zone=self.graph.start,
            )
            for i in range(1, self.graph.nb_drones + 1)
        ]
        self.distances = self._distances_to_end()

        if self.graph.start.name not in self.distances:
            raise SimulationError(
                f"No route from '{self.graph.start.name}' "
                f"to '{self.graph.end.name}'")

    def run(self) -> None:
        """ Run the simulation turn by turn until drones are delivered"""
        while not self.all_drones_delivered():
            self.turn += 1
            moves = self._play_turn()

            if moves:
                print(" ".join(moves))
            elif not self._any_drone_pending():
                raise SimulationError(
                    f"Deadlocked at turn {self.turn}: no drone can move")

        print(f"All drones delivered in {self.turn} turns")

    def all_drones_delivered(self) -> bool:
        """ Check if all drones have been delivered"""
        return all(
            drone.state is Drone_state.DELIVERED for drone in self.drones)

    def _any_drone_pending(self) -> bool:
        """ Whether a non-delivered drone is only resting (restricted-zone
            dwell) rather than genuinely stuck, so an empty turn isn't
            a deadlock"""
        return any(
            self.busy_until.get(drone.id, 0) >= self.turn
            for drone in self.drones
            if drone.state is not Drone_state.DELIVERED
        )

    def _play_turn(self) -> list[str]:
        """ Attempt to move every waiting drone once; returns the moves"""
        for connection in self.graph.connections:
            connection.occupants = []

        moves = []
        for drone in self.drones:
            if drone.state is Drone_state.DELIVERED:
                continue
            if self.busy_until.get(drone.id, 0) >= self.turn:
                continue

            move = self._advance(drone)
            if move is not None:
                moves.append(move)

        return moves

    def _advance(self, drone: Drone) -> str | None:
        """ Move a drone one hop closer to end if a slot is free"""
        next_zone, connection = self._choose_next_hop(drone)
        if next_zone is None or connection is None:
            return None

        connection.occupants.append(drone.id)

        if drone.current_zone.role not in (Zone_role.START, Zone_role.END):
            drone.current_zone.decrease_capacity(1)
        if next_zone.role not in (Zone_role.START, Zone_role.END):
            next_zone.increase_capacity(1)

        drone.move_forward(next_zone)
        drone.state = Drone_state.TRANSIT
        drone.mark_delivered()

        if next_zone.type is Zone_type.RESTRICTED:
            self.busy_until[drone.id] = (
                self.turn + next_zone.type.movement_cost - 1)

        return f"D{drone.id}-{next_zone.name}"

    def _choose_next_hop(
            self, drone: Drone) -> tuple[Zone | None, Connection | None]:
        """ Pick the closest-to-end neighbor with a free zone/link slot"""
        current_distance = self.distances[drone.current_zone.name]

        candidates = sorted(
            (
                (zone, connection)
                for zone, connection in self.graph.neighbors(
                    drone.current_zone)
                if zone.name in self.distances
                and self.distances[zone.name] < current_distance
            ),
            key=lambda pair: self.distances[pair[0].name],
        )

        for zone, connection in candidates:
            if connection.has_capacity() and self._has_room(zone):
                return zone, connection

        return None, None

    def _has_room(self, zone: Zone) -> bool:
        """ Whether a drone can still enter this zone this turn"""
        return (
            zone.role in (Zone_role.START, Zone_role.END)
            or zone.occupants < zone.max_drones
        )

    def _distances_to_end(self) -> dict[str, int]:
        """ BFS distance from every reachable zone to end, skips blocked"""
        distances = {self.graph.end.name: 0}
        queue = deque([self.graph.end])

        while queue:
            zone = queue.popleft()
            for neighbor, _ in self.graph.neighbors(zone):
                if (
                    neighbor.type is Zone_type.BLOCKED
                    or neighbor.name in distances
                ):
                    continue
                distances[neighbor.name] = distances[zone.name] + 1
                queue.append(neighbor)

        return distances
