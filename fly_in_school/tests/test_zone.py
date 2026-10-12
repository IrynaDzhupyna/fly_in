import pytest

from zone import Zone, Coordinates, Zone_role, Zone_type


@pytest.fixture
def zone() -> Zone:
    return Zone(
        name="Test Zone",
        coordinates=Coordinates(x=0, y=0),
        role=Zone_role.HUB,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=2
    )


def test_zone_default(zone: Zone) -> None:
    assert zone.name == "Test Zone"

    assert zone.coordinates.x == 0
    assert zone.coordinates.y == 0

    assert zone.role == Zone_role.HUB

    assert zone.type == Zone_type.NORMAL

    assert zone.color == "blue"

    assert zone.max_drones == 2

    assert zone.occupants == 0
    assert zone.connections == []


@pytest.mark.parametrize(
    "zone_type, cost", [
        (Zone_type.NORMAL, 1),
        (Zone_type.BLOCKED, 1),
        (Zone_type.RESTRICTED, 2),
        (Zone_type.PRIORITY, 1)
    ]
)
def test_movement_cost(zone_type: Zone_type, cost: int) -> None:
    zone = Zone(
        name="Test Cost",
        coordinates=Coordinates(x=0, y=0),
        role=Zone_role.HUB,
        type=zone_type,
        color="blue",
        max_drones=1
    )

    assert zone.type.movement_cost == cost


def test_has_capacity_when_empty(zone: Zone) -> None:

    assert zone.has_capacity() is True


def test_has_capacity_full(zone: Zone) -> None:
    zone.occupants = 2
    assert zone.has_capacity() is False


@pytest.mark.parametrize(
    "zone_type, expected", [
        (Zone_type.NORMAL, True),
        (Zone_type.BLOCKED, False),
        (Zone_type.RESTRICTED, True),
        (Zone_type.PRIORITY, True)
    ]
)
def test_has_capapacity_blocked(zone_type: Zone_type, expected: bool) -> None:
    zone = Zone(
        name="Test Zone",
        coordinates=Coordinates(x=0, y=0),
        role=Zone_role.HUB,
        type=zone_type,
        color="blue",
        max_drones=1
    )

    assert zone.has_capacity() == expected


@pytest.mark.parametrize(
    "zone_role", [
        Zone_role.START,
        Zone_role.END
    ]
)
def test_start_end_always_has_capacity(zone_role: Zone_role) -> None:
    zone = Zone(
        name="Test Zone",
        coordinates=Coordinates(x=0, y=0),
        role=zone_role,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=1
    )
    zone.max_drones = 1
    zone.occupants = 10

    assert zone.has_capacity() is True

# increase capacity


def test_increase_capacity(zone: Zone) -> None:
    result = zone.increase_capacity()

    assert zone.occupants == 1
    assert result is True


def test_increase_capacity_blocked() -> None:
    zone = Zone(
        name="Test Zone",
        coordinates=Coordinates(x=0, y=0),
        role=Zone_role.HUB,
        type=Zone_type.BLOCKED,
        color="blue",
        max_drones=1
    )

    result = zone.increase_capacity()

    assert zone.occupants == 0
    assert result is False


def test_increase_capacity_full(zone: Zone) -> None:
    zone.occupants = 2
    result = zone.increase_capacity()

    assert zone.occupants == 2
    assert result is False


@pytest.mark.parametrize(
    "zone_role", [
        Zone_role.START,
        Zone_role.END
    ]
)
def test_increase_capacity_start_end(zone_role: Zone_role) -> None:
    zone = Zone(
        name="Test Zone",
        coordinates=Coordinates(x=0, y=0),
        role=zone_role,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=1
    )
    zone.occupants = 11

    result = zone.increase_capacity()

    assert zone.occupants == 12
    assert result is True

# decrease_capacity should we test do we use it


def test_decrease_capacity() -> None:
    pass

# zone has connection


def test_two_zones_independent_connections() -> None:
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

    zone_a.connections.append(zone_b.name)
    zone_b.connections.append(zone_a.name)

    zone_a.connections.remove(zone_b.name)

    assert zone_a.connections == []
    assert zone_b.connections == [zone_a.name]


def test_two_zones_same_name_same_hash() -> None:

    zone_a = Zone(
        name="Zone_A",
        coordinates=Coordinates(x=0, y=0),
        role=Zone_role.START,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=1
    )

    zone_b = Zone(
        name="Zone_A",
        coordinates=Coordinates(x=1, y=0),
        role=Zone_role.START,
        type=Zone_type.NORMAL,
        color="blue",
        max_drones=1
    )

    assert hash(zone_a) == hash(zone_b)
