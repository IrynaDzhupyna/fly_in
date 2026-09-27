import arcade

from graph import Graph
from zone import Zone


WINDOW_TITLE = "Fly-in"

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

ZONE_RADIUS = 50
MAP_SCALE = 50
MAP_MARGIN = 100
CONNECTION_WIDTH = 2


class Window(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title, graph: Graph):
        """ Create the variables """

        # Init the parent class
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.NAVY_BLUE)
        self.graph = graph

    def on_draw(self):
        """ Draw everything """
        self.clear()

        # Draw connections
        for connection in self.graph.connections:
            self.draw_connection(connection)

        for zone in self.graph.zones.values():
            self.draw_zone(zone)


    def draw_connection(self, connection):
        """ Draw a connection between two zones """
        arcade.draw_line(
            connection.zone_a.coordinates.x,
            connection.zone_a.coordinates.y,
            connection.zone_b.coordinates.x,
            connection.zone_b.coordinates.y,
            arcade.color.BLACK,
            CONNECTION_WIDTH,
        )

    def draw_zone(self, zone):
        """ Draw a zone """
        screen_x, screen_y = self.to_screen_coordinates(zone)

        arcade.draw_circle_filled(
            screen_x,
            screen_y,
            ZONE_RADIUS,
            arcade.color.BLUE
        )

        arcade.draw_text(
            zone.name,
            screen_x + 10,
            screen_y + 10,
            arcade.color.WHITE
            )

    def to_screen_coordinates(self, zone: Zone) -> tuple[float, float]:
        """ Convert world coordinates to screen coordinates """
        screen_x = zone.coordinates.x * MAP_SCALE + MAP_MARGIN
        screen_y = zone.coordinates.y * MAP_SCALE + MAP_MARGIN
        return screen_x, screen_y

    def run(self):
        """ Run the arcade window """
        # self.on_draw()
        arcade.run()
