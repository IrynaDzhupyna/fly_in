import arcade
import pyglet
from dataclasses import dataclass, field

from graph import Graph
from zone import Zone, Coordinates
from simulation_engine import SimulationEngine
from drone import Drone, Drone_state

WINDOW_TITLE = "Fly-in"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

MAP_MARGIN = 100

ZONE_RADIUS = 50
MIN_ZONE_RADIUS = 10
COLOR_DEFAULT = arcade.color.YELLOW

TURN_DURATION = 1.0

KEY_HINTS = "SPACE play/pause   RIGHT next turn   ESC close"


class CoordinateTransformer:
    """Transforms coordinates from graph to screen.

    X and Y get their own scale, so a long, flat map (like the challenger,
    23 units wide and 4 high) uses the whole window instead of a thin
    strip. Zone circles and labels shrink when zones are close together.
    """

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

        self.scale_x, self.scale_y = self._calculate_graph_scale()

    @property
    def zone_radius(self) -> float:
        """Circle radius: at most ZONE_RADIUS, and small enough that
        neighbouring zones (one map unit apart) do not overlap."""

        spacing = min(self.scale_x, self.scale_y)
        return max(MIN_ZONE_RADIUS, min(ZONE_RADIUS, spacing * 0.35))

    @property
    def crowded(self) -> bool:
        """True when zones are too close for full-size circles."""

        return self.zone_radius < ZONE_RADIUS

    @property
    def label_font_size(self) -> int:
        """Zone name font size, smaller when zones are close together."""

        return 16 if not self.crowded else 9

    def _calculate_graph_bounds(self) -> tuple[int, int, int, int]:
        """Calculates the min/max for X and Y of the graph"""

        max_x = max(zone.coordinates.x for zone in self.graph.zones.values())
        min_x = min(zone.coordinates.x for zone in self.graph.zones.values())

        max_y = max(zone.coordinates.y for zone in self.graph.zones.values())
        min_y = min(zone.coordinates.y for zone in self.graph.zones.values())

        return (min_x, max_x, min_y, max_y)

    def _calculate_graph_scale(self) -> tuple[float, float]:
        """Pixels per map unit, separately for X and Y.

        A flat dimension (all zones on one line) gets the other
        dimension's scale, so circles keep a sensible size.
        """

        graph_width = self.max_x - self.min_x
        graph_height = self.max_y - self.min_y

        usable_width = self.window_width - self.map_margin * 2
        usable_height = self.window_height - self.map_margin * 2

        scale_x = usable_width / graph_width if graph_width else 0.0
        scale_y = usable_height / graph_height if graph_height else 0.0

        if not scale_x and not scale_y:
            return (1.0, 1.0)
        if not scale_x:
            scale_x = scale_y
        if not scale_y:
            scale_y = scale_x

        return (scale_x, scale_y)

    def to_screen_coordinates(
            self,
            coordinates: Coordinates) -> tuple[float, float]:
        """Takes a zone coordinates from graph
        and transforms it to screen coordinates.
        A flat map is centred in the window."""

        if self.max_x == self.min_x:
            screen_x = self.window_width / 2
        else:
            screen_x = (
                (coordinates.x - self.min_x) * self.scale_x
                + self.map_margin
            )

        if self.max_y == self.min_y:
            screen_y = self.window_height / 2
        else:
            screen_y = (
                (coordinates.y - self.min_y) * self.scale_y
                + self.map_margin
            )

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

        SimulationWindow(
            graph_drawer,
            drone_drawer,
            self.engine
        )

        arcade.run()

        # macOS removes a closed window only while events are processed:
        # handle them briefly before the terminal menu takes over again
        for _ in range(10):
            pyglet.app.platform_event_loop.step(0.01)


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
                radius=self.coord_transformer.zone_radius,
                color=self._get_zone_color(zone)
            )

        for label in self.zone_labels:
            label.draw()

    def _get_zone_color(self, zone: Zone) -> arcade.types.Color:
        """Converst color-name string into Arcade color"""

        if zone.color is None:
            return COLOR_DEFAULT

        color = zone.color.upper()

        color_value = getattr(arcade.color, color, None)

        if isinstance(color_value, arcade.types.Color):
            return color_value

        return COLOR_DEFAULT

    def _create_zone_labels(self) -> list[arcade.Text]:
        """Creates a lable for each zone in the graph"""

        zones_names: list[arcade.Text] = []

        label_marge = 6
        radius = self.coord_transformer.zone_radius
        crowded = self.coord_transformer.crowded

        for zone in self.graph.zones.values():
            x, y = self.coord_transformer.to_screen_coordinates(
                zone.coordinates
            )

            # when zones are close, neighbours alternate their name
            # above / below the circle so the names do not overlap
            below = crowded and (zone.coordinates.x + zone.coordinates.y) % 2
            if below:
                label_y = y - radius - label_marge
                anchor_y = "top"
            else:
                label_y = y + radius + label_marge
                anchor_y = "baseline"

            label = arcade.Text(
                text=zone.name,
                x=x,
                y=label_y,
                color=arcade.color.BLACK,
                font_size=self.coord_transformer.label_font_size,
                font_name="Arial",
                anchor_x="center",
                anchor_y=anchor_y,
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
            if drone.state is Drone_state.IN_TRANSIT:
                # drawn halfway along its connection, not in a zone
                self._draw_drone(drone, 0, 1)
                continue

            if drone.current_zone not in drones_by_zone:
                drones_by_zone[drone.current_zone] = []

            drones_by_zone[drone.current_zone].append(drone)

        for zone, drones in drones_by_zone.items():
            x, y = self.coord_transformer.to_screen_coordinates(
                zone.coordinates
            )
            offset = self.coord_transformer.zone_radius * 0.8
            arcade.draw_text(
                text=str(len(drones)),
                x=x + offset,
                y=y + offset,
                color=arcade.color.BLACK,
                font_size=14 if offset > 30 else 10
            )
            # crowded map: one label per zone, the number shows the rest
            limit = 1 if self.coord_transformer.crowded else 5

            if len(drones) <= limit:
                visible_drones = drones
            else:
                visible_drones = [
                    drones[-1]
                ]

            for index, drone in enumerate(visible_drones):
                self._draw_drone(drone, index, len(visible_drones))

    def _draw_drone(self, drone: Drone, index: int, count: int) -> None:
        """Draws one drone; `index` of `count` drones shown in its zone,
        laid out in rows of three centred on the zone"""

        if drone.state is Drone_state.IN_TRANSIT:
            connection = drone.current_connection

            if connection is None:
                raise ValueError(
                    "Drone is in transit without a connection"
                )

            zone_a = connection.zone_a
            zone_b = connection.zone_b

            x1, y1 = self.coord_transformer.to_screen_coordinates(
                zone_a.coordinates)
            x2, y2 = self.coord_transformer.to_screen_coordinates(
                zone_b.coordinates)

            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
        else:
            x, y = self.coord_transformer.to_screen_coordinates(
                drone.current_zone.coordinates)

            columns = 3
            x_spacing = 35
            y_spacing = 25

            column = index % columns
            row = index // columns
            in_row = min(columns, count - row * columns)

            x += (column - (in_row - 1) / 2) * x_spacing
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

        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.graph_drawer = graph_drawer
        self.drone_drawer = drone_drawer
        self.engine = engine

        self.is_playing = False
        self.time_since_last_turn = 0.0

        self.turn_text = arcade.Text(
            "", x=20, y=WINDOW_HEIGHT - 30,
            color=arcade.color.BLACK, font_size=16, bold=True
        )
        self.moves_text = arcade.Text(
            "", x=20, y=WINDOW_HEIGHT - 55,
            color=arcade.color.BLACK, font_size=11
        )
        self.hints_text = arcade.Text(
            KEY_HINTS, x=20, y=15,
            color=arcade.color.BLACK, font_size=11
        )

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_update(self, delta_time: float) -> None:
        """Advance the simulation according to elapsed time"""

        if not self.is_playing:
            return

        if self.engine.is_finished:
            self.is_playing = False
            return

        self.time_since_last_turn += delta_time

        if self.time_since_last_turn >= TURN_DURATION:
            self.engine.run_turn()
            self.time_since_last_turn = 0.0

            if self.engine.is_finished:
                self.is_playing = False

    def on_key_press(self, key: int, key_modifier: int) -> None:
        """Make a turn if space pressed"""

        if key == arcade.key.SPACE:
            if not self.engine.is_finished:
                self.is_playing = not self.is_playing
                self.time_since_last_turn = 0.0

        elif key == arcade.key.RIGHT:
            if not self.is_playing and not self.engine.is_finished:
                self.engine.run_turn()

        elif key == arcade.key.ESCAPE:
            self.set_visible(False)
            self.close()

    def on_draw(self) -> None:
        """Calls all classes needed for visualization"""

        self.clear()
        self.graph_drawer.draw()
        self.drone_drawer.draw()
        self._draw_info()

    def _draw_info(self) -> None:
        """Draws the turn counter, the last moves and the key hints."""

        status = "finished" if self.engine.is_finished else (
            "playing" if self.is_playing else "paused"
        )
        self.turn_text.text = (
            f"Turn {self.engine.turn} / {self.engine.total_turns}"
            f"   ({status})"
        )

        moves = self.engine.last_line
        if len(moves) > 150:
            moves = moves[:147] + "..."
        self.moves_text.text = moves

        self.turn_text.draw()
        self.moves_text.draw()
        self.hints_text.draw()
