import sys
from pydantic import BaseModel, Field
from enum import Enum

from zone import Coordinates, Zone, Zone_role, Zone_type
from connection import Connection
from graph import Graph


# Mapping: A -> B
ZONE_PREFIXES = {
    "start_hub": Zone_role.START,
    "end_hub": Zone_role.END,
    "hub": Zone_role.HUB,
}

# Membership: is A allowed?
ZONE_METADATA = {
    "zone",
    "color",
    "max_drones",
}

CONNECTION_METADATA = {
    "max_link_capacity"
}


class ParserError(Exception):
    """ Raised when the input map file is malformed"""


class Parser(BaseModel):
    """ Reads a map file and builds the drone count and Graph from it"""
    file_name: str
    nb_drones: int | None = None
    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)

    def parse(self) -> Graph:
        """ Parses lines from map file sets nb_drones and returns Graph"""

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
        """ Opens map file and returns all lines as a list
            Raises ParserError if some problems occure"""
        try:
            with open(self.file_name, "r") as file:
                return file.readlines()
        except OSError as error:
            raise ParserError(f"Could not open '{self.file_name}': {error}") from error

    def _parse_line(self, line: str) -> None:
        """ Dispatch a line to the appropriate parser"""
        if ":" not in line:
            raise ParserError(f"Invalid line format: '{line}'")
        
        prefix = line.split(":", 1)[0].strip()

        if prefix == "nb_drones":
            self._parse_nb_drones(line)

        elif prefix == "connection":
            self._parse_connection(line)

        elif prefix in ZONE_PREFIXES:
            self._parse_zone(line)

        else:
            raise ParserError(f"Unrecognized line format: '{line}'")

    def _parse_nb_drones(self, line: str) -> None:
        """Parse the number of drones"""
        if self.nb_drones is not None:
            raise ParserError("'nb_drones' defined more than once")
        # nb_drones: 2
        # check with not int 
        _, value = line.split(":", 1)
        value = value.strip()

        if not value:
            raise ParserError(f"'nb_drones' cannot be empty")
        
        self.nb_drones = self._parse_positive_int(value, "nb_drones")

    def _parse_connection(self, line: str) -> None:
        """Parse a connection definition."""
        _, content = line.split(":", 1)

        tokens = content.strip().split()

        if not tokens:
            raise ParserError(f"Missing connection zones: '{line}'")

        zone_pair, *metadata_tokens = tokens

        parts = zone_pair.split("-")

        if len(parts) != 2:
            raise ParserError(
                f"Invalid connection format: '{zone_pair}'")

        zone_a_name, zone_b_name = parts

        if not zone_a_name or not zone_b_name:
            raise ParserError(
                f"Invalid connection format: '{zone_pair}'"
            )
        
        if zone_a_name == zone_b_name:
            raise ParserError(
                f"Connection cannot link a zone to itself: '{zone_pair}'")

        zone_a = self.zones.get(zone_a_name)
        zone_b = self.zones.get(zone_b_name)
        
        if zone_a is None or zone_b is None:
            raise ParserError(
                f"Connection references unknown zone(s): '{zone_pair}'")

        for connection in self.connections:
            existing_pair = {
                connection.zone_a.name,
                connection.zone_b.name,
            }

            if existing_pair == {
                zone_a_name,
                zone_b_name,
            }:
                raise ParserError(
                    f"Duplicate connection: '{zone_pair}'"
                )

        metadata = self._parse_metadata(
            metadata_tokens, allowed_keys=CONNECTION_METADATA)
        
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

    
    def _parse_zone(self, line: str) -> None:
        """Parse a zone definiton"""
        prefix, content = line.split(":", 1)
        tokens = content.strip().split(maxsplit=3)

        if len(tokens) < 3:
            raise ParserError("Usage: <zone_name> <x> <y>")
        
        name, x, y = tokens[:3]
        metadata_tockens = tokens[3:]

        if not name:
            raise ParserError("Zone name cannot be empty")
        if name in self.zones:
            raise ParserError(f"Duplicate zone name: '{line}'")

        try:
            coordinates = Coordinates(int(x), int(y))
        except ValueError as error:
            raise ParserError(f"Invalid coordinates: x='{x}', y='{y}'") from error

        metadata = self._parse_metadata(
            metadata_tockens, allowed_keys=ZONE_METADATA)

        self.zones[name] = Zone(
            name=name,
            coordinates=coordinates,
            role=ZONE_PREFIXES[prefix],
            type=self._parse_zone_type(metadata),
            color=metadata.get("color"),
            max_drones=self._parse_positive_int(
                metadata.get("max_drones", "1"), "max_drones"),
        )

    def _parse_metadata(
            self, tokens: list[str],
            allowed_keys: set[str]
            ) -> dict[str, str]:
        """Parse and validate metadata."""

        if not tokens:
            return {}

        if len(tokens) != 1:
            raise ParserError("Invalid metadata format")

        metadata = tokens[0]

        if not metadata.startswith("[") or not metadata.endswith("]"):
            raise ParserError(f"Invalid metadata format: '{metadata}'")
        # removing []
        metadata = metadata[1:-1].strip()

        if not metadata:
            raise ParserError(
                "Metadata cannot be empty"
            )

        result: dict[str, str] = {}

        for item in metadata.split(","):
            item = item.strip()

            if not item:
                raise ParserError(
                    "Invalid metadata: empty item"
                )

            key, separator, value = item.partition("=")

            if not separator:
                raise ParserError(
                    f"Invalid metadata: '{item}'"
                )

            key = key.strip()
            value = value.strip()

            if not key:
                raise ParserError(
                    f"Invalid metadata key: '{item}'"
                )

            if not value:
                raise ParserError(
                    f"Invalid metadata value for '{key}'"
                )

            if key not in allowed_keys:
                raise ParserError(
                    f"Unknown metadata key: '{key}'"
                )

            if key in result:
                raise ParserError(
                    f"Duplicate metadata key: '{key}'"
                )

            result[key] = value

        return result

    def _parse_zone_type(self, metadata: dict[str, str]) -> Zone_type:
        """Parse and validate the zone type."""

        value = metadata.get("zone", "normal")

        try:
            return Zone_type(value)
        except ValueError as error:
            raise ParserError(
                f"Invalid zone type: '{value}'"
            ) from error

    def _parse_positive_int(self, value: str, field_name: str) -> int:
        """Parse a positive integer from metadata."""
        try:
            number = int(value)
        except ValueError as error:
            raise ParserError(
                f"'{field_name}' must be an integer, got '{value}'"
            ) from error

        if number <= 0:
            raise ParserError(
                f"'{field_name}' must be greater than 0, got '{value}'"
            )

        return number

    def _build_graph(self) -> Graph:
        """Validate parsed data and build the Graph."""

        if self.nb_drones is None:
            raise ParserError("Missing nb_drones definition")
        
        if not self.zones:
            raise ParserError("No zones defined")

        starts = [
            zone
            for zone in self.zones.values()
            if zone.role is Zone_role.START
        ]

        ends = [
            zone
            for zone in self.zones.values()
            if zone.role is Zone_role.END
        ]

        if len(starts) != 1:
            raise ParserError(
                f"Expected exactly one start_hub, found {len(starts)}")
        if len(ends) != 1:
            raise ParserError(
                f"Expected exactly one end_hub, found {len(ends)}")

        return Graph(
            nb_drones=self.nb_drones,
            zones=self.zones,
            connections=self.connections,
            start=starts[0],
            end=ends[0],
        )


# def main() -> None:
#     if len(sys.argv) != 2:
#         print(f"Usage: {sys.argv[0]} <map_file>")
#         sys.exit(1)

#     parser = Parser()

#     try:
#         graph = parser.parse(sys.argv[1])
#     except ParserError as error:
#         print(f"Error: {error}", file=sys.stderr)
#         sys.exit(1)

#     print(f"Number of drones: {parser.nb_drones}")
#     print(f"Zones: {list(graph.zones.keys())}")
#     print(f"Start: {graph.start.name}")
#     print(f"End: {graph.end.name}")

#     print("Connections:")
#     for connection in graph.connections:
#         print(
#             f"  {connection.zone_a.name} <-> "
#             f"{connection.zone_b.name}"
#         )


# if __name__ == "__main__":
#     main()
