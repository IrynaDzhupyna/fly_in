"""Independent checker for simulation output.

It only reads the map (through the Parser) and the printed output lines,
and replays them with its own bookkeeping. It shares no logic with the
Scheduler or the SimulationEngine, so it can catch their mistakes.

Rules checked (subject, chapter VII):
    - one line per turn, "D<ID>-<zone>" or "D<ID>-<connection>" tokens
      separated by single spaces;
    - a drone moves at most once per turn;
    - a drone only moves along an existing connection;
    - blocked zones are never entered;
    - a restricted zone takes two turns: first onto the connection,
      then the drone MUST arrive the next turn;
    - at the end of every turn no zone holds more than max_drones
      (start and end zones are unlimited);
    - no connection is used by more than max_link_capacity drones
      in the same turn;
    - at the end, every drone is in the end zone.
"""

import re
from dataclasses import dataclass, field

from connection import Connection
from parser import Parser
from zone import Zone_role, Zone_type


TOKEN = re.compile(r"D(\d+)-(.+)")


@dataclass
class Report:
    """Result of checking one simulation output."""

    turns: int
    problems: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """True when no rule was broken."""

        return not self.problems


def check_output(map_file: str, lines: list[str]) -> Report:
    """Replays the output lines on the map and lists every broken rule."""

    graph = Parser(file_name=map_file).parse()
    report = Report(turns=len(lines))

    links: dict[tuple[str, str], Connection] = {}
    for connection in graph.connections:
        links[(connection.zone_a.name, connection.zone_b.name)] = connection
        links[(connection.zone_b.name, connection.zone_a.name)] = connection
    by_name = {connection.name: connection for connection in graph.connections}

    position: dict[int, str] = {
        drone: graph.start.name for drone in range(1, graph.nb_drones + 1)
    }
    # drone -> (connection name, restricted destination, departure turn)
    in_flight: dict[int, tuple[str, str, int]] = {}

    for turn, line in enumerate(lines, 1):
        problems = report.problems

        if line != line.strip() or "  " in line:
            problems.append(f"turn {turn}: extra spaces in '{line}'")

        moved: set[int] = set()
        link_use: dict[str, int] = {}

        for token in line.split():
            match = TOKEN.fullmatch(token)
            if match is None:
                problems.append(f"turn {turn}: bad token '{token}'")
                continue

            drone, target = int(match.group(1)), match.group(2)

            if drone not in position:
                problems.append(f"turn {turn}: unknown drone D{drone}")
                continue
            if drone in moved:
                problems.append(f"turn {turn}: D{drone} moves twice")
            moved.add(drone)

            if drone in in_flight:
                _name, destination, _start = in_flight.pop(drone)
                if target != destination:
                    problems.append(
                        f"turn {turn}: D{drone} had to arrive in "
                        f"'{destination}', moved to '{target}'"
                    )
                position[drone] = destination
                continue

            here = position[drone]

            if target in by_name and target not in graph.zones:
                connection = by_name[target]
                ends = (connection.zone_a.name, connection.zone_b.name)
                if here not in ends:
                    problems.append(
                        f"turn {turn}: D{drone} in '{here}' cannot "
                        f"use connection '{target}'"
                    )
                    continue
                destination = ends[1] if ends[0] == here else ends[0]
                if graph.zones[destination].type is not Zone_type.RESTRICTED:
                    problems.append(
                        f"turn {turn}: D{drone} stops on connection "
                        f"'{target}' to a non-restricted zone"
                    )
                in_flight[drone] = (target, destination, turn)
                link_use[target] = link_use.get(target, 0) + 1
                continue

            if target not in graph.zones or (here, target) not in links:
                problems.append(
                    f"turn {turn}: D{drone} cannot go from "
                    f"'{here}' to '{target}'"
                )
                continue

            zone = graph.zones[target]
            if zone.type is Zone_type.BLOCKED:
                problems.append(f"turn {turn}: D{drone} entered blocked "
                                f"zone '{target}'")
            if zone.type is Zone_type.RESTRICTED:
                problems.append(f"turn {turn}: D{drone} entered restricted "
                                f"zone '{target}' in one turn")

            connection = links[(here, target)]
            link_use[connection.name] = link_use.get(connection.name, 0) + 1
            position[drone] = target

        for drone, (_name, destination, start) in in_flight.items():
            if start < turn:
                problems.append(f"turn {turn}: D{drone} waited on the "
                                f"connection to '{destination}'")

        for name, used in link_use.items():
            limit = by_name[name].max_link_capacity
            if used > limit:
                problems.append(f"turn {turn}: connection '{name}' used by "
                                f"{used} drones (max {limit})")

        inside: dict[str, int] = {}
        for drone, zone_name in position.items():
            if drone not in in_flight:
                inside[zone_name] = inside.get(zone_name, 0) + 1

        for zone_name, count in inside.items():
            zone = graph.zones[zone_name]
            if zone.role is Zone_role.HUB and count > zone.max_drones:
                problems.append(f"turn {turn}: zone '{zone_name}' holds "
                                f"{count} drones (max {zone.max_drones})")

    if in_flight or any(
        zone_name != graph.end.name for zone_name in position.values()
    ):
        report.problems.append("not every drone reached the end zone")

    return report
