# Fly-In — Path Selection Progress Summary

## Date

19 September 2026

## Goal of today's work

Today we continued building the advanced pathfinding strategy for Fly-In.

The focus was not yet on moving drones. Instead, we worked on understanding the available routes and selecting a useful first group of paths that can operate without sharing intermediate zones.

The long-term project objective remains: move all drones from START to END in the fewest simulation turns while respecting zone capacity, connection capacity, restricted-zone movement costs, and conflicts.

---

## 1. Current `Path` object

`Path` represents one complete discovered route.

It currently stores:

```python
@dataclass
class Path:
    zones: list[Zone]
    cost: int
    moves: int
```

Meaning:

- `zones` — ordered zones belonging to the route.
- `cost` — total movement cost of the route.
- `moves` — number of edges/movements in the route.

`info_path()` is currently used for debugging and prints the route, total cost, and moves.

---

## 2. Finding all possible paths

`PathFinderAdv.find_all_paths()` performs a breadth-first exploration using:

```python
deque[Path]
```

We begin with:

```text
START
```

and create new `Path` objects whenever we expand to a neighboring zone.

A candidate neighbor is ignored when:

- it is already present in the current path, preventing loops;
- it is a blocked zone.

Only paths that actually reach END are stored in:

```python
self.all_paths
```

So after `find_all_paths()` finishes, we have all complete simple valid routes discovered by the current algorithm.

---

## 3. Sorting paths by cost

Inside `find_best_paths()` we currently sort all complete paths using:

```python
sorted_by_cost = sorted(
    self.all_paths,
    key=lambda path: path.cost
)
```

This means cheaper paths are considered first.

We also added protection for the case where no path exists:

```python
if not sorted_by_cost:
    raise PathFinderError("Nothing to sort")
```

A clearer error message such as `"No path from start to end"` may be used later.

---

## 4. Understanding a simulation turn

We clarified what a **turn** means.

A turn is one complete simulation step during which multiple drones may move simultaneously.

Example:

```text
TURN 1:
D1: START -> A
D2: START -> C

TURN 2:
D1: A -> B
D2: C -> D

TURN 3:
D1: B -> END
D2: D -> END
```

This is three simulation turns, even though six individual movements occurred.

This is important because the final optimization target is not simply shortest individual paths. We want to maximize useful simultaneous movement and minimize the number of turns needed to deliver the entire fleet.

---

## 5. Detecting conflicts between paths

We created:

```python
@dataclass
class PathConflict:
    path_a: Path
    path_b: Path
    zones: list[Zone]
```

A `PathConflict` represents two routes that share one or more intermediate zones.

START and END are intentionally ignored when checking shared zones because every route naturally shares them and both have special occupancy behavior.

The current method:

```python
conflicting_paths(
    sorted_paths: list[Path]
) -> list[PathConflict]
```

compares every pair of paths.

For each pair:

```text
path_a
path_b
```

we collect shared intermediate zones.

If there are no shared intermediate zones, no `PathConflict` is created.

If shared zones exist, we store:

```python
PathConflict(
    path_a=path_a,
    path_b=path_b,
    zones=shared_zones
)
```

This means we calculate path conflicts once and can reuse that information later instead of repeatedly comparing every zone.

---

## 6. `PathConflict.has_paths()`

Originally we were going to check both possible orders manually:

```text
path == conflict.path_a AND chosen == conflict.path_b

OR

path == conflict.path_b AND chosen == conflict.path_a
```

We decided that this was noisy and exposed too much internal detail.

Instead, `PathConflict` now knows how to answer whether it represents a pair:

```python
def has_paths(
    self,
    path_1: Path,
    path_2: Path
) -> bool:
    paths = self.path_a, self.path_b
    return path_1 in paths and path_2 in paths
```

This lets the pathfinder simply ask:

```python
conflict.has_paths(path, chosen)
```

The order of the two paths no longer matters.

We also fixed an earlier bug where `paths` was accidentally created from `path_1, path_2`, which made the method always return `True`.

---

## 7. Selecting a first non-conflicting path set

We added:

```python
chosen_paths: list[Path] = field(
    init=False,
    default_factory=list
)
```

to `PathFinderAdv`.

`find_best_paths()` now stores the selected paths in:

```python
self.chosen_paths
```

instead of a temporary local list.

The current greedy strategy starts with the cheapest route:

```python
self.chosen_paths = [sorted_by_cost[0]]
```

Then each remaining candidate is checked against every path already chosen.

Current logic:

```python
for path in sorted_by_cost[1:]:

    has_conflict = False

    for chosen in self.chosen_paths:

        for conflict in conflicts:
            if conflict.has_paths(path, chosen):
                has_conflict = True
                break

        if has_conflict:
            break

    if not has_conflict:
        self.chosen_paths.append(path)
```

### Meaning in plain English

For each candidate path:

1. Assume it does not conflict.
2. Compare it with every already-selected path.
3. Search the known `PathConflict` objects for that pair.
4. As soon as one conflict is found, stop checking.
5. If no conflict was found, add the candidate to `self.chosen_paths`.

The two `break` statements are intentional:

- the first stops searching the remaining conflict objects;
- the second stops comparing the candidate against other chosen paths.

Once one conflict is found, that candidate cannot belong to the current mutually non-conflicting set.

---

## 8. Test result

We tested a map that produced these routes:

```text
P1:
start -> end
cost 1

P2:
start -> B -> end
cost 3

P3:
start -> A -> C -> end
cost 3

P4:
start -> A -> C -> E -> end
cost 4
```

Conflict detection found that P3 and P4 share:

```text
A
C
```

The resulting chosen set was:

```text
P1: start -> end
P2: start -> B -> end
P3: start -> A -> C -> end
```

P4 was rejected because it conflicts with P3.

This confirmed that the basic conflict detection and greedy non-conflicting selection are working as intended.

---

## 9. Why non-conflicting paths are useful

Our current strategy is to concentrate first on paths that do not share intermediate zones.

The reason is that independent paths are much easier to use simultaneously.

For example:

```text
P1: START -> A -> B -> END
P2: START -> C -> D -> END
```

can potentially carry drones in parallel without the routes competing for A, B, C, or D.

However, we clarified an important point:

**Non-conflicting paths do not mean that scheduling becomes unnecessary.**

The final simulation still has to respect:

- zone capacities;
- connection capacities;
- multiple drones using the same path;
- restricted-zone two-turn movements;
- simultaneous movement rules.

Non-conflicting paths simply reduce interactions between different routes.

---

## 10. Conflicting paths are not bad paths

We should NOT permanently discard every conflicting route.

Example:

```text
P1: START -> A -> B -> END
P2: START -> A -> E -> END
```

These paths conflict at A.

That does not automatically make P2 useless.

Later, P2 may still be usable if:

- A has capacity greater than one;
- drones enter A on different turns;
- scheduling avoids collisions;
- using the additional route improves total fleet throughput.

Therefore our long-term concept is approximately:

```text
ALL PATHS
    |
    v
sort / evaluate
    |
    v
detect conflicts
    |
    +----------------------+
    |                      |
    v                      v
easy independent       overlapping /
path combinations      conflicting paths
    |                      |
    |                      v
    |                 evaluate whether
    |                 scheduling makes
    |                 them useful
    |                      |
    +----------+-----------+
               |
               v
         selected routes
               |
               v
            scheduler
               |
               v
       turn-by-turn movement
```

---

## 11. Important limitation of the current greedy algorithm

Our current `find_best_paths()` does **not yet guarantee the globally best path set**.

Consider:

```text
P1 cost 2
P2 cost 3
P3 cost 3
```

Suppose:

```text
P1 conflicts with P2
P1 conflicts with P3

P2 does NOT conflict with P3
```

The current greedy algorithm sees P1 first because it is cheapest.

It produces:

```text
[P1]
```

But another possible set is:

```text
[P2, P3]
```

For a large number of drones, two slightly longer independent routes could deliver the entire fleet faster than one very short route.

Therefore:

```text
cheapest individual path
```

is not necessarily the same thing as:

```text
best path combination for the whole fleet
```

This is one of the main optimization problems we will address later.

For now, our current algorithm should be understood as:

> Find one cheap mutually non-conflicting path set.

It is a useful baseline, not the final optimization algorithm.

---

# Strategy for the next stages

## Stage 1 — Keep the current greedy selector as a baseline

Do not overcomplicate `find_best_paths()` immediately.

We now have a working first strategy that can:

- find routes;
- calculate their costs;
- detect overlaps;
- create a cheap non-conflicting set.

This gives us something concrete to test future improvements against.

---

## Stage 2 — Understand path throughput

Next we need to stop thinking only about the cost of one drone.

We need to ask:

> Given N drones, how efficiently can this path deliver them?

For example, compare:

```text
Option A:
one path with cost 2

Option B:
two independent paths with cost 3 each
```

With one drone, Option A may obviously be preferable.

With ten drones, Option B may potentially provide better throughput because multiple drones can progress on separate routes simultaneously.

We need to understand this before deciding what the truly best path set is.

---

## Stage 3 — Drone distribution

Once we understand path throughput, determine how many drones should be assigned to each selected route.

Example:

```text
10 drones

P1 cost 3
P2 cost 4
P3 cost 7
```

The correct distribution may not be:

```text
all 10 -> P1
```

and it may not be an equal split either.

The goal is to distribute drones so that the final drone reaches END as early as possible.

---

## Stage 4 — Compare path combinations

After we can estimate the delivery time of a path set, we can improve the current greedy algorithm.

Instead of only asking:

> Which individual path is cheapest?

we can compare combinations:

```text
[P1]

vs.

[P2, P3]

vs.

[P1, P4]

...
```

using the number of drones and estimated total completion turns.

This is where `find_best_paths()` can eventually become a genuine fleet-level optimizer.

We must also keep performance in mind because generating every possible combination may become expensive on large graphs.

---

## Stage 5 — Reconsider conflicting paths

After the easy non-conflicting case works, return to the routes that overlap.

For a conflicting route, investigate:

- which zones are shared;
- each shared zone's `max_drones`;
- when drones would reach the shared zone;
- whether different arrival times eliminate the conflict;
- whether using the route improves total completion time.

The existing `PathConflict.zones` data will become useful here because we already know exactly where two paths overlap.

---

## Stage 6 — Scheduler

The scheduler will work turn by turn.

Its central question will be:

> Which set of drone movements can legally happen during this turn?

It must account for:

- assigned paths;
- current drone positions;
- destination-zone capacity;
- connection capacity;
- drones leaving zones during the same turn;
- restricted-zone movement;
- overlapping routes;
- strategic waiting.

Conceptually:

```text
selected paths
      +
drone assignments
      |
      v
SCHEDULER
      |
      v
TURN 1
    all legal simultaneous movements

TURN 2
    all legal simultaneous movements

TURN 3
    ...
```

---

## Stage 7 — SimulationEngine remains the referee

Keep the architecture boundary established earlier:

```text
PATHFINDER / ROUTING STRATEGY
    decides which routes are useful
    and eventually which route a drone should use

                |
                v

SCHEDULER
    decides what should happen this turn

                |
                v

SIMULATION ENGINE
    validates and executes legal movement
    according to the simulation rules
```

The engine should not become responsible for deciding which route is strategically best.

---

## Stage 8 — Restricted zones and capacities

The final routing/scheduling logic must account for movement costs properly.

A restricted destination requires two turns.

That means a drone may occupy a connection while in transit and must arrive on the following turn.

Later we will need scheduling information such as:

```text
drone
current path
current path position
state
connection in transit
destination
remaining transit turns
```

We should add this only when the simpler normal-zone scheduling works.

---

# Immediate next step

When we continue, do not jump directly into the full scheduler.

The next problem should be:

> **How do we estimate how many turns a set of non-conflicting paths needs to deliver N drones?**

Example to investigate:

```text
5 drones

P1 cost 2
P2 cost 4
```

We should manually simulate/distribute those drones first and derive the logic ourselves.

That will teach us what makes one path combination better than another and give us the information needed to improve `find_best_paths()` without guessing.

---

## Current checkpoint

At the end of today we have:

```text
[✓] Discover all complete paths
[✓] Avoid blocked zones
[✓] Avoid loops inside a path
[✓] Calculate path cost
[✓] Calculate path moves
[✓] Sort paths by cost
[✓] Detect shared intermediate zones
[✓] Store conflicts as PathConflict objects
[✓] Check PathConflict pairs independent of order
[✓] Build one greedy non-conflicting path set
[✓] Store result in self.chosen_paths
[✓] Handle the no-path case

[ ] Evaluate throughput for multiple drones
[ ] Distribute drones between paths
[ ] Compare alternative path sets
[ ] Reintroduce useful conflicting paths
[ ] Schedule simultaneous movements
[ ] Handle capacities during scheduling
[ ] Handle restricted two-turn movement
[ ] Optimize total simulation turns
```

The key idea to carry into the next session is:

> **We are not optimizing the shortest route for one drone. We are optimizing how quickly the entire fleet reaches END.**
