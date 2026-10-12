
import pytest
import subprocess
from pathlib import Path


MAPS = Path("maps")
map_files = list(MAPS.glob("*.txt"))


@pytest.mark.parametrize("map_file", map_files)
def test_map(map_file):

    result = subprocess.run(
        ["poetry", "run", "python", "fly_in.py", str(map_file)],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0, result.stderr

    # Count lines containing drone movements
    turns = 0

    for line in result.stdout.splitlines():
        if line.startswith("D"):
            turns += 1

    print(f"\n{map_file.name}: {turns} turns")
