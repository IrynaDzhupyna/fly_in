import sys
from pydantic import BaseModel, Field

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


class Parser(BaseModel):
    """ Reads a map file and builds the drone count and Graph from it"""
    file_name: str
    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]

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

        return self.build_graph()

    def _read_lines(self) -> list[str]:
        """ Opens map file and returns all lines as a list
            Raises ParserError if some problems occure"""
        try:
            with open(self.file_name, "r") as file:
                return file.readlines()
        except OSError as error:
            raise ParserError(f"Could not open '{self.file_name}': {error}") from error

    def _parse_line(self, line: str) -> None:
        """ Redirects the lines to parse according to their prefix
            Raises ParserError is case of unallowed prefix"""
        prefix = line.split(":", 1)[0]
        if prefix == "nb_drones":
            self._parse_nb_drones(line)
        elif prefix == "connection":
            self._parse_connection(line)
        elif prefix in ZONE_PREFIXES:
            self._parse_zone(line)
        else:
            raise ParserError(f"Unrecognized line format: '{line}'")

    def _parse_nb_drones(self, line: str) -> None:
        """Parse the nb_drones line and adds value to nb_drone attribute"""
        if self.nb_drones is not None:
            raise ParserError("'nb_drones' defined more than once")
        # nb_drones: 2
        # check with not int 
        _, value = line.split(":")
        self.nb_drones = value.strip()

    def _parse_connection(self, line: str) -> None:
            prefix, content = line.split(":", 1)

            tokens = content.split()

            if not tokens:
                raise ParserError(f"Missing connection zones: '{line}'")

            zone_pair, *metadata_tokens = tokens
            if "-" not in zone_pair:
                raise ParserError(f"Invalid connection format: '{zone_pair}'")

            zone_a_name, zone_b_name = zone_pair.split("-", 1)
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

    
    def _parse_zone(self, line: str) -> None:
        prefix, content = line.split(":", 1)
        tokens = content.strip().split(maxsplit=3)

        if len(tokens) < 3:
            raise ParserError("Usage: <zone_name> <x> <y>")
        
        name, x, y = tokens[:3]
        metadata_tockens = tokens[3:]

        if name in self.zones:
            raise ParserError(f"Duplicate zone name: '{line}'")

        try:
            coordinates = Coordinates(int(x), int(y))
        except ValueError as error:
            raise ParserError(f"Invalid coordinates: x='{x}', y='{y}'") from error

        metadata = self._parse_metadata(metadata_tockens)

        self.zones[name] = Zone(
            name=name,
            coordinates=self._parse_coordinates(metadata),
            role=ZONE_PREFIXES[prefix],
            type=self._parse_zone_type(metadata),
            color=metadata.get("color"),
            max_drones=self._parse_positive_int(metadata.get("max_drones", "1"), "max_drones"),
        )

    def _parse_metadata(self, tokens: list[str]) -> dict[str, str]:
        if not tokens:
            return {}

        if len(tokens) != 1:
            raise ParserError("Invalid metadata format")

        metadata = tokens[0]

        if not metadata.startswith("[") or not metadata.endswith("]"):
            raise ParserError(f"Invalid metadata format: '{metadata}'")
        # removing []
        metadata = metadata[1:-1]

        result = {}

        for item in metadata.split(","):
            key, sep, value = item.strip().partition("=")

            if not sep:
                raise ParserError(f"Invalid metadata: '{item}'")

            result[key.strip()] = value.strip()

        return result


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
