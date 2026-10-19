
from dataclasses import dataclass, field

from connection import Connection
from graph import Graph
from path import Path
from zone import Zone, Zone_role, Zone_type


class SchedulerError(Exception):
    """Custom error for the Scheduler."""
    pass


@dataclass
class Step:
    """Represents one drone movement during one turn."""

    turn: int
    connection: Connection
    zone: Zone | None
    uses_link: bool = True

    @property
    def label(self) -> str:
        """Returns the name to print for this movement."""

        if self.zone is None:
            return self.connection.name

        return self.zone.name


@dataclass
class DroneSchedule:
    """Stores the planned movements of one drone."""

    drone_id: int
    path: Path
    start_delay: int
    steps: list[Step]

    @property
    def arrival_turn(self) -> int:
        """Returns the turn when the drone reaches the end."""

        if not self.steps:
            return 0

        last_step = self.steps[-1]
        return last_step.turn

    def step_at(self, turn: int) -> Step | None:
        """Finds the drone's movement for a given turn."""

        for step in self.steps:
            if step.turn == turn:
                return step

        return None


@dataclass
class ReservationTable:
    """Tracks occupied zones and connections for each turn."""

    zone_count: dict[tuple[str, int], int] = field(
        default_factory=dict
    )

    link_count: dict[tuple[str, int], int] = field(
        default_factory=dict
    )

    def fits(self, steps: list[Step]) -> bool:
        """Checks whether all planned movements are possible."""

        for step in steps:

            # Check connection capacity
            if step.uses_link:

                link_name = step.connection.name
                key = (link_name, step.turn)

                occupied = self.link_count.get(key, 0)
                capacity = step.connection.max_link_capacity

                if occupied + 1 > capacity:
                    return False

            # Check zone capacity
            zone = step.zone

            if zone is None:
                continue

            if zone.role is not Zone_role.HUB:
                continue

            key = (zone.name, step.turn)

            occupied = self.zone_count.get(key, 0)
            capacity = zone.max_drones

            if occupied + 1 > capacity:
                return False

        return True

    def book(self, steps: list[Step]) -> None:
        """Reserves zones and connections for one drone."""

        for step in steps:

            # Reserve the connection
            if step.uses_link:

                key = (step.connection.name, step.turn)

                occupied = self.link_count.get(key, 0)

                self.link_count[key] = occupied + 1

            # Reserve the destination zone
            if step.zone is not None:

                key = (step.zone.name, step.turn)

                occupied = self.zone_count.get(key, 0)

                self.zone_count[key] = occupied + 1


@dataclass
class Scheduler:
    """Creates movement schedules for all drones."""

    graph: Graph
    paths: list[Path]

    table: ReservationTable = field(
        init=False,
        default_factory=ReservationTable
    )

    links: dict[tuple[str, str], Connection] = field(
        init=False,
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Prepares connections for quick lookup."""

        if not self.paths:
            raise SchedulerError("No paths available")

        for connection in self.graph.connections:

            zone_a = connection.zone_a.name
            zone_b = connection.zone_b.name

            # Connections work in both directions
            self.links[(zone_a, zone_b)] = connection
            self.links[(zone_b, zone_a)] = connection

    def run(self) -> list[DroneSchedule]:
        """Creates a schedule for every drone."""

        schedules: list[DroneSchedule] = []

        for drone_id in range(1, self.graph.nb_drones + 1):

            # Find the best schedule for this drone
            schedule = self._plan_drone(drone_id)

            # Reserve its movements
            self.table.book(schedule.steps)

            # Save the schedule
            schedules.append(schedule)

        return schedules

    def _plan_drone(self, drone_id: int) -> DroneSchedule:
        """Finds the earliest possible arrival for one drone."""

        best_schedule: DroneSchedule | None = None

        for path in self.paths:

            delay = 0

            # Try starting immediately
            steps = self._timeline(path, delay)

            # If blocked, wait at the start and try again
            while not self.table.fits(steps):

                delay += 1
                steps = self._timeline(path, delay)

            # We found a valid schedule for this path
            candidate = DroneSchedule(
                drone_id=drone_id,
                path=path,
                start_delay=delay,
                steps=steps
            )

            # Compare with the best schedule found so far
            if best_schedule is None:
                best_schedule = candidate

            elif self._is_better(candidate, best_schedule):
                best_schedule = candidate

        if best_schedule is None:
            raise SchedulerError(
                f"No schedule found for drone {drone_id}"
            )

        return best_schedule

    def _timeline(self, path: Path, delay: int) -> list[Step]:
        """Builds all movements for a path and start delay."""

        steps: list[Step] = []

        turn = delay

        # Visit every pair of neighboring zones
        for index in range(len(path.zones) - 1):

            current_zone = path.zones[index]
            next_zone = path.zones[index + 1]

            key = (current_zone.name, next_zone.name)
            connection = self.links[key]

            # Restricted zones require two turns
            if next_zone.type is Zone_type.RESTRICTED:

                # First turn: enter the connection
                turn += 1

                first_step = Step(
                    turn=turn,
                    connection=connection,
                    zone=None,
                    uses_link=True
                )

                steps.append(first_step)

                # Second turn: arrive at the restricted zone
                turn += 1

                second_step = Step(
                    turn=turn,
                    connection=connection,
                    zone=next_zone,
                    uses_link=False
                )

                steps.append(second_step)

            else:

                # Normal and priority zones take one turn
                turn += 1

                step = Step(
                    turn=turn,
                    connection=connection,
                    zone=next_zone,
                    uses_link=True
                )

                steps.append(step)

        return steps

    @staticmethod
    def _is_better(
        candidate: DroneSchedule,
        best: DroneSchedule
    ) -> bool:
        """Compares two schedules and chooses the better one."""

        # First priority: arrive earlier
        if candidate.arrival_turn < best.arrival_turn:
            return True

        if candidate.arrival_turn > best.arrival_turn:
            return False

        # Second priority: more priority zones
        if candidate.path.priority_zones > best.path.priority_zones:
            return True

        if candidate.path.priority_zones < best.path.priority_zones:
            return False

        # Third priority: lower path cost
        if candidate.path.cost < best.path.cost:
            return True

        return False
