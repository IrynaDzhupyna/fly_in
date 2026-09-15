# Fly-In — Path / Advanced Pathfinder Progress Summary

## Date
15 September 2026

## Goal of today's work

Today we focused on improving the pathfinding design using OOP. The main idea was to separate:

- the object that **searches for routes** (`PathFinderAdv`)
- the object that **represents one discovered route** (`Path`)
- the drone's existing `path`, which remains the **actual route already travelled by that drone**

This keeps planned routes separate from movement history.

## OOP decision: `Path` should not inherit from `PathFinder`

We considered making `Path` inherit from `PathFinder`, but rejected that design.

Inheritance should represent an **is-a** relationship:

- A `PathFinder` searches for paths.
- A `Path` represents a path.

Therefore, a `Path` is **not** a kind of `PathFinder`.

The intended relationship is composition:

```text
PathFinderAdv
    |
    | finds / creates
    v
   Path
```

## `Path` data class

We introduced a dedicated `Path` data object.

Current design:

```python
@dataclass
class Path:
    zones: list[Zone]
    cost: int
    moves: int
```

### Meaning of the fields

`zones`
- The ordered zones belonging to the planned route.
- Example:

```text
[start, A, B, end]
```

`moves`
- Number of transitions/edges between zones.
- It is currently calculated as:

```python
len(valid_path) - 1
```

Example:

```text
start -> A -> B -> end
```

contains 4 zones but 3 moves.

`cost`
- Total movement cost of traversing the route.
- It is different from the number of moves because restricted zones cost 2 turns to enter.

Example:

```text
start -> A(normal) -> B(restricted) -> end(normal)
```

has:

```text
moves = 3
cost = 4
```

We decided to keep `moves` in `Path` for now even though it can be derived from `zones`.

We discussed a future `capacity` property but intentionally postponed it until we define precisely what path capacity means.

## Zone movement cost

The existing `Zone_type` already contains the correct source of truth:

```python
class Zone_type(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def movement_cost(self) -> int:
        return 2 if self is Zone_type.RESTRICTED else 1
```

We decided **not** to add another `cost` attribute directly to `Zone`.

A zone's movement cost can already be obtained with:

```python
zone.type.movement_cost
```

Adding a separate `Zone.cost` would create two possible sources of truth and could allow inconsistent state.

## Difference between moves, path cost, and simulation turns

This distinction is important.

For:

```text
start -> A(normal) -> B(restricted) -> end
```

we have:

```text
moves = 3
path cost = 4
```

The actual simulation may take even longer because drones can have to wait due to:

- zone capacity
- connection capacity
- conflicts with other drones
- scheduling

Therefore:

```text
moves != necessarily path cost
path cost != necessarily final simulation turns
```

## `PathFinderAdv`

Current direction:

```python
@dataclass
class PathFinderAdv:
    graph: Graph
    all_paths: list[Path] = field(init=False, default_factory=list)
```

`all_paths` belongs to the pathfinder and starts empty, so callers should only need to provide the graph.

Conceptually:

```python
path_finder = PathFinderAdv(graph)
```

rather than forcing the caller to provide an empty path list.

## BFS improvements made today

We corrected several details in the BFS implementation.

### Queue

Because we use `popleft()`, the queue is a deque of zones:

```python
queue: deque[Zone] = deque([start])
```

### Loop condition

We use:

```python
while queue:
```

instead of:

```python
while queue is not None:
```

An empty deque is still not `None`; `while queue:` correctly stops when it becomes empty.

### `come_from`

Correct type:

```python
come_from: dict[Zone, Zone | None] = {start: None}
```

When discovering a new zone:

```python
come_from[zone] = current
```

This means:

```text
zone -> the zone we came from
```

Example:

```text
start -> None
A     -> start
B     -> A
end   -> B
```

That lets us reconstruct the route backwards from `end`.

## Path reconstruction

After BFS, we check whether the end was reached:

```python
if end not in come_from:
    raise PathFinderError("The path doesn't have 'end'")
```

Then reconstruct backwards:

```python
current: Zone | None = end
valid_path: list[Zone] = []

while current is not None:
    valid_path.append(current)
    current = come_from[current]

valid_path.reverse()
```

This converts:

```text
end -> B -> A -> start
```

into:

```text
start -> A -> B -> end
```

## Creating the `Path` object

After reconstruction, the intended calculation is:

```python
path = Path(
    zones=valid_path,
    cost=sum(
        zone.type.movement_cost
        for zone in valid_path[1:]
    ),
    moves=len(valid_path) - 1
)

self.all_paths.append(path)
```

We skip `valid_path[0]` when calculating cost because the first zone is `start`; the drone begins there and does not pay a movement cost for entering it.

## Important limitation discovered

The current BFS can find **one route**, but it cannot find all possible routes.

The reason is the global visited set:

```python
visited: set[Zone] = {start}
```

and the structure:

```python
come_from: dict[Zone, Zone | None]
```

Each zone can only have one stored parent.

For example:

```text
        A -> C
       /     \
start         end
       \     /
        B -> D
```

there can be both:

```text
start -> A -> C -> end
start -> B -> D -> end
```

but a single `come_from[end]` can only remember one predecessor.

## Why blocking the previous path is not enough

We considered finding one route and then blocking a zone from that route.

For:

```text
start -> A -> end
     \
      -> B -> end
```

blocking `A` would allow the second search to find the path through `B`.

However, this fails when valid paths share zones:

```text
          B
         / \
start -> A   -> end
         \ /
          C
```

Valid paths include:

```text
start -> A -> B -> end
start -> A -> C -> end
```

If we block `A` after finding the first path, we accidentally eliminate the second valid path too.

Therefore we should not globally block every zone from an already-found path.

## New idea for finding multiple simple paths

The next design direction is to make the queue store an **entire candidate path**, rather than only one current zone.

Instead of:

```text
queue:
start
A
B
```

we would conceptually store:

```text
queue:
[start]
[start, A]
[start, A, B]
...
```

When a candidate branches, we can create independent candidates:

```text
[start, A, B]
[start, A, C]
```

and eventually discover:

```text
[start, A, B, end]
[start, A, C, end]
```

The key rule becomes:

> A neighbor must not already exist inside the candidate path currently being explored.

This prevents loops while still allowing different candidate paths to share zones.

That means the visited concept becomes **path-local**, instead of one global `visited` set for the entire search.

## Where we stopped

The final question we reached was:

If the queue stores candidate paths such as:

```python
[start, A, B]
```

instead of individual zones, what should the queue type become?

Current:

```python
queue: deque[Zone]
```

Next we need to reason out the nested type representing:

```text
deque containing lists of Zone objects
```

Do this before writing the new algorithm.

# Plan for next session

## Step 1 — Finish and test the current single-path version

Before replacing the search algorithm, make sure the current implementation correctly creates one `Path` object with:

- correct `zones`
- correct `moves`
- correct `cost`
- blocked zones ignored
- unreachable end raising `PathFinderError`

Also consider stopping BFS once `end` has been found instead of continuing to explore unnecessary zones.

## Step 2 — Design the candidate-path queue

Work out the correct data structure and type annotation for a queue whose items are complete candidate routes.

Conceptually:

```text
deque
  -> candidate path
       -> Zone
       -> Zone
       -> Zone
```

Do not immediately copy an all-paths algorithm. Build it step by step and understand why each part exists.

## Step 3 — Replace global `visited` with path-local cycle prevention

For each candidate path:

1. Look at its last zone.
2. Get that zone's neighbors.
3. Ignore blocked zones.
4. Ignore a neighbor if that neighbor already appears in the same candidate path.
5. Otherwise create a new candidate path.

This should prevent cycles without globally forbidding shared zones.

## Step 4 — Detect completed candidate paths

When the last zone of a candidate path is `end`, that candidate represents a complete route.

Convert it into a `Path` object with:

```text
zones
cost
moves
```

and add it to `all_paths`.

## Step 5 — Test branching and loops

Create small maps specifically for understanding the algorithm.

Test at least:

```text
Two separate routes
Shared-prefix routes
A graph containing a cycle
A blocked branch
No route to end
```

Verify that the search does not enter an infinite loop.

## Step 6 — Think about whether we truly want *all* paths

This will become an important optimization question.

A graph can contain a very large number of simple paths. Finding literally every possible path can become expensive.

The Fly-In objective is not merely to enumerate routes; it is to distribute drones efficiently and minimize simulation turns.

After we understand the multiple-path algorithm, decide whether the final system should:

- enumerate all simple paths,
- keep only useful candidate paths,
- find a limited number of best paths,
- or use another strategy.

Do not optimize this prematurely; first understand and test the basic multiple-path search.

## Step 7 — Later: path capacity and route comparison

Once multiple paths exist, define what `Path.capacity` should actually mean.

Potential factors include:

- minimum zone capacity along the path
- connection capacities
- shared zones/connections with other paths
- throughput per simulation turn

Only add the attribute once its meaning is precise.

Then `PathFinderAdv` can eventually compare routes using information such as:

```text
Path A:
moves = 3
cost = 3
capacity / throughput = ...

Path B:
moves = 4
cost = 5
capacity / throughput = ...
```

This will prepare us for assigning multiple drones intelligently.

# Architecture to preserve

Keep the responsibility boundaries clear:

```text
PathFinderAdv
    searches the graph
    discovers candidate routes
    calculates route properties
    returns/stores Path objects

Path
    represents one planned route
    stores route information

SimulationEngine
    enforces whether requested movements are legal
    updates drone/zone/connection state

Drone.path
    records the route actually travelled by that drone
```

The next session should continue from the candidate-path queue idea rather than jumping directly into drone scheduling.
