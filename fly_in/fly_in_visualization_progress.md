# Fly-In Visualization Architecture --- Progress Summary

## Goal

We started planning the visualization architecture for the Fly-In
project using **Arcade**.

The main design goal is to keep responsibilities separated and make
`main()` simple.

Current intended entry flow:

``` python
graph = Parser(filename).parse()

visualizer = Visualizer(graph)
visualizer.run()
```

Parsing stays outside the visualization layer. `Visualizer` receives an
already-created `Graph`.

------------------------------------------------------------------------

## 1. Visualization Architecture

We currently plan these components:

``` text
Visualizer
│
├── GraphDrawer
├── DroneDrawer
└── SimulationWindow
      ├── GraphDrawer
      └── DroneDrawer
```

### `Visualizer`

Responsibility:

> Initializes and connects all components needed for the graphical
> simulation, then starts the visualization.

Current structure:

``` python
class Visualizer:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self) -> None:
        graph_drawer = GraphDrawer(self.graph)
        drone_drawer = DroneDrawer()

        window = SimulationWindow(
            graph_drawer,
            drone_drawer
        )
```

`Visualizer` is a **coordinator**. It should not contain graph drawing
logic, parsing logic, or drone drawing logic.

### `SimulationWindow`

Responsibility:

> Creates and manages the Arcade window and controls when drawing
> happens.

Initial window constants:

``` python
WINDOW_TITLE = "Fly-in"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
```

Background:

``` python
arcade.csscolor.CORNFLOWER_BLUE
```

The window will eventually hold references to `GraphDrawer` and
`DroneDrawer`.

Conceptually, `on_draw()` will become:

``` python
def on_draw(self) -> None:
    self.clear()

    self.graph_drawer.draw()
    self.drone_drawer.draw()
```

We have not connected these objects yet.

### `GraphDrawer`

Responsibility:

> Draws the static graph: connections, zones, and zone names.

We decided to use one public method:

``` python
def draw(self) -> None:
    self._draw_connections()
    self._draw_zones()
```

The order matters:

1.  Draw connections.
2.  Draw zones on top of the connections.

Zone names will be considered part of drawing a zone rather than
creating a separate label system for now.

### `DroneDrawer`

Responsibility:

> Draws the changing drone positions.

It is intentionally still empty. We will return to it after the static
graph visualization works.

------------------------------------------------------------------------

## 2. Why `GraphDrawer` Uses Plural Drawing Methods

We considered two designs.

### Drawing one object at a time

``` python
def draw(self):
    for connection in self.graph.connections:
        self._draw_connection(connection)

    for zone in self.graph.zones.values():
        self._draw_zone(zone)
```

### Letting helper methods handle the collections

``` python
def draw(self):
    self._draw_connections()
    self._draw_zones()
```

We chose the second approach because we know the graph visualization
will need shared **scaling and translation**.

Current intended structure:

``` python
def _draw_connections(self) -> None:
    for connection in self.graph.connections:
        ...

def _draw_zones(self) -> None:
    for zone in self.graph.zones.values():
        ...
```

Both use the same graph-to-screen coordinate transformation.

------------------------------------------------------------------------

## 3. Coordinate Representation

Existing project structure:

``` python
@dataclass
class Coordinates:
    x: int
    y: int


@dataclass
class Zone:
    name: str
    coordinates: Coordinates
    ...
```

We considered making the coordinate transformation receive a `Zone`:

``` python
_to_screen_coordinates(zone)
```

but decided against it.

The transformation only needs coordinates, so the clearer interface is:

``` python
def _to_screen_coordinates(
    self,
    coordinates: Coordinates
) -> tuple[float, float]:
    ...
```

This keeps the transformation independent from the complete `Zone`
object.

Usage for a connection:

``` python
x_a, y_a = self._to_screen_coordinates(zone_a.coordinates)
x_b, y_b = self._to_screen_coordinates(zone_b.coordinates)
```

------------------------------------------------------------------------

## 4. Graph Bounds

To fit arbitrary graph coordinates into the window, `GraphDrawer` needs
to know:

``` text
min_x
max_x
min_y
max_y
```

We decided these values belong to `GraphDrawer`, not `Visualizer`.

They are calculated once because the graph is static.

Current approach:

``` python
def _calculate_graph_bounds(
    self
) -> tuple[int, int, int, int]:

    max_x = max(
        zone.coordinates.x
        for zone in self.graph.zones.values()
    )
    min_x = min(
        zone.coordinates.x
        for zone in self.graph.zones.values()
    )

    max_y = max(
        zone.coordinates.y
        for zone in self.graph.zones.values()
    )
    min_y = min(
        zone.coordinates.y
        for zone in self.graph.zones.values()
    )

    return min_x, max_x, min_y, max_y
```

And in `__init__`:

``` python
(
    self.min_x,
    self.max_x,
    self.min_y,
    self.max_y,
) = self._calculate_graph_bounds()
```

We discussed the risk of mixing up four tuple values. For now we decided
not to introduce another `GraphBounds` class. We will keep the tuple
order consistently:

``` text
min_x → max_x → min_y → max_y
```

If graph-bound handling grows later, a dedicated object can be
introduced.

------------------------------------------------------------------------

## 5. Graph Scaling

We introduced:

``` python
MAP_MARGIN = 100
```

The graph must fit inside:

``` text
1280 × 720
```

while leaving space around the edges.

The usable drawing dimensions are:

``` python
usable_width = WINDOW_WIDTH - MAP_MARGIN * 2
usable_height = WINDOW_HEIGHT - MAP_MARGIN * 2
```

Graph dimensions:

``` python
map_width = self.max_x - self.min_x
map_height = self.max_y - self.min_y
```

Scale calculation:

``` python
def _calculate_graph_scale(self) -> float:
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

    scale_x = usable_width / map_width
    scale_y = usable_height / map_height

    return min(scale_x, scale_y)
```

We use:

``` python
min(scale_x, scale_y)
```

because the graph must fit on **both axes** while preserving its
proportions.

The scale is static, so we decided to calculate it once in
`GraphDrawer.__init__`:

``` python
self._map_scale = self._calculate_graph_scale()
```

rather than recalculating it for every zone and connection endpoint.

------------------------------------------------------------------------

## 6. Negative Coordinates and Relative Coordinates

We discussed graphs whose coordinates do not begin at `(0, 0)` and may
even be negative.

Example:

``` text
-10   -5   0   5
```

The first step of graph-to-screen conversion will be to make coordinates
relative to the graph's minimum:

``` python
relative_x = coordinates.x - self.min_x
relative_y = coordinates.y - self.min_y
```

For:

``` text
min_x = -10
```

we get:

``` text
Original X     Relative X

-10            0
 -5            5
  0           10
  5           15
```

This preserves distances between zones while translating the graph's own
coordinate system so that its minimum starts at zero.

We chose the names:

``` text
relative_x
relative_y
```

instead of `graph_x` / `graph_y` because they describe the values more
clearly.

------------------------------------------------------------------------

## 7. Centering the Graph

We decided the graph should not merely have margins --- it should also
be **centered inside the window**.

After scaling, calculate the actual size of the rendered graph:

``` python
map_width = self.max_x - self.min_x
map_height = self.max_y - self.min_y

scaled_width = map_width * self._map_scale
scaled_height = map_height * self._map_scale
```

Then calculate centering offsets:

``` python
offset_x = (WINDOW_WIDTH - scaled_width) / 2
offset_y = (WINDOW_HEIGHT - scaled_height) / 2
```

The important observation is that `MAP_MARGIN` is already used when
calculating the maximum scale.

Therefore the final offset does not need to simply add `MAP_MARGIN`;
centering naturally distributes the remaining free space.

The intended transformation is:

``` text
original graph coordinate
          ↓
subtract min_x / min_y
          ↓
relative coordinate
          ↓
multiply by graph scale
          ↓
scaled coordinate
          ↓
add centering offset
          ↓
screen coordinate
```

Eventually:

``` python
relative_x = coordinates.x - self.min_x
relative_y = coordinates.y - self.min_y

screen_x = relative_x * self._map_scale + self._offset_x
screen_y = relative_y * self._map_scale + self._offset_y
```

------------------------------------------------------------------------

## 8. Current `GraphDrawer` Initialization Direction

We are moving toward:

``` python
class GraphDrawer:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

        (
            self.min_x,
            self.max_x,
            self.min_y,
            self.max_y,
        ) = self._calculate_graph_bounds()

        self._map_scale = self._calculate_graph_scale()

        # next:
        # self._offset_x, self._offset_y = ...
```

The dependency order is intentional:

``` text
Graph
  ↓
Graph bounds
  ↓
Graph scale
  ↓
Centering offsets
  ↓
Graph → screen coordinate conversion
  ↓
Drawing
```

------------------------------------------------------------------------

# Next Steps

## Immediate next step: centering offsets

Create a helper that calculates the X/Y offsets once for the static
graph.

Possible direction:

``` python
def _calculate_graph_offset(
    self
) -> tuple[float, float]:
    ...
```

Then store the result in `__init__`:

``` python
self._offset_x, self._offset_y = (
    self._calculate_graph_offset()
)
```

The helper will use:

``` text
graph bounds
+ map scale
+ window width/height
```

to determine where the scaled graph should begin so that it is centered.

## Then finish `_to_screen_coordinates()`

It should use only already-calculated values:

``` text
self.min_x
self.min_y
self._map_scale
self._offset_x
self._offset_y
```

It should **not** recalculate graph bounds, scale, or offsets for each
coordinate.

## Then implement connection drawing

For every connection:

``` python
zone_a = connection.zone_a
zone_b = connection.zone_b

x_a, y_a = self._to_screen_coordinates(zone_a.coordinates)
x_b, y_b = self._to_screen_coordinates(zone_b.coordinates)
```

Then use Arcade to draw a line between the two screen positions.

## Then implement zone drawing

For every zone:

1.  Convert its graph coordinates to screen coordinates.
2.  Draw its shape.
3.  Draw its name.
4.  Later decide how zone role/type/color affects its appearance.

## Then connect `SimulationWindow`

Current `Visualizer` already intends to do:

``` python
window = SimulationWindow(
    graph_drawer,
    drone_drawer
)
```

but `SimulationWindow.__init__()` does not yet accept these objects.

Once `GraphDrawer` works, update the window so it stores:

``` text
GraphDrawer
DroneDrawer
```

and calls their `draw()` methods from `on_draw()`.

The Arcade event loop also still needs to be started as part of the
final `Visualizer.run()` flow.

## Finally: `DroneDrawer`

After the static graph renders correctly, design `DroneDrawer`.

Questions to solve later include:

-   What simulation object/state should `DroneDrawer` receive?
-   How does it know each drone's current zone?
-   How should multiple drones in the same start/end zone be displayed?
-   How should movement between zones be animated?
-   Should drone positions use the same graph-to-screen transformation
    owned by `GraphDrawer`, or should coordinate transformation
    eventually become its own shared component?

That last question should be postponed until drone drawing actually
needs it rather than abstracting prematurely.
