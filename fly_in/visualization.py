import arcade

from graph import Graph


WINDOW_TITLE = "Fly-in"

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

ZONE_RADIUS = 50
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
        arcade.draw_circle_filled(
            zone.coordinates.x,
            zone.coordinates.y,
            ZONE_RADIUS,
            arcade.color.BLUE
        )

        arcade.draw_text(
            zone.name,
            zone.coordinates.x + 10,
            zone.coordinates.y + 10,
            arcade.color.WHITE
            )

    def to_screen_coordinates(self, zone: Zone):
        """ Convert world coordinates to screen coordinates """
        x = zone.coordinates.x * 

    
    def run(self):
        """ Run the arcade window """
        # self.on_draw()
        arcade.run()
