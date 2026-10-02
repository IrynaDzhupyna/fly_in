from parser import Parser


def test_valid_minimal_map(tmp_path):
    # arrange
    map_file = tmp_path / "map.txt"

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


