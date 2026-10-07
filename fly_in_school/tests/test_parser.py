import pytest

from parser import Parser, ParserError
from zone import Zone_type

@pytest.fixture
def map_file(tmp_path):
    return tmp_path / "map.txt"

def test_valid_minimal_map(map_file):

    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub: end 1 0
connection: start-end
"""
    )
    # act
    parser = Parser(file_name=str(map_file))
    graph = parser.parse()

    # assert
    assert graph.nb_drones == 2

    assert graph.start.name == "start"
    assert graph.start.coordinates.x == 0
    assert graph.start.coordinates.y == 0
    
    assert graph.end.name == "end"
    assert graph.end.coordinates.x == 1
    assert graph.end.coordinates.y == 0

    assert len(graph.connections) == 1
    
    connection = graph.connections[0]
    
    assert connection.zone_a.name == "start"
    assert connection.zone_b.name == "end"

# testing parser errors containing line and cause
def test_parser_error_contains_line_and_cause(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A abc 2
end_hub: end 1 0
"""
    )

    with pytest.raises(ParserError) as error:
        Parser(file_name=str(map_file)).parse()

    message = str(error.value)

    assert "Line 3" in message
    assert "Invalid coordinates" in message

# testing comments and empty lines are ignored
def test_comments_and_empty_lines_ignored(map_file):
    map_file.write_text(
        """# This is a comment


nb_drones: 2
start_hub: start 0 0
# Another comment
end_hub: end 1 0
connection: start-end
"""
    )
    parser = Parser(file_name=str(map_file))
    graph = parser.parse()
    assert graph.nb_drones == 2
    assert len(graph.zones) == 2
    assert len(graph.connections) == 1

# testing nb_drones
def test_nb_drones_first_line(map_file):
    map_file.write_text(
        """start_hub: start 0 0
nb_drones: 2
end_hub: end 1 0
connection: start-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

@pytest.mark.parametrize(
        "value", [
            "0",
            "-1",
            "abc",
            "1.5",
            ""
        ]
)

def test_invalid_nb_drones_raise_error(map_file, value):
    
    map_file.write_text(
        f"""nb_drones: {value}
start_hub: start 0 0
end_hub: end 0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_missing_nb_drones_raise_error(map_file):
    map_file.write_text(
        """start_hub: start 0 0
end_hub: end 0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_multiple_nb_drones_raise_error(map_file):
    map_file.write_text(
        """nb_drones: 2
nb_drones: 3
start_hub: start 0 0
end_hub: end 0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# testing start_hub
def test_start_missing(map_file):
    map_file.write_text(
        """nb_drones: 2
end_hub: end 0 1
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_start_multiple(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
start_hub: start2 1 1
end_hub: end 0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_start_empty_name(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub:  0 0
end_hub: end 0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

@pytest.mark.parametrize(
    "coordinates", [
        "a 0",
        "0 a",
        "0",
        "1.5 2",
        "2 1.5",
        "0 1 2",
        "a b",
        ""
    ]
)

def test_start_invalid_coordinates(map_file, coordinates):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start {coordinates}
end_hub: end 0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# testing end_hub
def test_end_missing(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_end_multiple(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub: end 0 1
end_hub: end2 1 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_end_empty_name(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub:  0 1
connection: start-end
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_start_end_same_name(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: hub 0 0
end_hub: hub 0 1
connection: hub-hub
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# testing hubs
def test_valid_hub(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )

    parser = Parser(file_name=str(map_file))
    graph = parser.parse()

    assert "A" in graph.zones
    A = graph.zones["A"]
    assert A.coordinates.x == 1
    assert A.coordinates.y == 0

# hub name with dash is invalid
def test_hub_name_with_dash(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A-B 1 0
end_hub: end 0 1
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# hub name with space is invalid
def test_hub_name_with_space(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A B 1 0
end_hub: end 0 1
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_hub_duplicate_name(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0
hub: A 2 0
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# testing hub metadata
def test_valid_hub_metadata(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0 [zone=restricted max_drones=2]
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )

    parser = Parser(file_name=str(map_file))
    graph = parser.parse()

    A = graph.zones["A"]

    assert A.type is Zone_type.RESTRICTED
    assert A.max_drones == 2

# default metadata
def test_hub_default_metadata(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 2 0
"""
    )

    graph = Parser(file_name=str(map_file)).parse()

    hub = graph.zones["A"]

    assert hub.type is Zone_type.NORMAL
    assert hub.color is None
    assert hub.max_drones == 1

# metadata syntax
@pytest.mark.parametrize(
    "metadata", [
        "[]",
        "[zone=]",
        "[zone]",
        "[=restricted]",
        "[zone=normal",
        "zone=normal]",
        "[zone=normal max_drones=]",
        "zone=normal max_drones]"
    ]
)

def test_invalid_hub_metadata(map_file, metadata):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0 {metadata}
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# metadata keys
def test_invalid_hub_metadata_unknown_field(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0 [unknown=normal]
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# metadata values for zone
@pytest.mark.parametrize(
    "zone, expected_type", [
        ("normal", Zone_type.NORMAL),
        ("blocked", Zone_type.BLOCKED),
        ("restricted", Zone_type.RESTRICTED),
        ("priority", Zone_type.PRIORITY)
    ]
)

def test_valid_hub_metadata_zone(map_file, zone, expected_type):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0 [zone={zone}]
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    assert Parser(file_name=str(map_file)).parse().zones["A"].type is expected_type

@pytest.mark.parametrize(
    "zone", [
        "abc",
        "NORMAL",
    ]
)
def test_invalid_hub_metadata_zone(map_file, zone):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0 [zone={zone}]
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

@pytest.mark.parametrize(
    "metadata", [
        "[zone=normal zone=restricted]",
        "[max_drones=2 max_drones=3]"
    ]
)

def test_invalid_hub_metadata_duplicate_field(map_file, metadata):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0 {metadata}
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# values max_drones
@pytest.mark.parametrize(
    "max_drones", [
        "abc",
        "-1",
        "0",
        "1.5"
    ]
)
def test_invalid_hub_metadata_max_drones(map_file, max_drones):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0 [zone=normal max_drones={max_drones}]
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# start end hubs ignore metadata[max_drones]
@pytest.mark.parametrize(
    "start_metadata, end_metadata", [
        ("[max_drones=5]", ""),
        ("", "[max_drones=5]"),
    ]
)
def test_start_end_max_drones_ignored(
        map_file,
        start_metadata,
        end_metadata
    ):

    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0 {start_metadata}
end_hub: end 0 1 {end_metadata}
connection: start-end
"""
    )

    graph = Parser(file_name=str(map_file)).parse()

    assert graph.start.max_drones == 1
    assert graph.end.max_drones == 1

def test_start_end_max_drones_invalid_ignored(
        map_file
    ):

    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0 [max_drones=abc]
end_hub: end 0 1 [max_drones=-1]
connection: start-end
"""
    )
    graph = Parser(file_name=str(map_file)).parse()
    assert graph.start.max_drones == 1
    assert graph.end.max_drones == 1

# testing connections
def test_connection_valid(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A
connection: A-end
"""
    )
    graph = Parser(file_name=str(map_file)).parse()

    assert len(graph.connections) == 2

    first = graph.connections[0]
    second = graph.connections[1]

    assert first.zone_a.name == "start"
    assert first.zone_b.name == "A"
    assert second.zone_a.name == "A"
    assert second.zone_b.name == "end"

# default connection
def test_connection_default_capacity(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub: end 1 0
connection: start-end
"""
    )

    graph = Parser(file_name=str(map_file)).parse()

    connection = graph.connections[0]

    assert connection.max_link_capacity == 1

# invalid connections format
@pytest.mark.parametrize(
    "connection", [
        "startA",
        "start-A-B",
        "start-",
        "-A"
    ]
)
def test_connection_invalid_format(map_file, connection):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
end_hub: end 0 1
connection: {connection}
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_connection_missing_zones(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub: end 0 1
connection:
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_connection_unknown_zone(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub: end 0 1
connection: start-unknown
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

@pytest.mark.parametrize(
    "connection", [
        "start-start",
        "end-end"
    ]
)
def test_connection_self_link(map_file, connection):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
end_hub: end 0 1
connection: {connection}
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

@pytest.mark.parametrize(
    "connection1, connection2", [
        ("start-A", "start-A"),
        ("start-A", "A-start"),
        ("A-end", "end-A")
    ]
)

def test_connection_duplicate(map_file, connection1, connection2):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: {connection1}
connection: {connection2}
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# undefined zones in connections
def test_connection_undefined_zone(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
end_hub: end 0 1
connection: start-A
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_connection_zone_defined_after_connection(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
connection: start-A
hub: A 1 0
end_hub: end 0 1
"""
    )

    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# connection with metadata
def test_connection_with_metadata(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A [max_link_capacity=2]
connection: A-end [max_link_capacity=3]
"""
    )
    graph = Parser(file_name=str(map_file)).parse()
    assert graph.connections[0].max_link_capacity == 2
    assert graph.connections[1].max_link_capacity == 3

# testing connection metadata invalid syntax
@pytest.mark.parametrize(
    "metadata", [
        "[]",
        "[max_link_capacity=]",
        "[max_link_capacity]",
        "[=2]"
    ]
)
def test_connection_with_invalid_metadata_syntax(map_file, metadata):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A {metadata}
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# testing connection metadata invalid keys
@pytest.mark.parametrize(
    "metadata", [
        "[unknown=2]",
        "[max_link_capacity=2 unknown=3]"
    ]
)

def test_connection_with_invalid_metadata_key(map_file, metadata):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A {metadata}
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

# testing connection metadata duplicate keys
def test_connection_with_invalid_metadata_duplicate_key(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A [max_link_capacity=2 max_link_capacity=3]
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

@pytest.mark.parametrize(
    "max_link_capacity", [
        "abc",
        "0",
        "-1",
        "1.5"
    ]
)

def test_connection_with_invalid_metadata(map_file, max_link_capacity):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0
end_hub: end 0 1
connection: start-A [max_link_capacity={max_link_capacity}]
connection: A-end
"""
    )
    with pytest.raises(ParserError):
        Parser(file_name=str(map_file)).parse()

def test_hub_color_metadata(map_file):
    map_file.write_text(
        """nb_drones: 2
start_hub: start 0 0
hub: A 1 0 [color=purple]
end_hub: end 2 0
"""
    )

    graph = Parser(file_name=str(map_file)).parse()

    hub = graph.zones["A"]

    assert hub.color == "purple"

@pytest.mark.parametrize(
    "metadata", [
        "[zone=restricted max_drones=2 color=purple]",
        "[zone=restricted color=purple max_drones=2]",
        "[max_drones=2 zone=restricted color=purple]",
        "[max_drones=2 color=purple zone=restricted]",
        "[color=purple zone=restricted max_drones=2]",
        "[color=purple max_drones=2 zone=restricted]",
    ]
)
def test_hub_metadata_order_independent(map_file, metadata):
    map_file.write_text(
        f"""nb_drones: 2
start_hub: start 0 0
hub: A 1 0 {metadata}
end_hub: end 2 0
"""
    )

    graph = Parser(file_name=str(map_file)).parse()

    hub = graph.zones["A"]

    assert hub.type is Zone_type.RESTRICTED
    assert hub.max_drones == 2
    assert hub.color == "purple"