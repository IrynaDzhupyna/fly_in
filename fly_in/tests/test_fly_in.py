"""Regression tests for Fly-in movement planning and simulation.

Place this file in your project's tests/ directory and run:
    poetry run pytest -q tests/test_fly_in.py

The tests use the public classes shown during development. Adjust only the
Path/PathSet/PathAssignment constructor helper if your local API differs.
"""

import pytest

from connection import Connection
from drone import Drone, Drone_state
from drone_route import DroneRoute
from graph import Graph
from move_coordinator import MoveCoordinator
from path_finder import Path, PathAssignment, PathSet
from simulation_engine import SimulationEngine
from zone import Coordinates, Zone, Zone_role, Zone_type


def make_graph(start: Zone, end: Zone, nb_drones: int,
               links: list[Connection]) -> Graph:
    """Builds a real Graph from the zones used by the given links."""
    zones: dict[str, Zone] = {start.name: start, end.name: end}
    for connection in links:
        zones[connection.zone_a.name] = connection.zone_a
        zones[connection.zone_b.name] = connection.zone_b
    return Graph(nb_drones=nb_drones, zones=zones, connections=links,
                 start=start, end=end)


def zone(name: str, role: Zone_role = Zone_role.HUB,
         kind: Zone_type = Zone_type.NORMAL,
         capacity: int = 1) -> Zone:
    return Zone(
        name=name,
        coordinates=Coordinates(0, 0),
        role=role,
        type=kind,
        max_drones=capacity,
    )


def link(a: Zone, b: Zone, capacity: int = 1) -> Connection:
    return Connection(zone_a=a, zone_b=b, max_link_capacity=capacity)


def make_engine(paths: list[tuple[list[Zone], int]],
                links: list[Connection]) -> SimulationEngine:
    start = paths[0][0][0]
    end = paths[0][0][-1]
    graph = make_graph(start, end, sum(n for _, n in paths), links)
    assignments = [
        PathAssignment(Path(zones=nodes, cost=0, moves=0), count)
        for nodes, count in paths
    ]
    return SimulationEngine(graph=graph, path_set=PathSet(assignments))


def run_limited(engine: SimulationEngine, limit: int = 30) -> int:
    """Fail quickly if simulation cannot deliver all drones."""
    for _ in range(limit):
        if engine.is_finished:
            return engine.turn
        engine.run_turn()
    pytest.fail(f"Simulation did not finish within {limit} turns")


def make_coordinator(
    paths: list[list[Zone]],
    links: list[Connection],
) -> tuple[MoveCoordinator, list[Drone]]:
    drones: list[Drone] = []
    routes: list[DroneRoute] = []
    for i, nodes in enumerate(paths, 1):
        drone = Drone(id=i, state=Drone_state.AVAILABLE,
                      current_zone=nodes[0])
        nodes[0].increase_capacity()
        drones.append(drone)
        routes.append(DroneRoute(
            drone=drone, path=Path(zones=nodes, cost=0, moves=0)))
    graph = make_graph(paths[0][0], paths[0][-1], len(paths), links)
    return MoveCoordinator(graph=graph, drone_routes=routes), drones


def test_linear_two_drones_three_turns() -> None:
    start = zone("start", Zone_role.START)
    a = zone("A")
    end = zone("end", Zone_role.END)
    engine = make_engine(
        [([start, a, end], 2)], [link(start, a), link(a, end)]
    )

    assert run_limited(engine) == 3
    assert all(d.state is Drone_state.DELIVERED for d in engine.drones)
    assert a.occupants == 0


def test_restricted_end_requires_two_turns() -> None:
    start = zone("start", Zone_role.START)
    end = zone("end", Zone_role.END, Zone_type.RESTRICTED)
    connection = link(start, end)
    engine = make_engine([([start, end], 1)], [connection])

    engine.run_turn()
    drone = engine.drones[0]
    assert drone.state is Drone_state.IN_TRANSIT
    assert drone.current_connection is connection
    assert not engine.is_finished

    engine.run_turn()
    assert engine.is_finished
    assert engine.turn == 2
    assert drone.state is Drone_state.DELIVERED
    assert drone.current_zone is end
    assert drone.current_connection is None
    assert not connection.occupants
    assert end.reserved == 0


def test_full_zone_can_be_entered_when_occupant_leaves() -> None:
    a = zone("A")
    b = zone("B")
    end = zone("end", Zone_role.END)
    coordinator, drones = make_coordinator(
        [[a, b], [b, end]], [link(a, b), link(b, end)]
    )

    approved = coordinator.run()
    assert {m.drone.id for m in approved} == {1, 2}
    assert b.occupants == 1  # Planning must not change occupancy.


def test_competing_arrivals_only_one_wins() -> None:
    a = zone("A")
    c = zone("C")
    b = zone("B", capacity=1)
    coordinator, _ = make_coordinator(
        [[a, b], [c, b]], [link(a, b), link(c, b)]
    )

    approved = coordinator.run()
    assert len(approved) == 1
    assert approved[0].zone is b


def test_capacity_two_allows_two_arrivals() -> None:
    a = zone("A")
    c = zone("C")
    b = zone("B", capacity=2)
    coordinator, _ = make_coordinator(
        [[a, b], [c, b]], [link(a, b), link(c, b)]
    )

    approved = coordinator.run()
    assert {m.drone.id for m in approved} == {1, 2}


def test_connection_capacity_one_rejects_opposite_direction() -> None:
    a = zone("A")
    b = zone("B")
    shared = link(a, b, capacity=1)
    coordinator, _ = make_coordinator([[a, b], [b, a]], [shared])

    approved = coordinator.run()
    assert len(approved) <= 1


def test_three_drone_cycle_moves_together() -> None:
    a = zone("A")
    b = zone("B")
    c = zone("C")
    coordinator, _ = make_coordinator(
        [[a, b], [b, c], [c, a]],
        [link(a, b), link(b, c), link(c, a)],
    )

    approved = coordinator.run()
    assert {m.drone.id for m in approved} == {1, 2, 3}


def test_deadlock_returns_no_moves() -> None:
    a = zone("A")
    b = zone("B")
    coordinator, drones = make_coordinator(
        [[a, b]], [link(a, b)]
    )
    b.increase_capacity()  # Stationary occupant with no departure.

    approved = coordinator.run()
    assert approved == []
    assert drones[0].current_zone is a
    assert a.occupants == 1
    assert b.occupants == 1


def test_reserved_capacity_blocks_new_arrival() -> None:
    a = zone("A")
    b = zone("B", kind=Zone_type.RESTRICTED)
    coordinator, _ = make_coordinator([[a, b]], [link(a, b)])
    assert b.reserve_capacity()

    approved = coordinator.run()
    assert approved == []
    assert b.reserved == 1


def test_coordinator_does_not_move_drone() -> None:
    start = zone("start", Zone_role.START)
    end = zone("end", Zone_role.END)
    coordinator, drones = make_coordinator(
        [[start, end]], [link(start, end)]
    )

    approved = coordinator.run()
    assert len(approved) == 1
    assert drones[0].current_zone is start
    assert start.occupants == 1
    assert end.occupants == 0


def test_restricted_arrival_does_not_move_twice_same_turn(
    capsys: pytest.CaptureFixture[str]
) -> None:
    """A drone finishing restricted transit cannot leave again that turn."""
    start = zone("start", Zone_role.START)
    restricted = zone("r", kind=Zone_type.RESTRICTED)
    goal = zone("goal", Zone_role.END)
    engine = make_engine(
        [([start, restricted, goal], 1)],
        [link(start, restricted), link(restricted, goal)],
    )
    drone = engine.drones[0]
    route = engine.drone_routes[0]

    engine.run_turn()
    first_output = capsys.readouterr().out
    assert "D1-start-r" in first_output
    assert drone.state is Drone_state.IN_TRANSIT
    assert route.position == 0

    engine.run_turn()
    second_output = capsys.readouterr().out

    # Arrival consumes the drone's one action for this turn.
    assert "D1-r" in second_output
    assert "D1-goal" not in second_output
    assert second_output.count("D1-") == 1
    assert drone.current_zone is restricted
    assert drone.state is not Drone_state.DELIVERED
    assert route.position == 1
    assert restricted.occupants == 1
    assert restricted.reserved == 0

    engine.run_turn()
    third_output = capsys.readouterr().out
    assert "D1-goal" in third_output
    assert drone.state is Drone_state.DELIVERED
    assert engine.turn == 3
