from dataclasses import dataclass, field

from graph import Graph
from path import Path
from connection import Connection
from zone import Zone


class SchedulerError(Exception):
    """Raised when a drone can not be scheduled."""
    pass


@dataclass
class Step:
    """One move of one drone during one turn."""
    turn: int
    connection: Connection
    zone: Zone | None
    uses_link: bool = True

    @property
    def label(self) -> str:
        if self.zone is None:
            return self.connection.name
        return self.zone.name


@dataclass
class DroneScheduler:
    """Complete timetable for one drone."""

    drone_id: int
    path: Path
    steps: list[Step]

    def arrival_turn(self) -> int:
        """Returns the turn on each drone arrives to end"""
        # return self.steps[-1].turn if self.steps else 0
        if not self.steps:
            return 0
        return self.steps[-1].turn

    def step_at(self, turn: int) -> Step | None:
        for step in self.steps:
            if step.turn == turn:
                return step
        return None


@dataclass
class Scheduler:
    """Coordinates the movement of all drones"""

    graph: Graph
    paths: list[Path]

    reserved_zones: dict[tuple[str, int], int] = field(
        init=False,
        default_factory=dict
    )

    reserved_connections: dict[tuple[str, int], int] = field(
        init=False,
        default_factory=dict
    )

    connections: dict[tuple[str, str], Connection] = field(
        init=False,
        default_factory=dict
    )

    def post_init_(self) -> None:
        if not self.paths:
            raise SchedulerError("No path available.")

        for connection in self.grap.connections:
            a = connection.zone_a.name
            b = connection.zone_b.name

            self.connections[(a, b)] = connection
            self.connections[(b, a)] = connection

    def make_steps(self, path: Path, delay: int) -> list[Step]:
        """Create a timetable for a path and departure delay."""

        steps: list[Step] = []
        turn = delay

        

