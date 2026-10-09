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

    def run(self) -> bool:
        """Activates the movement coordinator"""

        next_moves: list[NextMove] = self._intended_movements()
        
        for move in next_moves:
            can_move = self._can_move_to(
                move.drone, move.zone, move.connection)
            
            if not can_move:
                pass

    def _intended_movements(self):
        """Checks and future moves of all drones
        and returns the list of them"""

        zones_to: list[NextMove] = []

        for route in self.drone_routes:

            drone = route.drone
            
            if drone.state is Drone_state.DELIVERED:
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
