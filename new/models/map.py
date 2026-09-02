from dataclasses import dataclass

@dataclass
class Map:
    """ Represents a map/graph object with its properties. """
    start_hub: Zone
    end_hub: Zone
    zones: list[Zone]
    connections: list[Connection]

    def __post_init__(self):
        """ Post-initialization to ensure zones and connections are valid. """
        if not self.zones:
            raise ValueError("Map must contain at least one zone.")
        if not self.connections:
            raise ValueError("Map must contain at least one connection.")
        if self.start_hub not in self.zones or self.end_hub not in self.zones:
            raise ValueError("Start and end hubs must be part of the zones list.")
        if self.start_hub == self.end_hub:
            raise ValueError("Start and end hubs must be different.")

    
    def add_zone(self, zone: Zone) -> None:
        """ Add a new zone to the map. """
        self.zones.append(zone)

    def add_connection(self, connection: Connection) -> None:
        """ Add a new connection to the map. """
        self.connections.append(connection)

    def neighbors(self, zone: Zone) -> list[Zone]:
    """Return zones directly connected to the given zone."""
        neighbors = []

        for connection in self.connections:
            if connection.start == zone:
                neighbors.append(connection.end)
            elif connection.end == zone:
                neighbors.append(connection.start)

        return neighbors