# Fly-In --- Development Progress Summary

**Date:** September 10, 2026

## Goal of Today's Work

Today we focused on getting the basic `SimulationEngine` working
correctly for **normal one-turn drone movement** before implementing a
real pathfinding algorithm.

The main architectural principle remains:

``` text
PATHFINDER / ALGORITHM
    decides where a drone should TRY to move

            ↓ requested move

SIMULATION ENGINE
    checks whether that move is legal
    and updates simulation state
```

The engine should enforce simulation rules; it should not eventually be
responsible for choosing the best route.

------------------------------------------------------------------------

## 1. Basic Simulation Loop

The engine runs turn by turn until every drone has reached the end zone.

The current structure is conceptually:

``` text
while not all drones are delivered:
    process every non-delivered drone
    increase turn
```

Each drone is initialized at the start zone with an `AVAILABLE` state.

We also confirmed that the start zone still tracks its actual number of
occupants even though its capacity is unlimited.

------------------------------------------------------------------------

## 2. Normal One-Turn Movement

We implemented and tested basic movement between normal zones.

A successful move currently performs these operations:

1.  Decrease occupancy of the drone's current zone.
2.  Increase occupancy of the destination zone.
3.  Update `drone.current_zone`.
4.  Append the destination to the drone's actual `path`.
5.  Mark the drone as delivered if the destination is the END zone.

The drone's `path` represents the **actual route already travelled**,
not a planned route.

------------------------------------------------------------------------

## 3. Move Validation

The engine currently checks whether a requested destination can be
entered using:

-   `zone.has_capacity()`
-   `connection.has_capacity()`

The current `_can_move_to()` behavior also changes a drone to `WAITING`
when movement is not currently possible.

When movement becomes possible again, the drone returns to `AVAILABLE`.

Conceptually:

``` text
destination unavailable
    -> WAITING

destination available later
    -> AVAILABLE
    -> move
```

------------------------------------------------------------------------

## 4. Zone Capacity Testing

We tested a regular intermediate zone with:

``` text
[max_drones=2]
```

Example map:

``` text
        A (capacity 2)
       / \
start       end
       \ /
        B
```

With three drones, the observed behavior was:

``` text
Turn 0:
D1 -> A
D2 -> A
D3 -> B

Turn 1:
D1 -> end
D2 -> end
D3 -> end
```

This confirmed that:

-   A zone accepts drones until `max_drones` is reached.
-   Once capacity is reached, `has_capacity()` returns `False`.
-   The engine can try another neighbor if the first neighbor is
    unavailable.
-   Multiple drones can occupy the END zone.

------------------------------------------------------------------------

## 5. Blocked Zone Testing

We changed `B` to:

``` text
[zone=blocked]
```

The third drone first found `A` full and then checked `B`.

Because `Zone.has_capacity()` also rejects blocked zones, D3 correctly
remained at START.

Observed behavior:

``` text
Turn 0:
D1 -> A
D2 -> A
D3 waits at start

Turn 1:
D1 -> end
D2 -> end
D3 -> A

Turn 2:
D3 -> end
```

This confirmed:

-   Blocked zones cannot be entered.
-   A waiting drone can retry on a later turn.
-   Once A is freed, D3 can enter it.
-   The simulation continues until the final drone is delivered.

------------------------------------------------------------------------

## 6. START Neighbor Behavior

Because graph connections are bidirectional, when a drone is at `A` in:

``` text
start <-> A <-> end
```

`graph.neighbors(A)` includes both:

``` text
start
end
```

For the current temporary movement logic, we skip START:

``` python
if zone.role is Zone_role.START:
    continue
```

We moved this check before the debug print so the engine no longer
unnecessarily prints:

``` text
Checking 'start'
```

Important: this is **temporary routing behavior**, not a permanent
simulation rule.

Eventually the pathfinder should choose the desired next zone, so the
engine should not need to decide that moving toward START is
strategically bad.

------------------------------------------------------------------------

## 7. Fixed Early Simulation Termination

We found an indentation bug in `_all_drones_delivered()`.

Previously, `return True` was inside the `for` loop. This caused the
function to return `True` after checking only the first drone once D1
had been delivered.

The correct concept is:

``` text
for every drone:
    if any drone is not delivered:
        return False

only after checking all drones:
    return True
```

After fixing this, the simple three-drone linear simulation correctly
continued until D3 reached END.

------------------------------------------------------------------------

## 8. One Move Per Drone Per Turn

We also identified that `_process_drone()` must stop processing a drone
after it successfully moves.

Without stopping, a drone could potentially execute more than one
movement during a single simulation turn if several neighbors were
legal.

The intended logic is:

``` text
try neighbor

if illegal:
    continue looking

if legal:
    move drone
    stop processing this drone for this turn
```

This keeps normal movement to one adjacent-zone move per turn.

------------------------------------------------------------------------

## 9. Linear Pipeline Test

For:

``` text
start -> A -> end
```

with three drones and `A.max_drones = 1`, the simulation now behaves as
expected:

``` text
Turn 0:
D1 -> A

Turn 1:
D1 -> end
D2 -> A

Turn 2:
D2 -> end
D3 -> A

Turn 3:
D3 -> end
```

This confirmed basic occupancy updates, waiting, retrying, delivery, and
termination.

------------------------------------------------------------------------

## 10. Dead-End Test Exposed the Next Problem

We discussed testing a normal, non-blocked dead end.

The current `_process_drone()` does not have a real routing algorithm.
It simply iterates through neighboring zones and chooses the first legal
destination.

That can cause a drone to:

-   enter a dead end,
-   move backward,
-   bounce between zones,
-   or remain unable to reach END.

Because `_all_drones_delivered()` then never becomes true, the
simulation can run forever.

This is not something we should solve by adding more routing-specific
`if` statements to `SimulationEngine`.

Instead, it demonstrates that we have reached the point where a real
**Pathfinder** is needed.

------------------------------------------------------------------------

# Current Status

Basic normal movement is now working well enough to proceed.

``` text
Drone initialization             DONE
Start occupancy tracking         DONE
Normal zone occupancy            DONE
max_drones testing               DONE
Blocked-zone rejection           DONE
WAITING behavior                 DONE
WAITING -> AVAILABLE             DONE
Normal one-turn movement         DONE
Actual drone path tracking       DONE
End delivery                     DONE
Unlimited END occupancy          DONE
Simulation termination           DONE
One movement per drone/turn      DONE

Real pathfinding                 NEXT
Restricted movement              LATER
Real connection transit usage    LATER
Simultaneous reservations        LATER
Priority routing                 LATER
Optimization                     LATER
Final output formatting          LATER
```

------------------------------------------------------------------------

# Next Step --- Introduce Pathfinder

The next component should be a separate `Pathfinder` class.

Start with:

``` text
pathfinder.py
```

Its responsibility should be:

> Find a valid route through the graph from START to END.

It should **not** initially worry about:

-   current zone occupancy,
-   connection occupancy,
-   waiting drones,
-   simulation turns,
-   restricted movement cost,
-   priority optimization,
-   distributing multiple drones.

The first goal is simply:

``` text
Given this graph, can I find a valid path from START to END
without entering blocked zones?
```

------------------------------------------------------------------------

## First Pathfinder Algorithm: BFS

The suggested first algorithm is **Breadth-First Search (BFS)**.

For normal zones where each movement currently costs one turn, BFS is a
good starting point because it finds a path with the fewest edges.

BFS needs three main pieces of information:

### Queue

Zones waiting to be explored.

Initially:

``` text
queue = [start]
```

### Visited

Zones that have already been discovered.

This prevents loops such as:

``` text
start -> A -> start -> A -> ...
```

Initially:

``` text
visited = {start}
```

### Came From

A record of how each discovered zone was reached.

For example:

``` text
B came from start
C came from B
end came from C
```

Once END is found, this information can reconstruct:

``` text
end <- C <- B <- start
```

and reverse it into:

``` text
start -> B -> C -> end
```

------------------------------------------------------------------------

## Suggested Pathfinder Structure

Start small.

Conceptually:

``` text
Pathfinder
    graph: Graph
```

Eventually its use could look like:

``` text
pathfinder = Pathfinder(graph)

path = pathfinder.find_path(
    graph.start,
    graph.end
)
```

The first version of `find_path()` should:

1.  Start exploration from START.
2.  Explore neighbors using `Graph.neighbors()`.
3.  Ignore blocked zones.
4.  Ignore already visited zones.
5.  Record where each discovered zone came from.
6.  Stop when END is discovered.
7.  Reconstruct and return the path.
8.  Handle the case where no valid path exists.

------------------------------------------------------------------------

# Recommended Development Order

Do not jump directly to the complete optimized Fly-In algorithm.

Continue incrementally:

``` text
1. Create Pathfinder class skeleton
        ↓
2. Understand and implement BFS queue
        ↓
3. Add visited tracking
        ↓
4. Skip blocked zones
        ↓
5. Detect END
        ↓
6. Reconstruct one valid path
        ↓
7. Test BFS independently from SimulationEngine
        ↓
8. Give the pathfinder's requested next move to the engine
        ↓
9. Test pathfinding + normal movement together
        ↓
10. Add restricted two-turn movement
        ↓
11. Handle connection occupancy/transit
        ↓
12. Improve simultaneous-turn scheduling
        ↓
13. Find/use multiple paths
        ↓
14. Add priority and weighted path costs
        ↓
15. Optimize total simulation turns
```

The key rule going forward is to preserve the separation:

``` text
PATHFINDER
"What should the drone try to do?"

SIMULATION ENGINE
"Is that requested action legal right now?"
```

That separation will become increasingly important once restricted
zones, capacities, multiple paths, and scheduling are added.
