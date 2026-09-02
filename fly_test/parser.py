from pydantic import BaseModel

from zone import Zone, Zone_role, Zone_type, Coordinates
from connection import Connection
from graph import Graph


class ParserError(Exception):
    """Raised when map file is malformed"""
    pass

ZONE_ROLE_VALUES = {role.value for role in Zone_role}

# what real things are represented in this file: hub, connection, nb_drones
class Parser(BaseModel):

    file_name: str
    nb_drones: int
    zones: list[Zone]
    connections: list[Connection]

    def parser_engine(self):
        for line in self.read_the_file(self.file_name):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = line.split(": ", 1)
            if key == "nb_drones":
                self._parse_nb_drones(key, value)
            elif key == "connection":
                self._parse_connection(key, value)
            elif key in ZONE_ROLE_VALUES:
                self._parse_zone(key, value)
            else:
                raise ParserError(f"Unrecognized format: '{line}'")

    def _parse_nb_drones(self, key: str, value: str):
        try:
            converted = int(value.rstrip())
        except ValueError:
            raise ParserError(f"For '{key}': can not convert '{value}' to int")
        if converted < 1:
            raise ParserError(f"{key} must be a positive int, got '{value}'")
        else:
            self.nb_drones = converted


    def _parse_connection(self, key: str, value: str):
        pair, _, capacity_str = value.partition(" ")
        if "-" not in pair:
            raise ParserError(f"Invalid connection format: '{value}'")

        zone_a_name, zone_b_name = pair.split("-", 1)
        if not zone_a_name or not zone_b_name or "-" in zone_a_name or "-" in zone_b_name:
            raise ParserError("The connection syntax forbids dashes in zone names.")
        if zone_a_name == zone_b_name:
            raise ParserError("Connection can not link a zone to itself")

        zone_a = self._find_zone(zone_a_name)
        zone_b = self._find_zone(zone_b_name)

        connection = Connection(zone_a=zone_a, zone_b=zone_b)
        if capacity_str:
            try:
                connection.max_link_capacity = int(capacity_str)
            except ValueError:
                raise ParserError(f"Invalid max_link_capacity: '{capacity_str}'")

        self.connections.append(connection)

    def _find_zone(self, name: str) -> Zone:
        for zone in self.zones:
            if zone.name == name:
                return zone
        raise ParserError(f"Connection references unknown zone: '{name}'")


    def _parse_zone(self, key: str, value: str):
        parts = value.split(" ", 3)
        if len(parts) < 3:
            raise ParserError(f"Invalid zone format: '{value}'")

        name, x, y, *rest = parts
        try:
            coordinates = Coordinates(int(x), int(y))
        except ValueError:
            raise ParserError(f"Invalid coordinates for zone '{name}': '{x} {y}'")

        # parse color if present, could be not [0] but at any position
        
        color = self._parse_color(rest[0]) if rest else None

        self.zones.append(
            Zone(
                name=name,
                coordinates=coordinates,
                color=color,
                role=Zone_role(key),
            )
        )

    def parse_zone_v2(self, key: str, value:str) -> None:
        parts = value.split(" ", 3)
        if len(parts) < 3:
            raise ParserError(f"Invalid zone format: '{value}'")

        name, x, y, *rest = parts
        try:
            coordinates = Coordinates(int(x), int(y))
        except ValueError:
            raise ParserError(f"Invalid coordinates for zone '{name}': '{x} {y}'")
        
        # now we need to split the rest to get the color, type, max_droned if present
        if not rest[0].startswith("[") or not rest[-1].endswith("]"):
            raise ParserError(f"Invalid metadata format: '{rest}'")

        for element in rest:
            if element is "[" or element is "]":
                continue
            elif element.startswith("color="):
                color = self._parse_color(element)
            elif element.startswith("zone="):
                zone_type = self._parse_zone_type(element)
            elif element.startswith("max_drones="):
                max_drones = self._parse_max_drones(element)
            else:
                raise ParserError(f"Invalid metadata entry: '{element}'")
        
        self.zones.append(
            Zone(
                name=name,
                coordinates=coordinates,
                color=color[1] if color else None,
                type=zone_type[1] if zone_type else Zone_type.NORMAL,
                max_drones=int(max_drones[1]) if max_drones else 1,
                role=Zone_role(key),
            )
        )
    
    def _parse_color(self, metadata: str) -> str | None:
        metadata = metadata.strip()

        for pair in metadata[1:-1].split(","):
            if "=" not in pair:
                raise ParserError(f"Invalid metadata entry: '{pair}'")
            attr, attr_value = (part.strip() for part in pair.split("=", 1))
            if attr == "color":
                return attr_value

        return None

    def _parse_zone_type(self, metadata: str) -> Zone_type | None:
        metadata = metadata.strip()

        for pair in metadata[1:-1].split(","):
            if "=" not in pair:
                raise ParserError(f"Invalid metadata entry: '{pair}'")
            attr, attr_value = (part.strip() for part in pair.split("=", 1))
            if attr == "zone":
                try:
                    return Zone_type(attr_value)
                except ValueError:
                    raise ParserError(f"Invalid zone type: '{attr_value}'")

        return None

    def _parse_max_drones(self, metadata: str) -> int | None:
        metadata = metadata.strip()

        for pair in metadata[1:-1].split(","):
            if "=" not in pair:
                raise ParserError(f"Invalid metadata entry: '{pair}'")
            attr, attr_value = (part.strip() for part in pair.split("=", 1))
            if attr == "max_drones":
                try:
                    return int(attr_value)
                except ValueError:
                    raise ParserError(f"Invalid max_drones value: '{attr_value}'")

        return None

    
            
    # read the file and got content
    def read_the_file(self, file_name: str) -> list[str]:
        """ Reads the file and returns the contect as a list of str"""
        try:
            with open(file_name, "r") as file:
                return file.readlines()
        except OSError as err:
            raise ParserError(f"Could not open '{file_name}': {err}") from err

    # you got a content
    # now you need to go through each line and fill the objects:
    #   nb_drones: if it can be int
    #   zone: if it has name, coordinates meta_data if any
    #   connections: if zone_a-zone_b, max_link_capacity

    
