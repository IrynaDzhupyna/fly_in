from dataclasses import dataclass
from zone import Zone
from connection import Connection


@dataclass
class Graph:
    """ Describes the network.
    All zones and links, plus start and end"""

    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    start: Zone
    end: Zone

    def connections_for(self, zone_name: str) -> list[Connection]:
        """ Returns links for a given zone name"""
        return [
            connection
            for connection in self.connections
            if zone_name in (connection.zone_a.name, connection.zone_b.name)
        ]

    # where i got another_end() from?
    def neighbors(self, zone: Zone) -> list[tuple[Zone, Connection]]:
        """ Returns a list of tuples (neighbor_zone, connection) for a given zone"""
        
        return [
            (connection.another_end(zone), connection)
            for connection in self.connections_for(zone.name)
        ]

    # remove when you don't need me
    def info(self) -> None:
        pass
        
