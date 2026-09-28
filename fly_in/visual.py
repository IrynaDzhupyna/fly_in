import arcade

from graph import Graph
from zone import Zone, Coordinates

WINDOW_TITLE="Fly-in"

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

MAP_MARGIN = 100


class Visualizer:
    """Initializes and connects all components needed for 
    graphical simulation, then starts the visualization."""

    def __init__(self, graph: Graph) -> None:

        self.graph = graph

    def run(self) -> None:
        """Activates the visualization"""

        graph_drawer = GraphDrawer(self.graph)
        drone_drawer = DroneDrawer()

        window = SimulationWindow(
            graph_drawer,
            drone_drawer
        )


class SimulationWindow(arcade.Window):
    """ Creates/manages the Arcade window"""

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self) -> None:
        """Calls another classes"""
        self.clear()

    def run(self) -> None:
        arcade.run()


class GraphDrawer:
    """Draws the static graph: connections and zones"""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

        (self.min_x, self.max_x,
        self.min_y, self.max_y) = self._calculate_graph_bounds()

        self.map_scale = self._calculate_graph_scale()

    def draw(self) -> None:
        """Draws the complete graph"""

        self._draw_connections()
        self._draw_zones()

    def _draw_connections(self) -> None:
        """Draws the connections"""

        for connection in self.graph.connections:
            zone_a = connection.zone_a
            zone_b = connection.zone_b

            x_a, y_a = self._to_screen_coordinates(zone_a.coordinates)
            x_b, y_b = self._to_screen_coordinates(zone_b.coordinates)
            pass


    def _draw_zones(self) -> None:
        """Draws zones: shape and name"""

        for zone in self.graph.zones.values():
            pass

    def _to_screen_coordinates(
            self,
            coordinates: Coordinates) -> tuple[float, float]:
        """Takes the coordinates from graph and transforms it to screen.
            SCALE:
                graph of size of 0...100
                must fit inside 1280 x 720
                
            TRANSLATE:
                graph should have margins / be positioned nicely
                instead of starting directly at screen (0, 0)"""

        graph_x = coordinates.x - self.min_x
        graph_y = coordinates.y - self.min_y

        # scale
        scaled_x = graph_x * self.map_scale
        scaled_y = graph_y * self.map_scale

        # translate away from edge of the window using margin

        screen_x = scaled_x + MAP_MARGIN
        screen_y = scaled_y + MAP_MARGIN


    def _calculate_graph_bounds(self) -> tuple[int, int, int, int]:
        """Calculates the min/max for X and Y of the graph"""

        max_x = max(zone.coordinates.x for zone in self.graph.zones.values())
        min_x = min(zone.coordinates.x for zone in self.graph.zones.values())

        max_y = max(zone.coordinates.y for zone in self.graph.zones.values())
        min_y = min(zone.coordinates.y for zone in self.graph.zones.values())

        return (min_x, max_x, min_y, max_y)

    def _calculate_graph_scale(self) -> float:
        """Calculates the scale for the graph so
        all the objects have space"""

        map_width = self.max_x - self.min_x
        map_height = self.max_y - self.min_y

        if map_width == 0 and map_height == 0:
            return 1.0

        usable_width = WINDOW_WIDTH - MAP_MARGIN * 2
        usable_height = WINDOW_HEIGHT - MAP_MARGIN * 2
        
        if map_width == 0:
            return usable_height / map_height

        if map_height == 0:
            return usable_width / map_width

        # how many pixels can 1 map unit occupy
        scale_x = usable_width / map_width
        scale_y = usable_height / map_height

        return min(scale_x, scale_y)

    


class DroneDrawer:
    """Draws the changing drone positions"""
    pass




def main():

    w = SimulationWindow()
    w.run()

if __name__ == "__main__":
    main()