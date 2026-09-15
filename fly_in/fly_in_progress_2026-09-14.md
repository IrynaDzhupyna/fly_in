# Fly-In Progress Summary --- 2026-09-14

**Date:** September 14 2026
## Where we started today

The immediate problem was that a drone could enter a dead end and the
simulation could get stuck in an infinite loop. We decided that the
engine should not greedily choose any available neighboring zone. A
pathfinder should first find a complete route from START to END.

We began with **BFS (Breadth-First Search)** as the first pathfinding
layer. This is intentionally a simple foundation: it finds a valid
shortest-by-edges route on the current unweighted graph. Later, the
final project will need more sophisticated routing for movement costs,
priority zones, capacities, multiple paths, and multiple drones.

## Architecture we are keeping

The main responsibility boundary is:

``` text
PATHFINDER
    decides what route / move should be attempted

            ↓

SIMULATION ENGINE
    validates whether movement is legal now
    executes the move
    updates drone / zone / connection state
```

`Drone.path` remains the **actual path already travelled**, not the
future planned route.

We also decided that the `SimulationEngine` should own one shared
`PathFinder`, because all drones operate on the same graph.

Conceptually:

``` text
SimulationEngine
├── graph
├── drones
├── turn
└── path_finder
```

## BFS implemented today

`PathFinder.find_path()` now:

-   Starts from `graph.start`.
-   Uses a FIFO queue.
-   Uses `visited` to prevent revisiting zones and therefore avoids
    cycles.
-   Skips `Zone_type.BLOCKED` zones.
-   Uses `come_from` to remember how each discovered zone was reached.
-   Detects when END is unreachable and raises `PathFinderError`.
-   Reconstructs the route backwards from END to START.
-   Reverses it and returns a forward `list[Zone]`.

The current conceptual BFS data structures are:

``` python
queue = [start]
visited: set[Zone] = {start}
come_from: dict[Zone, Zone | None] = {start: None}
```

When discovering a new zone:

``` python
queue.append(zone)
visited.add(zone)
come_from[zone] = current
```

Route reconstruction works conceptually like:

``` text
come_from:

start → None
A     → start
C     → A
end   → C

Reconstruction:
end ← C ← A ← start

After reversing:
start → A → C → end
```

## Hashability problem we solved

Python initially raised:

``` text
TypeError: unhashable type: 'Zone'
```

because BFS wanted to put mutable `Zone` dataclass objects in a `set`
and use them as dictionary keys.

We discussed two possible solutions:

1.  Store zone names (`str`) in BFS bookkeeping.
2.  Make `Zone` hashable using its stable identity.

We chose the second approach because it lets Pathfinder work naturally
with actual `Zone` objects.

The idea is:

``` python
def __hash__(self) -> int:
    return hash(self.name)
```

This means the hash of a zone depends only on its name.

Important rule: if `name` determines the hash, a zone's name must remain
stable while that object is used in sets or as dictionary keys. Runtime
fields such as occupancy may still change because they are not part of
the hash.

This allows:

``` python
visited: set[Zone]
come_from: dict[Zone, Zone | None]
```

instead of converting the whole pathfinder to strings.

## Tests completed

We tested the pathfinder independently from the simulation engine.

For a reachable map such as:

``` text
start ─ A ─ end
   \
    B   (dead end)
```

BFS should return:

``` text
start
A
end
```

For a map where END is completely unreachable, BFS correctly finishes
instead of looping forever and raises:

``` text
PathFinderError: The path was not found
```

This confirms the key behavior we wanted: dead ends and cycles do not
cause an endless search.

## Small cleanup still available

The current queue uses:

``` python
queue.pop(0)
```

This is correct for learning/basic BFS, but removing index 0 from a
Python list shifts the remaining elements. Later we should replace the
list with `collections.deque` and use `popleft()`.

Do this as a cleanup after the engine integration is working; it is not
the next conceptual problem.

------------------------------------------------------------------------

# Plan for Tomorrow

## Step 1 --- Finish connecting PathFinder to SimulationEngine

Add a `path_finder` attribute to `SimulationEngine` and initialize one
shared `PathFinder` from the engine's graph.

The engine should not create one pathfinder per drone.

For the first integration, call:

``` text
path_finder.find_path()
```

**once before the turn loop**, rather than once per drone or once per
turn.

Why: the current BFS only understands static graph structure and blocked
zones. Re-running it every turn would currently return the same path and
add unnecessary work.

## Step 2 --- Pass the route into `_process_drone()`

Our current preferred interface is conceptually:

``` text
_process_drone(drone, path)
```

rather than immediately storing the route as another engine-wide state
variable.

The next question to solve is:

> Given a drone's `current_zone` and a route such as
> `[start, A, C, end]`, how does `_process_drone()` determine the **next
> zone** that this drone should try to enter?

Do not jump straight to code. Work through examples first:

``` text
current = start  → desired next = A
current = A      → desired next = C
current = C      → desired next = end
```

## Step 3 --- Let the engine validate the desired move

Once `_process_drone()` knows the desired next zone, keep the
responsibility split:

``` text
PathFinder route
      ↓
desired next zone
      ↓
SimulationEngine validation
      ↓
legal? move
illegal now? wait
```

The engine should remain responsible for zone capacity, connection
capacity, and actual state updates.

## Step 4 --- Test one route with multiple drones

Initially, all drones can use the same BFS route. This is **not the
final routing strategy**. It is only an integration test.

Verify:

-   Drones follow the planned route instead of entering dead ends.
-   Capacity rules still prevent illegal moves.
-   Waiting does not create an infinite loop.
-   Drones eventually reach END.
-   `Drone.path` records the actual travelled route.

## Step 5 --- Add targeted Pathfinder tests

Before making the algorithm more advanced, keep small maps for:

-   Simple route.
-   Dead end.
-   Cycle.
-   Blocked shortcut.
-   Completely unreachable END.
-   Two alternative valid routes.

These maps will become useful regression tests as the algorithm changes.

## Step 6 --- Improve the BFS queue

After correctness is stable:

``` text
list + pop(0)
        ↓
collections.deque + popleft()
```

This preserves FIFO behavior while making queue removal efficient.

## Step 7 --- Only then move beyond basic BFS

Basic BFS minimizes the number of edges. It does **not** solve the
complete Fly-In optimization problem.

Later routing work must account for:

-   Restricted zones with higher movement cost.
-   Priority-zone preference.
-   Zone and connection capacities.
-   Multiple useful routes.
-   Distribution of multiple drones between routes.
-   Waiting when it improves total throughput.
-   Avoiding conflicts and deadlocks.
-   Minimizing total simulation turns.

So tomorrow's goal is **not** to build the final algorithm. The goal is
to make one BFS route cleanly drive the existing SimulationEngine while
preserving the architecture boundary.

## Tomorrow's starting point

Start from this question:

> We have `path = [start, A, C, end]` and `drone.current_zone`. How
> should `_process_drone(drone, path)` find the next zone the drone
> should request?

Solve that first, then connect it to the engine's existing
move-validation logic.

## Core principle to remember

``` text
PathFinder = strategist
SimulationEngine = referee
Drone = state of one drone
Graph = network structure
```

Keep those responsibilities separate as the project grows.
