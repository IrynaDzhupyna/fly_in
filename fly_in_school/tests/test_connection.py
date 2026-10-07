import pytest

from connection import Connection
from zone import Zone, Coordinates, Zone_type, Zone_role

def test_connection():
    zone_a = Zone(
        name="Zone_A",
        coordinates=Coordinates(x=0, y=0),
        role=Zone_role.START,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=1
    )

    zone_b = Zone(
        name="Zone_B",
        coordinates=Coordinates(x=0, y=1),
        role=Zone_role.START,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=1
    )

    connection = Connection(zone_a, zone_b)

    assert connection.zone_a == zone_a
    assert connection.zone_b == zone_b
    assert connection.occupants == []
    assert connection.max_link_capacity == 1
