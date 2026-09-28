import arcade

from graph import Graph
from zone import Zone


WINDOW_TITLE = "Fly-in"

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

ZONE_RADIUS = 50

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

        self.min_x, self.max_x, self.min_y, self.max_y = self.calculate_map_bounds()

        self.map_scale = self.calculate_map_scale()

    def on_draw(self):
        """ Draw everything """

        self.clear()

        # Draw connections
        for connection in self.graph.connections:
            self.draw_connection(connection)

        # Draw zone
        for zone in self.graph.zones.values():
            self.draw_zone(zone)


    def draw_connection(self, connection):
        """ Draw a connection between two zones """

        start_x, start_y = self.scale_zone_coordinates(connection.zone_a)
        end_x, end_y = self.scale_zone_coordinates(connection.zone_b)

        arcade.draw_line(
            start_x,
            start_y,
            end_x,
            end_y,
            arcade.color.BLACK,
            CONNECTION_WIDTH,
        )

    def draw_zone(self, zone):
        """ Draw a zone """
        screen_x, screen_y = self.scale_zone_coordinates(zone)

        arcade.draw_circle_filled(
            screen_x,
            screen_y,
            ZONE_RADIUS,
            arcade.color.BLUE
        )

        # change hardcoded part to calculated
        arcade.draw_text(
            zone.name,
            screen_x + 30,
            screen_y + 30,
            arcade.color.WHITE
            )

    def calculate_map_scale(self) -> float:
        """Calculates the scale for the map so all objects have space"""
        
        # easy map - devision by zero

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

    def translate_zone_coordinates(self, zone: Zone) -> tuple[int, int]:
        """Moves zone coordinates to window start."""

        translated_x = zone.coordinates.x - self.min_x
        translated_y = zone.coordinates.y - self.min_y

        return (translated_x, translated_y)

    def scale_zone_coordinates(self) -> tuple[float, float]:
        """"Scale zone coordinates from map units to pixels."""

        screen_x = zone.coordinates.x * self.map_scale
        screen_y = zone.coordinates.y * self.map_scale

        return screen_x, screen_y

    
    def calculate_map_bounds(self) -> tuple[int, int, int, int]:
        """Finds min/max X and Y"""

        min_x = min(zone.coordinates.x for zone in self.graph.zones.values())
        max_x = max(zone.coordinates.x for zone in self.graph.zones.values())

        min_y = min(zone.coordinates.y for zone in self.graph.zones.values())
        max_y = max(zone.coordinates.y for zone in self.graph.zones.values())

        return (min_x, max_x, min_y, max_y)

    def run(self):
        """ Run the arcade window """
        # self.on_draw()
        arcade.run()


# scaling
# translation
