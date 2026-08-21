import sys

from zone import Coordinates, Zone, Zone_role, Zone_type
from connection import Connection
from graph import Graph

ZONE_PREFIXES = {
    "start_hub": Zone_role.START,
    "end_hub": Zone_role.END,
    "hub": Zone_role.HUB,
}


class ParserError(Exception):
    """ Raised when the input map file is malformed"""


class Parser:
    """ Reads a map file and builds the drone count and Graph from it"""

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.nb_drones: int | None = None
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    def parse(self) -> Graph:
        for line_number, raw_line in enumerate(self._read_lines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                self._parse_line(line)
            except ParserError as error:
                raise ParserError(f"Line {line_number}: {error}") from error

        return self._build_graph()

    def _read_lines(self) -> list[str]:
        try:
            with open(self.file_name, "r") as file:
                return file.readlines()
        except OSError as error:
            raise ParserError(f"Could not open '{self.file_name}': {error}") from error

    def _parse_line(self, line: str) -> None:
        prefix = line.split(":", 1)[0]
        if prefix == "nb_drones":
            self._parse_nb_drones(line)
        elif prefix == "connection":
            self._parse_connection(line)
        elif prefix in ZONE_PREFIXES:
            self._parse_zone(prefix, line)
        else:
            raise ParserError(f"Unrecognized line format: '{line}'")

    def _parse_nb_drones(self, line: str) -> None:
        if self.nb_drones is not None:
            raise ParserError("nb_drones defined more than once")
        _, _, value = line.partition(":")
        self.nb_drones = self._parse_positive_int(value.strip(), "nb_drones")

    def _parse_zone(self, prefix: str, line: str) -> None:
        _, _, rest = line.partition(":")
        tokens = rest.split()
        if not tokens:
            raise ParserError(f"Missing zone name: '{line}'")

        name, *metadata_tokens = tokens
        if name in self.zones:
            raise ParserError(f"Duplicate zone name: '{name}'")
        metadata = self._parse_metadata(metadata_tokens)

        self.zones[name] = Zone(
            name=name,
            coordinates=self._parse_coordinates(metadata),
            role=ZONE_PREFIXES[prefix],
            type=self._parse_zone_type(metadata),
            color=metadata.get("color"),
            max_drones=self._parse_positive_int(metadata.get("max_drones", "1"), "max_drones"),
        )

    def _parse_connection(self, line: str) -> None:
        _, _, rest = line.partition(":")
        tokens = rest.split()
        if not tokens:
            raise ParserError(f"Missing connection zones: '{line}'")

        zone_pair, *metadata_tokens = tokens
        if "-" not in zone_pair:
            raise ParserError(f"Invalid connection format: '{zone_pair}'")

        zone_a_name, _, zone_b_name = zone_pair.partition("-")
        if zone_a_name == zone_b_name:
            raise ParserError(f"Connection cannot link a zone to itself: '{zone_pair}'")

        zone_a = self.zones.get(zone_a_name)
        zone_b = self.zones.get(zone_b_name)
        if zone_a is None or zone_b is None:
            raise ParserError(f"Connection references unknown zone(s): '{zone_pair}'")

        for connection in self.connections:
            if {connection.zone_a.name, connection.zone_b.name} == {zone_a_name, zone_b_name}:
                raise ParserError(f"Duplicate connection: '{zone_pair}'")

        metadata = self._parse_metadata(metadata_tokens)
        max_link_capacity = self._parse_positive_int(
            metadata.get("max_link_capacity", "1"), "max_link_capacity"
        )

        self.connections.append(
            Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                occupants=[],
                max_link_capacity=max_link_capacity,
            )
        )
        zone_a.connections.append(zone_b_name)
        zone_b.connections.append(zone_a_name)

    def _parse_metadata(self, tokens: list[str]) -> dict[str, str]:
        metadata = {}
        for token in tokens:
            key, sep, value = token.partition("=")
            if not sep:
                raise ParserError(f"Invalid metadata token: '{token}'")
            metadata[key] = value
        return metadata

    def _parse_coordinates(self, metadata: dict[str, str]) -> Coordinates:
        try:
            x = int(metadata.get("x", 0))
            y = int(metadata.get("y", 0))
        except ValueError:
            raise ParserError(f"Invalid coordinates: x='{metadata.get('x')}' y='{metadata.get('y')}'")
        return Coordinates(x, y)

    def _parse_zone_type(self, metadata: dict[str, str]) -> Zone_type:
        value = metadata.get("zone", Zone_type.NORMAL.value)
        try:
            return Zone_type(value)
        except ValueError:
            valid = ", ".join(zone_type.value for zone_type in Zone_type)
            raise ParserError(f"Invalid zone type '{value}' (expected one of: {valid})")

    def _parse_positive_int(self, value: str, label: str) -> int:
        try:
            parsed = int(value)
        except ValueError:
            raise ParserError(f"Invalid {label}: '{value}'")
        if parsed <= 0:
            raise ParserError(f"{label} must be a positive integer, got {parsed}")
        return parsed

    def _build_graph(self) -> Graph:
        if self.nb_drones is None:
            raise ParserError("Missing nb_drones definition")
        if not self.zones:
            raise ParserError("No zones defined")

        starts = [zone for zone in self.zones.values() if zone.role is Zone_role.START]
        ends = [zone for zone in self.zones.values() if zone.role is Zone_role.END]
        if len(starts) != 1:
            raise ParserError(f"Expected exactly one start_hub, found {len(starts)}")
        if len(ends) != 1:
            raise ParserError(f"Expected exactly one end_hub, found {len(ends)}")

        return Graph(
            zones=self.zones,
            connections=self.connections,
            start=starts[0],
            end=ends[0],
        )


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: parser.py <map_file>")
        return

    parser = Parser(sys.argv[1])
    try:
        graph = parser.parse()
    except ParserError as error:
        print(f"Error: {error}")
        return

    print(f"nb_drones: {parser.nb_drones}")
    print(f"zones: {list(graph.zones)}")
    print(f"start: {graph.start.name}, end: {graph.end.name}")
    print(f"connections: {[(c.zone_a.name, c.zone_b.name) for c in graph.connections]}")


if __name__ == "__main__":
    main()
