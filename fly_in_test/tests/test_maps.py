"""Runs every shipped map through the whole program, without a window.

For each map: Parser -> PathFinder -> Scheduler -> SimulationEngine.
The printed output is checked by the independent rule checker in
output_rules.py, and the number of turns is compared to the subject's
optimum (chapter VII.6).
"""

import contextlib
import io
from pathlib import Path

import pytest

from fly_in import run_simulation
from output_rules import check_output


MAPS_DIR = Path(__file__).resolve().parent.parent / "maps"
CUSTOM_DIR = Path(__file__).resolve().parent.parent / "custom_maps"

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

SHIPPED_MAPS = sorted(MAPS_DIR.rglob("*.txt"))
VALID_CUSTOM_MAPS = sorted(
    path for path in CUSTOM_DIR.glob("*.txt")
    if not path.name.startswith("error_")
)
ERROR_MAPS = sorted(CUSTOM_DIR.glob("error_*.txt"))


def simulate(map_file: Path) -> tuple[bool, list[str]]:
    """Runs the simulation and returns (success, printed lines)."""

    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        success = run_simulation(str(map_file))

    lines = [line for line in output.getvalue().split("\n") if line]
    return success, lines


def test_maps_found() -> None:
    """Fails loudly if the maps folder is missing or empty."""

    assert len(SHIPPED_MAPS) == len(OPTIMUM), f"maps missing in {MAPS_DIR}"


@pytest.mark.parametrize("map_file", SHIPPED_MAPS, ids=lambda p: p.stem)
def test_shipped_map_is_valid_and_optimal(map_file: Path) -> None:
    """Every rule respected, and exactly the optimal number of turns."""

    success, lines = simulate(map_file)
    assert success, lines

    report = check_output(str(map_file), lines)
    assert report.valid, report.problems[:5]

    print(f"\n{map_file.name}: {report.turns} turns "
          f"(optimum {OPTIMUM[map_file.stem]})")
    assert report.turns == OPTIMUM[map_file.stem]


@pytest.mark.parametrize("map_file", VALID_CUSTOM_MAPS, ids=lambda p: p.stem)
def test_custom_map_is_valid(map_file: Path) -> None:
    """Our own edge-case maps run and respect every rule."""

    success, lines = simulate(map_file)
    assert success, lines

    report = check_output(str(map_file), lines)
    assert report.valid, report.problems[:5]


@pytest.mark.parametrize("map_file", ERROR_MAPS, ids=lambda p: p.stem)
def test_error_map_prints_clear_error(map_file: Path) -> None:
    """Broken maps stop with one clear 'Error:' line, never a crash."""

    success, lines = simulate(map_file)

    assert not success
    assert len(lines) == 1
    assert lines[0].startswith("Error:")
