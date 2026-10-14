from dataclasses import dataclass, field

from drone import Drone, Drone_state
from graph import Graph
from scheduler import DroneSchedule, Step
from zone import Zone_role


class EngineError(Exception):
    """Custom exception of SimulationEngine class."""
    pass


@dataclass
class SimulationEngine:
    """Plays the drones' timetables turn by turn.

    The Scheduler decides who moves when; the engine executes those
    moves, keeps drones, zones and connections up to date (the visual
    reads them), and double-checks every capacity rule after each turn.
    """

    graph: Graph
    schedules: list[DroneSchedule]

    drones: list[Drone] = field(init=False, default_factory=list)
    turn: int = field(init=False, default=0)
    last_line: str = field(init=False, default="")

    @property
    def is_finished(self) -> bool:
        """Returns True when all drones are delivered."""

        return all(
            drone.state is Drone_state.DELIVERED for drone in self.drones
        )

    @property
    def total_turns(self) -> int:
        """Number of turns the whole simulation takes."""

        return max(
            (schedule.arrival_turn for schedule in self.schedules),
            default=0,
        )

    def __post_init__(self) -> None:
        """Creates one drone per timetable, all in the start zone."""

        for schedule in self.schedules:
            drone = Drone(
                id=schedule.drone_id,
                state=Drone_state.AVAILABLE,
                current_zone=self.graph.start,
            )
            self.drones.append(drone)
            self.graph.start.occupants += 1

    def run(self) -> None:
        """Runs turns until every drone is delivered, printing each turn."""

        while not self.is_finished:
            print(self.run_turn())

    def run_turn(self) -> str:
        """Executes one turn and returns its output line.

        All moves of a turn happen at the same time: first every moving
        drone leaves its zone or connection, then every drone takes its
        new place. So a place freed in this turn can be used in this turn.
        """

        if self.is_finished:
            return ""

        self.turn += 1
        moves: list[tuple[Drone, Step]] = []

        for schedule, drone in zip(self.schedules, self.drones):
            step = schedule.step_at(self.turn)
            if step is not None:
                moves.append((drone, step))

        for drone, _step in moves:
            self._leave_current_place(drone)

        for drone, step in moves:
            self._enter_new_place(drone, step)

        self._check_capacities()

        self.last_line = " ".join(
            f"D{drone.id}-{step.label}" for drone, step in moves
        )
        return self.last_line

    def _leave_current_place(self, drone: Drone) -> None:
        """Removes a moving drone from its zone or connection."""

        if drone.current_connection is not None:
            drone.current_connection.decrease_capacity(drone)
        else:
            drone.current_zone.decrease_capacity()

    def _enter_new_place(self, drone: Drone, step: Step) -> None:
        """Puts a moving drone on its connection or into its new zone."""

        if step.zone is None:
            step.connection.increase_capacity(drone)
            drone.move_to_connection(step.connection)
            return

        step.zone.occupants += 1
        drone.move_to_zone(step.zone)

        if step.zone.role is Zone_role.END:
            drone.mark_delivered()

    def _check_capacities(self) -> None:
        """Safety net: no zone may hold more drones than allowed."""

        for zone in self.graph.zones.values():
            if zone.role is not Zone_role.HUB:
                continue

            if zone.occupants > zone.max_drones:
                raise EngineError(
                    f"Turn {self.turn}: zone '{zone.name}' holds "
                    f"{zone.occupants} drones (max {zone.max_drones})"
                )
