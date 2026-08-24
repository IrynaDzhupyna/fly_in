from dataclasses import dataclass
from zone import Zone
from connection import Connection
# from drone import Drone


@dataclass
class Graph:
    """Set of edges and a set of nodes
    Simple graph - has no loops or mltiple ages
    Multi graph - has mltiple edges between the nodes"""
    start: Zone
    end: Zone
    zones: list[Zone]
    connections: list[Connection]