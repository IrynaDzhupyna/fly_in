"""Plans the complete timetable of every drone before the simulation runs.

Idea (reservation table):
    Drones are planned one after another. For each drone, every candidate
    path is tried with a start delay d = 0, 1, 2 ... : the drone waits d
    turns in the start zone, then flies the path without stopping.
    Each step is checked against a table of what earlier drones already
    booked: how many drones are in each zone at the end of each turn, and
    how many use each connection during each turn. The (path, delay) that
    reaches the end zone first is kept and booked in the table.

Why it is always valid:
    every booking respects zone capacity (max_drones) and connection
    capacity (max_link_capacity) at every turn, and a restricted zone is
    always reached in exactly two turns (one on the connection, one to
    arrive), so a drone never waits on a connection.

Why it never gets stuck:
    the start zone has no capacity limit, so a drone can always wait
    there. Once all earlier drones are done, nothing blocks it any more.
"""

from dataclasses import dataclass, field

from connection import Connection
from graph import Graph
from path import Path
from zone import Zone, Zone_role, Zone_type


class SchedulerError(Exception):
    """Custom error for the Scheduler class."""
    pass


@dataclass
class Step:
    """One move of one drone during one turn.

    Attributes:
        turn: the turn in which the move happens (first turn is 1).
        connection: the connection the drone uses.
        zone: the zone the drone is in at the end of the turn, or None
            if the drone is still on the connection towards a
            restricted zone.
        uses_link: False only for the second half of a restricted move:
            the subject frees the connection on the arrival turn, so
            another drone may start crossing it in that same turn.
    """

    turn: int
    connection: Connection
    zone: Zone | None
    uses_link: bool = True

    @property
    def label(self) -> str:
        """Output text of the move, without the drone ID."""

        if self.zone is None:
            return self.connection.name

        return self.zone.name


@dataclass
class DroneSchedule:
    """The full timetable of one drone."""

    drone_id: int
    path: Path
    start_delay: int
    steps: list[Step]

    @property
    def arrival_turn(self) -> int:
        """Turn in which the drone reaches the end zone."""

        return self.steps[-1].turn if self.steps else 0

    def step_at(self, turn: int) -> Step | None:
        """Returns the move made in this turn, or None if the drone
        does not move."""

        index = turn - self.start_delay - 1

        if 0 <= index < len(self.steps):
            step = self.steps[index]
            if step.turn == turn:
                return step

        return None


@dataclass
class ReservationTable:
    """Remembers what earlier drones already booked, turn by turn."""

    zone_count: dict[tuple[str, int], int] = field(default_factory=dict)
    link_count: dict[tuple[str, int], int] = field(default_factory=dict)

    def fits(self, steps: list[Step]) -> bool:
        """Checks if one more drone can make all these moves."""

        for step in steps:
            if step.uses_link:
                key = (step.connection.name, step.turn)
                if self.link_count.get(key, 0) + 1 > \
                        step.connection.max_link_capacity:
                    return False

            zone = step.zone
            if zone is not None and zone.role is Zone_role.HUB:
                inside = self.zone_count.get((zone.name, step.turn), 0)
                if inside + 1 > zone.max_drones:
                    return False

        return True

    def book(self, steps: list[Step]) -> None:
        """Books all moves of one drone."""

        for step in steps:
            if step.uses_link:
                link_key = (step.connection.name, step.turn)
                self.link_count[link_key] = (
                    self.link_count.get(link_key, 0) + 1
                )

            if step.zone is not None:
                zone_key = (step.zone.name, step.turn)
                self.zone_count[zone_key] = (
                    self.zone_count.get(zone_key, 0) + 1
                )


@dataclass
class Scheduler:
    """Builds a timetable for every drone (see module docstring)."""

    graph: Graph
    paths: list[Path]
    table: ReservationTable = field(
        init=False, default_factory=ReservationTable
    )
    links: dict[tuple[str, str], Connection] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        """Indexes connections by the names of both their zones."""

        if not self.paths:
            raise SchedulerError("No paths to schedule drones on")

        for connection in self.graph.connections:
            a, b = connection.zone_a.name, connection.zone_b.name
            self.links[(a, b)] = connection
            self.links[(b, a)] = connection

    def run(self) -> list[DroneSchedule]:
        """Plans all drones, in ID order, and returns their timetables."""

        schedules: list[DroneSchedule] = []

        for drone_id in range(1, self.graph.nb_drones + 1):
            schedule = self._plan_drone(drone_id)
            self.table.book(schedule.steps)
            schedules.append(schedule)

        return schedules

    def _plan_drone(self, drone_id: int) -> DroneSchedule:
        """Finds the (path, start delay) that arrives first."""

        best: DroneSchedule | None = None

        for path in self.paths:
            delay = 0
            steps = self._timeline(path, delay)

            while not self.table.fits(steps):
                delay += 1
                steps = self._timeline(path, delay)

            candidate = DroneSchedule(drone_id, path, delay, steps)

            if best is None or self._is_better(candidate, best):
                best = candidate

        if best is None:
            raise SchedulerError(f"No schedule found for D{drone_id}")

        return best

    def _timeline(self, path: Path, delay: int) -> list[Step]:
        """All moves of a drone that waits `delay` turns in the start
        zone and then flies `path` without stopping."""

        steps: list[Step] = []
        turn = delay

        for here, there in zip(path.zones, path.zones[1:]):
            connection = self.links[(here.name, there.name)]

            if there.type is Zone_type.RESTRICTED:
                # turn 1: on the connection, turn 2: arrives in the zone
                steps.append(Step(turn + 1, connection, None))
                steps.append(Step(turn + 2, connection, there, False))
                turn += 2
            else:
                steps.append(Step(turn + 1, connection, there))
                turn += 1

        return steps

    @staticmethod
    def _is_better(candidate: DroneSchedule, best: DroneSchedule) -> bool:
        """Earlier arrival wins; on a tie, more priority zones, then the
        cheaper path."""

        return (
            candidate.arrival_turn,
            -candidate.path.priority_zones,
            candidate.path.cost,
        ) < (
            best.arrival_turn,
            -best.path.priority_zones,
            best.path.cost,
        )
