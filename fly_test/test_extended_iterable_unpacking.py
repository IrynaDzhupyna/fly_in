from graph import Graph
from dataclasses import dataclass

@dataclass
class Parser:
    file_name: str
    nb_drones: int
    zones: list["Zone"]
    

file = "01_linear_path.txt"

with open (file, "r") as f:
    content = f.readlines()

for line in content:
    if line.startswith("#") or not line:
        continue
    else:
        if line.startswith("nb_drones"):
            nb_drones = int(line.split()[1])
        elif line.startswith("connection"):
            connection = self._parse_connection(line)


def _parse_connection(line: str) -> Connection | None:
    parts = line.split(" ", 3)
    if len(parts) < 3:
        raise ParserError(f"Invalid connection line: '{line}'")
    _, zone1_name, zone2_name, *rest = parts
    print(f"zone1_name: {zone1_name}, zone2_name: {zone2_name}, rest: {rest}")
