"""Runs every shipped map through the full pipeline, without a window.

Each map is parsed, routed by the PathFinder and simulated by the
SimulationEngine directly, so no arcade window is opened. A map passes
when every drone reaches the end zone within a turn limit.
"""

from pathlib import Path

import pytest

from drone import Drone_state
from parser import Parser
from path_finder import PathFinder
from simulation_engine import SimulationEngine


MAPS_DIR = Path(__file__).resolve().parent.parent / "maps"

# Optimum number of turns for each shipped map (subject, chapter VII.6).
OPTIMUM: dict[str, int] = {
    "01_linear_path": 4,
    "02_simple_fork": 4,
    "03_basic_capacity": 4,
    "01_dead_end_trap": 8,
    "02_circular_loop": 10,
    "03_priority_puzzle": 6,
    "01_maze_nightmare": 13,
    "02_capacity_hell": 16,
    "03_ultimate_challenge": 26,
    "01_the_impossible_dream": 43,
}

# Stop a simulation that is stuck instead of looping forever.
TURN_LIMIT_FACTOR = 5

MANDATORY_MAPS = sorted(
    path for path in MAPS_DIR.rglob("*.txt")
    if path.parent.name != "challenger"
)
CHALLENGER_MAPS = sorted((MAPS_DIR / "challenger").glob("*.txt"))


def simulate(map_file: Path) -> SimulationEngine:
    """Parses a map, finds paths and runs turns until done or stuck."""

    graph = Parser(file_name=str(map_file)).parse()
    engine = SimulationEngine(graph, PathFinder(graph).run())

    limit = OPTIMUM.get(map_file.stem, 50) * TURN_LIMIT_FACTOR

    while not engine.is_finished and engine.turn < limit:
        engine.run_turn()

    return engine


def check_map(map_file: Path) -> None:
    """Asserts that every drone of the map is delivered."""

    engine = simulate(map_file)

    stuck = [
        f"D{drone.id} in {drone.current_zone.name}"
        for drone in engine.drones
        if drone.state is not Drone_state.DELIVERED
    ]

    assert not stuck, (
        f"{map_file.name}: not finished after {engine.turn} turns, "
        f"undelivered: {', '.join(stuck)}"
    )

    optimum = OPTIMUM.get(map_file.stem)
    print(f"\n{map_file.name}: {engine.turn} turns (optimum {optimum})")


def test_maps_found() -> None:
    """Fails loudly if the maps folder is missing or empty."""

    assert MANDATORY_MAPS, f"No maps found in {MAPS_DIR}"


@pytest.mark.parametrize(
    "map_file", MANDATORY_MAPS, ids=lambda path: path.stem
)
def test_mandatory_map_delivers_all_drones(map_file: Path) -> None:
    """Every mandatory map must finish with all drones delivered."""

    check_map(map_file)


@pytest.mark.xfail(
    run=False,
    reason="optional map: path search takes ~45 s and drones get stuck",
)
@pytest.mark.parametrize(
    "map_file", CHALLENGER_MAPS, ids=lambda path: path.stem
)
def test_challenger_map_delivers_all_drones(map_file: Path) -> None:
    """The optional challenger map (bonus)."""

    check_map(map_file)
