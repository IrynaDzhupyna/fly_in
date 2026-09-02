from dataclasses import dataclass
from zone import Zone
from connection import Connection


@dataclass
class Graph:
    """ All zones and links, plus start and end"""

    zones: dict[str, Zone]
    connections: list[Connection]
    start: Zone
    end: Zone

    def connections_for(self, zone_name: str) -> list[Connection]:
        return [
            connection
            for connection in self.connections
            if zone_name in (connection.zone_a.name, connection.zone_b.name)
        ]
