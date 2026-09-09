# Fly-In Simulation Engine — Progress Summary

## Goal

We are building the drone simulation engine step by step using OOP. The main goal is to keep responsibilities separated so that the simulation engine enforces the rules, while a future algorithm/pathfinder decides where drones should try to move.

## Main responsibility split

### Algorithm / Pathfinder — future work

The algorithm will act as the **strategist**. It will decide what a drone should try to do, for example which neighboring zone it should move toward.

It should answer a question such as:

> Where should this drone try to move next?

We have **not implemented the algorithm yet**.

### SimulationEngine

The engine acts as the **referee**. It should not decide which route is best. Instead, once a desired move is provided, it checks whether that move is legal according to the simulation rules.

Examples of engine responsibilities:

- Check destination-zone capacity.
- Check connection capacity.
- Reject blocked destinations.
- Later handle movement cost, including restricted zones.
- Later handle conflicts between drones in the same turn.
- Execute legal moves.
- Make a drone wait when a requested move cannot currently happen.
- Track simulation turns.
- Detect when every drone has been delivered.

## Drone states

We simplified the drone states to:

```python
class Drone_state(Enum):
    AVAILABLE = "available"
    TRANSIT = "transit"
    DELIVERED = "delivered"
```

Meaning:

- `AVAILABLE`: the drone is currently in a zone and can potentially move.
- `TRANSIT`: the drone is travelling between zones. This will matter especially for restricted movement.
- `DELIVERED`: the drone has reached the end zone.

We decided that an `ARRIVED` state is not necessary for now.

## Drone path

The existing `Drone.path` represents the **actual path already taken by the drone**.

It is **not** a planned route from the future pathfinding algorithm.

Therefore, when we eventually add route planning, planned-route information should be kept separate from `Drone.path`.

## SimulationEngine initialization

The engine receives a `Graph` and creates its own drones because the graph already contains `nb_drones`.

Each drone starts with:

- An ID from `1` through `graph.nb_drones`.
- State `Drone_state.AVAILABLE`.
- `current_zone = graph.start`.

The current initialization concept is:

```python
def __post_init__(self) -> None:
    """Initiates the list of drones and puts all drones on start zone."""

    for i in range(1, self.graph.nb_drones + 1):
        drone = Drone(
            id=i,
            state=Drone_state.AVAILABLE,
            current_zone=self.graph.start
        )

        self.drones.append(drone)
        self.graph.start.increase_capacity()
```

Calling `increase_capacity()` is preferable to modifying `zone.occupants` directly because the `Zone` object manages its own occupancy state.

## Zone occupancy vs. zone capacity

An important distinction we established is:

### `occupants`

This means how many drones are **actually currently inside the zone**.

We track this for every zone, including START and END.

For example, if three drones begin at START:

```text
START.occupants = 3
```

When one leaves START:

```text
START.occupants = 2
```

When a drone reaches END, END's occupancy should also increase.

### `max_drones`

This represents a capacity restriction.

Regular zones are restricted by `max_drones`, while START and END have unlimited occupancy. Therefore START and END still track `occupants`, but their `max_drones` restriction is ignored.

We decided **not** to change START/END `max_drones` to the number of drones. Their unlimited behavior belongs in the capacity-checking logic instead.

## Current Zone methods

The current design is:

```python
def increase_capacity(self) -> bool:
    """Increases occupants by 1."""

    if not self.has_capacity():
        return False

    self.occupants += 1
    return True


def decrease_capacity(self) -> bool:
    """Decreases occupants by 1."""

    if self.occupants - 1 >= 0:
        self.occupants -= 1
        return True

    return False


def has_capacity(self) -> bool:
    """Checks if zone has capacity for one drone."""

    if self.type is Zone_type.BLOCKED:
        return False

    if self.role is Zone_role.START or self.role is Zone_role.END:
        return True

    if self.occupants < self.max_drones:
        return True

    return False
```

### Why `has_capacity()` is public

We decided to keep `has_capacity()` public because the `SimulationEngine` needs to ask whether a drone **could** enter a zone without changing the zone yet.

The distinction is:

```text
has_capacity()
    asks whether entry is possible
    does not modify occupants

increase_capacity()
    attempts to add one drone
    modifies occupants

decrease_capacity()
    removes one drone
    modifies occupants
```

`has_capacity()` also rejects blocked zones, so the engine may not need an additional separate blocked-zone check when validating a destination.

## Connection capacity

The `Connection` class already has a capacity check similar to the zone:

```python
def has_capacity(self) -> bool:
    return len(self.occupants) < self.max_link_capacity
```

The engine will use this when determining whether a requested movement is currently legal.

One issue saved for later: the current type of `Connection.occupants` was `list[Zone]`. Conceptually, connection occupants will probably need to represent drones or drone IDs rather than zones. We have intentionally not fixed this yet because we are working one concept at a time.

## Graph neighbors

The graph already provides neighboring zones and their connections:

```python
def neighbors(self, zone: Zone) -> list[tuple[Zone, Connection]]:
    return [
        (connection.another_end(zone), connection)
        for connection in self.connections_for(zone.name)
    ]
```

Therefore the engine does not need another method that duplicates this behavior.

A returned item has the form:

```text
(neighbor_zone, connection_to_that_zone)
```

## Checking whether a move is legal

We started designing a helper such as `_can_move_to()`.

Its purpose is only to answer:

> Is this requested move legal right now?

At the current stage, the important checks are:

1. Does the destination zone have capacity?
2. Does the connection have capacity?

Because `Zone.has_capacity()` already returns `False` for a blocked zone, a separate blocked check may be redundant.

The helper should **not** choose which neighboring zone is best. That belongs to the future algorithm.

## Run loop

The planned engine loop works turn by turn until all drones are delivered.

The conceptual structure is:

```text
while not all drones are delivered:
    advance turn
    process drones that are not delivered
```

We also discussed a helper such as `_all_drones_delivered()` that loops through the drones and returns `False` if any drone is not in `Drone_state.DELIVERED`.

## Normal movement — next major engine operation

Once the engine knows that a normal move is legal, executing it should conceptually do three things:

```text
1. Drone leaves its current zone.
2. Drone enters the destination zone.
3. Drone's current_zone changes to the destination.
```

Because START and END occupancy is tracked too, their `occupants` values should also increase/decrease when drones enter or leave them. Their special behavior is only that they have no occupancy limit.

We have **not implemented this movement helper yet**.

## What we intentionally have not implemented yet

To keep the project understandable, we have postponed:

- The pathfinding/routing algorithm.
- Choosing the best neighboring zone.
- Full `_process_drone()` behavior.
- Restricted-zone two-turn movement.
- Proper transit state/data.
- Movement-cost handling inside the engine.
- Simultaneous movement conflicts.
- Per-turn reservation of zone/connection capacity.
- Priority-route preference.
- Rerouting decisions.
- Final output formatting.

## Planned next steps

We should continue in small pieces rather than implementing everything at once.

### Step 1 — Review current `SimulationEngine`

Look at the complete current engine code so that new methods fit the code that actually exists.

### Step 2 — Finish move validation

Make `_can_move_to()` work cleanly with:

- `Zone.has_capacity()`
- `Connection.has_capacity()`

Do not add pathfinding logic to it.

### Step 3 — Execute one legal NORMAL move

Design the engine operation that:

- Decreases occupancy of the source zone.
- Increases occupancy of the destination zone.
- Updates the drone's current zone / actual path.

At this stage, focus only on movement costing one turn.

### Step 4 — Connect movement to `_process_drone()`

Eventually `_process_drone()` should receive or obtain a **requested move**, validate it, and execute it or leave the drone waiting.

The algorithm interface still needs to be designed because no pathfinding algorithm exists yet.

### Step 5 — Add restricted movement

After normal movement works, handle zones with movement cost `2`. This will require thinking carefully about `Drone_state.TRANSIT` and what information must be stored while a drone is travelling on a connection.

### Step 6 — Handle multiple drones in one turn

After individual movement works correctly, implement conflicts and simultaneous-turn behavior. The engine must make sure multiple drones do not violate zone or connection capacities.

### Step 7 — Add the routing/pathfinding algorithm

Only after the engine rules are clear should we connect a strategist that chooses efficient desired moves/routes.

## Core design principle to keep

The most important architecture decision so far is:

```text
PATHFINDER / ALGORITHM
    decides what the drone should TRY to do

            ↓ requested move

SIMULATION ENGINE
    decides whether that move is ALLOWED now
    and updates the simulation state
```

Keeping this boundary clear should make the later pathfinding algorithm easier to add without turning `SimulationEngine` into one large class responsible for everything.
