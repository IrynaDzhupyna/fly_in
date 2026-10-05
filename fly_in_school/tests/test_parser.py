import pytest

from parser import Parser, ParserError

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


# testing nb_drones
@pytest.mark.parametrize(
        "value", [
            "0",
            "-1"
            "abc",
            "1.5"
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

@pytest.mark.parametrize(
    "value", [
        
    ]
)
