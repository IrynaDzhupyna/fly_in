from pydantic import BaseModel

from zone import Zone, Zone_role
from connection import Connection
from graph import Graph


class ParserError(Exception):
    """Raised when map file is malformed"""
    pass

# what real things are represented in this file: hub, connection, nb_drones
class Parser(BaseModel):

    file_name: str
    nb_drones: int
    zones: list[Zone]
    connections: list[Connection]

    def parser_engine(self):
        for line in self.read_the_file(self.file_name):
            if line.startswith("#") or line is None:
                continue

            key, value = line.split(": ", 1)
            if key == "nb_drones":
                self._parse_nb_drones(key, value)
            elif key == "connection":
                self._parse_connection(key, value)
            elif key in Zone.Zone_role:
                self._parse_zone(key, value)
            else:
                raise ParserError(f"Unrecognized format: '{line}'")

    def _parse_nb_drones(self, key: str, value: str):
        try:
            converted = int(value.rstrip())
        except ValueError:
            raise ParserError("For '{key}': can not convert '{value}' to int")
        if converted < 1:
            raise ParserError(f"{key} must be a positive int, got '{value}'")
        else:
            self.nb_drones = converted


    def _parse_connection(self, key: str, value: str):
        if value is None:
            raise ParserError(f"Missing connecion zones: {key}")
        elif "-" not in value:
            raise ParserError(f"Invalid connection ormat: '{value}'")
        
        zone_a, zone_b = value.split("-")
        if zone_a is None or zone_b is None:
            raise ParserError(f"Connection references unknown zone(s): '{value}'")
        
        if zone_a == zone_b:
            raise ParserError(f"Connection can not lint its zone to itself")
        if "-" in zone_a or "-" in zone_b:
            raise ParserError("The connection syntax forbids dashes in zone names.")
        
        

    def _parse_zone(self, key: str, value: str):
        name, x, y, rest = value.split(" ", 4)

        if key is Zone_role.START:
            Zone.name = name
            Zone.coordinates = x, y
            



    
            
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

    
