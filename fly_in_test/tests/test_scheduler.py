"""Unit tests for the Scheduler and the SimulationEngine on tiny maps."""

from connection import Connection
from graph import Graph
from path import Path
from scheduler import Scheduler, DroneSchedule
from simulation_engine import SimulationEngine
from zone import Coordinates, Zone, Zone_role, Zone_type


def zone(name: str, role: Zone_role = Zone_role.HUB,
         kind: Zone_type = Zone_type.NORMAL, capacity: int = 1) -> Zone:
    """Builds a zone with dummy coordinates."""

    return Zone(name=name, coordinates=Coordinates(0, 0), role=role,
                type=kind, max_drones=capacity)


def link(a: Zone, b: Zone, capacity: int = 1) -> Connection:
    """Builds a connection between two zones."""

    return Connection(zone_a=a, zone_b=b, max_link_capacity=capacity)


def path(zones: list[Zone]) -> Path:
    """Builds a path and its cost from a list of zones."""

    cost = sum(z.type.movement_cost for z in zones[1:])
    return Path(zones=zones, cost=cost, moves=len(zones) - 1)


def graph(zones: list[Zone], links: list[Connection], drones: int) -> Graph:
    """Builds a graph whose first zone is the start, last is the end."""

    return Graph(nb_drones=drones, zones={z.name: z for z in zones},
                 connections=links, start=zones[0], end=zones[-1])


def plan(g: Graph, paths: list[Path]) -> list[DroneSchedule]:
    """Runs the scheduler."""

    return Scheduler(g, paths).run()


def play(g: Graph, schedules: list[DroneSchedule]) -> list[str]:
    """Plays a whole simulation and returns its output lines."""

    engine = SimulationEngine(g, schedules)
    lines: list[str] = []

    while not engine.is_finished:
        lines.append(engine.run_turn())

    return lines


def test_single_file_column_advances_every_turn() -> None:
    start = zone("start", Zone_role.START)
    a = zone("a")
    end = zone("end", Zone_role.END)
    g = graph([start, a, end], [link(start, a), link(a, end)], 3)

    lines = play(g, plan(g, [path([start, a, end])]))

    assert lines == [
        "D1-a",
        "D1-end D2-a",
        "D2-end D3-a",
        "D3-end",
    ]


def test_restricted_zone_takes_two_turns() -> None:
    start = zone("start", Zone_role.START)
    r = zone("r", kind=Zone_type.RESTRICTED)
    end = zone("end", Zone_role.END)
    g = graph([start, r, end], [link(start, r), link(r, end)], 1)

    lines = play(g, plan(g, [path([start, r, end])]))

    assert lines == ["D1-start-r", "D1-r", "D1-end"]


def test_restricted_connection_reused_on_arrival_turn() -> None:
    """Subject example: D2 starts crossing when D1 arrives."""

    start = zone("start", Zone_role.START)
    r = zone("r", kind=Zone_type.RESTRICTED)
    end = zone("end", Zone_role.END)
    g = graph([start, r, end], [link(start, r), link(r, end)], 2)

    lines = play(g, plan(g, [path([start, r, end])]))

    assert lines[0] == "D1-start-r"
    assert lines[1] == "D1-r D2-start-r"


def test_link_capacity_limits_drones_per_turn() -> None:
    start = zone("start", Zone_role.START)
    hub = zone("hub", capacity=4)
    end = zone("end", Zone_role.END)
    g = graph([start, hub, end],
              [link(start, hub, 2), link(hub, end, 4)], 4)

    lines = play(g, plan(g, [path([start, hub, end])]))

    assert lines[0].count("-hub") == 2


def test_zone_capacity_lets_two_drones_in() -> None:
    start = zone("start", Zone_role.START)
    hub = zone("hub", capacity=2)
    end = zone("end", Zone_role.END)
    g = graph([start, hub, end],
              [link(start, hub, 2), link(hub, end, 2)], 2)

    lines = play(g, plan(g, [path([start, hub, end])]))

    assert lines == ["D1-hub D2-hub", "D1-end D2-end"]


def test_two_paths_are_used_in_parallel() -> None:
    start = zone("start", Zone_role.START)
    a = zone("a")
    b = zone("b")
    end = zone("end", Zone_role.END)
    links = [link(start, a), link(start, b), link(a, end), link(b, end)]
    g = graph([start, a, b, end], links, 4)

    schedules = plan(g, [path([start, a, end]), path([start, b, end])])

    assert max(s.arrival_turn for s in schedules) == 3


def test_priority_path_wins_a_tie() -> None:
    start = zone("start", Zone_role.START)
    normal = zone("normal")
    prio = zone("prio", kind=Zone_type.PRIORITY)
    end = zone("end", Zone_role.END)
    links = [link(start, normal), link(start, prio),
             link(normal, end), link(prio, end)]
    g = graph([start, normal, prio, end], links, 1)

    schedules = plan(
        g, [path([start, normal, end]), path([start, prio, end])]
    )

    assert schedules[0].path.zones[1] is prio


def test_engine_never_overfills_a_zone() -> None:
    start = zone("start", Zone_role.START)
    a = zone("a")
    end = zone("end", Zone_role.END)
    g = graph([start, a, end], [link(start, a), link(a, end)], 5)
    engine = SimulationEngine(g, plan(g, [path([start, a, end])]))

    while not engine.is_finished:
        engine.run_turn()
        assert a.occupants <= a.max_drones

    assert end.occupants == 5
