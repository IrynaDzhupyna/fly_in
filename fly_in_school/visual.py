import arcade
from dataclasses import dataclass, field

from graph import Graph
from zone import Zone, Coordinates
from simulation_engine import SimulationEngine
from drone import Drone

WINDOW_TITLE = "Fly-in"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

MAP_MARGIN = 100

ZONE_RADIUS = 50
COLOR_DEFAULT = arcade.color.YELLOW

TURN_DURATION = 1.0


class CoordinateTransformer:
    """Transforms coordinates from graph to screen"""

    def __init__(
            self, graph: Graph,
            window_width: int,
            window_height: int, map_margin: int) -> None:
        self.graph = graph
        self.window_width = window_width
        self.window_height = window_height
        self.map_margin = map_margin

        (
            self.min_x, self.max_x,
            self.min_y, self.max_y
            ) = self._calculate_graph_bounds()
        # nb of screen pixels representing 1 unit of distance
        # in the graph coordinates
        # how far is one zone/connection from another in pixels
        self.scale = self._calculate_graph_scale()

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

        graph_width = self.max_x - self.min_x
        graph_height = self.max_y - self.min_y

        if graph_width == 0 and graph_height == 0:
            return 1.0

        usable_width = self.window_width - self.map_margin * 2
        usable_height = self.window_height - self.map_margin * 2

        if graph_width == 0:
            return usable_height / graph_height

        if graph_height == 0:
            return usable_width / graph_width

        # how many pixels can 1 map unit occupy
        scale_x = usable_width / graph_width
        scale_y = usable_height / graph_height

        return min(scale_x, scale_y)

    def to_screen_coordinates(
            self,
            coordinates: Coordinates) -> tuple[float, float]:
        """Takes a zone coordinates from graph
        and transforms it to screen coordinates"""

        graph_x = coordinates.x - self.min_x
        graph_y = coordinates.y - self.min_y

        # scale
        scaled_x = graph_x * self.scale
        scaled_y = graph_y * self.scale

        # translate away from edge of the window using margin

        screen_x = scaled_x + self.map_margin
        screen_y = scaled_y + self.map_margin

        return (screen_x, screen_y)


class Visualizer:
    """Initializes and connects all components needed for
    graphical simulation, then starts the visualization."""

    def __init__(
        self,
        graph: Graph,
        engine: SimulationEngine
    ) -> None:

        self.graph = graph
        self.engine = engine

        self.screen_coordinates = CoordinateTransformer(
            self.graph, WINDOW_WIDTH, WINDOW_HEIGHT, MAP_MARGIN)

    def run(self) -> None:
        """Activates the visualization"""

        graph_drawer = GraphDrawer(
            self.graph,
            self.screen_coordinates
            )

        drone_drawer = DroneDrawer(
            self.engine.drones,
            self.screen_coordinates
            )

        window = SimulationWindow(
            graph_drawer,
            drone_drawer,
            self.engine
        )

        arcade.run()


class GraphDrawer:
    """Draws the static graph: connections and zones"""

    def __init__(
        self,
        graph: Graph,
        screen_coordinates: CoordinateTransformer
    ) -> None:
        """Initializes the graph drawer with the graph to be drawn"""

        self.graph = graph
        self.coord_transformer = screen_coordinates
        self.zone_labels = self._create_zone_labels()

    def draw(self) -> None:
        """Draws the complete graph"""

        self._draw_connections()
        self._draw_zones()
        # self._drone_counter()

    def _draw_connections(self) -> None:
        """Draws the connections"""

        for connection in self.graph.connections:
            zone_a = connection.zone_a
            zone_b = connection.zone_b

            x_a, y_a = self.coord_transformer.to_screen_coordinates(
                zone_a.coordinates
            )
            x_b, y_b = self.coord_transformer.to_screen_coordinates(
                zone_b.coordinates
            )

            arcade.draw_line(
                start_x=x_a,
                start_y=y_a,
                end_x=x_b,
                end_y=y_b,
                color=arcade.color.BLACK,
                line_width=2
            )

    def _draw_zones(self) -> None:
        """Draws zones: shape and name"""

        for zone in self.graph.zones.values():
            x, y = self.coord_transformer.to_screen_coordinates(
                zone.coordinates
                )

            arcade.draw_circle_filled(
                center_x=x,
                center_y=y,
                radius=ZONE_RADIUS,
                color=self._get_zone_color(zone)
            )

        for label in self.zone_labels:
            label.draw()

    def _get_zone_color(self, zone: Zone) -> arcade.types.Color:
        """Converst color-name string into Arcade color"""

        if zone.color is None:
            return COLOR_DEFAULT

        color = zone.color.upper()

        try:
            return getattr(arcade.color, color)
        except AttributeError:
            return COLOR_DEFAULT

    def _create_zone_labels(self) -> list[arcade.Text]:
        """Creates a lable for each zone in the graph"""

        zones_names: list[arcade.Text] = []

        label_marge = 10

        for zone in self.graph.zones.values():
            x, y = self.coord_transformer.to_screen_coordinates(
                zone.coordinates
            )
            dist_to_zone = y + ZONE_RADIUS + label_marge

            label = arcade.Text(
                text=zone.name,
                x=x,
                y=dist_to_zone,
                color=arcade.color.BLACK,
                font_size=16,
                font_name="Arial",
                anchor_x="center",
            )
            zones_names.append(label)

        return zones_names


@dataclass
class DroneVisual:
    """Creates and manages a drone's visual representation"""

    drone_id: int
    x: float
    y: float

    text: arcade.Text = field(init=False)

    def __post_init__(self) -> None:
        """Creates the drone 'text'"""

        self.text = self._create_text()

    # @property
    # def _x_move_left(self) -> float:
    #     """Modifies x coordinate so the label is left/midle of the drone"""

    #     return self.x - self.marge

    def _create_text(self) -> arcade.Text:
        """Draws ID of a drone"""

        font_size = 10

        return arcade.Text(
            text=f"D{self.drone_id}",
            x=self.x,
            y=self.y,
            color=arcade.color.BLACK,
            font_size=font_size,
            anchor_x="center",
            anchor_y="center"
        )

    def draw(self) -> None:
        """Draws the background and text."""

        arcade.draw_rect_filled(
            arcade.XYWH(
                self.x,
                self.y,
                32,
                20
            ),
            arcade.color.WHITE
        )

        self.text.draw()

    def update_position(self, x: float, y: float) -> None:
        """Updates the position when drone moves"""

        self.x = x
        self.y = y

        self.text.x = self.x
        self.text.y = self.y


class DroneDrawer:
    """Draws changing drone positions"""

    def __init__(
        self,
        drones: list[Drone],
        screen_coordinates: CoordinateTransformer
    ) -> None:

        self.drones = drones
        self.coord_transformer = screen_coordinates

        self.drone_visuals: dict[int, DroneVisual] = (
            self._create_drone_visuals()
        )

    def draw(self) -> None:
        """Draws drones according to their current zones."""

        drones_by_zone: dict[Zone, list[Drone]] = {}

        for drone in self.drones:
            if drone.current_zone not in drones_by_zone:
                drones_by_zone[drone.current_zone] = []

            drones_by_zone[drone.current_zone].append(drone)

        for zone, drones in drones_by_zone.items():
            x, y = self.coord_transformer.to_screen_coordinates(
                zone.coordinates
                )
            arcade.draw_text(
                text=str(len(drones)),
                x=x + 40,
                y=y + 40,
                color=arcade.color.BLACK,
                font_size=14
            )
            if len(drones) <= 5:
                visible_drones = drones
            else:
                visible_drones = [
                    # drones[0],
                    # drones[4],
                    # drones[9],
                    drones[-1]
                ]

            for index, drone in enumerate(visible_drones):
                self._draw_drone(drone, index)

    def _draw_drone(self, drone: Drone, index: int) -> None:
        """Draws one drone"""

        x, y = self.coord_transformer.to_screen_coordinates(
            drone.current_zone.coordinates)

        columns = 3
        x_spacing = 35
        y_spacing = 25

        column = index % columns
        row = index // columns

        x += (column - 1) * x_spacing
        y -= row * y_spacing

        visual = self.drone_visuals[drone.id]
        visual.update_position(x, y)

        visual.draw()

    def _create_drone_visuals(self) -> dict[int, DroneVisual]:
        """ Creates a lable for each drone"""

        drone_visuals: dict[int, DroneVisual] = {}

        for drone in self.drones:
            x, y = self.coord_transformer.to_screen_coordinates(
                drone.current_zone.coordinates
            )

            visual = DroneVisual(
                drone_id=drone.id,
                x=x,
                y=y
            )

            drone_visuals[drone.id] = visual

        return drone_visuals


class SimulationWindow(arcade.Window):
    """Creates/manages the Arcade window"""

    def __init__(
        self,
        graph_drawer: GraphDrawer,
        drone_drawer: DroneDrawer,
        engine: SimulationEngine
    ) -> None:
        self.graph_drawer = graph_drawer
        self.drone_drawer = drone_drawer
        self.engine = engine
        self.time_since_last_turn = 0.0
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_update(self, delta_time: float) -> None:
        """Advance the simulation according to elapsed time"""

        self.time_since_last_turn += delta_time

        # if (
        #     not self.engine.is_finished
        #     and self.time_since_last_turn >= TURN_DURATION
        #     ):
        #     self.engine.run_turn()
        # self.time_since_last_turn = 0.0

    def on_key_press(self, key: int, key_modifier: int) -> None:
        """Make a turn if space pressed"""

        if key == arcade.key.SPACE:
            if not self.engine.is_finished:
                self.engine.run_turn()

    def on_draw(self) -> None:
        """Calls all classes needed for visualization"""

        self.clear()
        self.graph_drawer.draw()
        self.drone_drawer.draw()
