# Fly-In --- Progress Summary and Next Steps

## Current focus

We are cleaning and stabilizing the advanced pathfinder before
connecting it to the simulation engine.

The current design separates these concepts:

-   `Path`: one discovered route through the graph.
-   `PathAssignment`: one path plus the number of drones assigned to it.
-   `PathSet`: a group of compatible path assignments and their overall
    finishing turn.
-   `PathConflict`: records when two paths share non-start/non-end
    zones.
-   `PathFinderAdv`: discovers paths, detects conflicts, chooses paths,
    and distributes drones.

## What we did today

### 1. Cleaned `PathAssignment`

Originally, `PathAssignment` stored `turns` as mutable state and
recalculated it manually during drone distribution.

We changed `turns` into a derived property:

``` python
@dataclass
class PathAssignment:
    path: Path
    drones: int = 0

    @property
    def turns(self) -> int:
        if self.drones == 0:
            return 0

        return self.path.cost + self.drones - 1
```

This means `turns` is no longer manually stored or updated. Whenever
`assignment.turns` is accessed, it is calculated from the current path
cost and number of assigned drones.

### 2. Clarified the finishing-turn formula

For a path with cost `C` and `N` assigned drones:

``` text
finishing turn = C + N - 1
```

The `-1` is necessary because the first drone already finishes after `C`
turns. Every additional drone adds one more finishing turn.

Example for path cost 3:

``` text
1 drone  -> 3 + 1 - 1 = 3
2 drones -> 3 + 2 - 1 = 4
3 drones -> 3 + 3 - 1 = 5
```

### 3. Clarified the temporary allocation calculation

While choosing which path should receive the next drone, we use:

``` python
a.path.cost + a.drones
```

This is the result of asking what the finishing turn would be if one
more drone were added:

``` text
cost + (drones + 1) - 1
= cost + drones
```

We decided not to create a second property such as `next_finish_turn`,
because this calculation is only needed temporarily by the distribution
algorithm.

### 4. Clarified `Path` versus `PathAssignment`

`Path` describes the route itself: zones, cost, and moves.

`PathAssignment` describes how that route is being used: the path,
number of drones, and derived finishing turns.

Therefore the cost is accessed as:

``` python
assignment.path.cost
```

rather than `assignment.cost`.

### 5. Simplified `drones_assignment()`

Because `turns` is now a property, the old manual
recalculation/finalization loops are unnecessary.

The intended cleaned version is:

``` python
def drones_assignment(self) -> list[PathAssignment]:
    assignments: list[PathAssignment] = []

    for path in self.chosen_paths:
        assignment = PathAssignment(path)
        assignments.append(assignment)

    for _ in range(self.graph.nb_drones):
        smallest_assignment = min(
            assignments,
            key=lambda a: a.path.cost + a.drones
        )
        smallest_assignment.drones += 1

    return assignments
```

Important: use `range(self.graph.nb_drones)`, not
`range(1, self.graph.nb_drones)`. No drone has been assigned before this
loop, so the loop must execute exactly once per drone.

## Current cleanup state

Before moving on, make sure the current source contains:

``` python
for _ in range(self.graph.nb_drones):
```

and that the old block assigning directly to `a.turns` has been removed.

Run the existing maps and verify that every drone is assigned, the
assignments add up to `graph.nb_drones`, and `PathSet.finishing_turn`
still produces the expected result.

## What to do next

### Step 1 --- Clean `PathSet`

`PathSet.finishing_turn` is currently stored and calculated in
`__post_init__()`.

This is similar to the old `PathAssignment.turns` design:
`finishing_turn` is derived from `assignments`. Review whether it should
also become a property so it cannot become stale if assignments change.

### Step 2 --- Clean debugging code

Review and eventually remove or relocate temporary output helpers and
commented debugging code:

-   `Path.info_path()`
-   `PathAssignment.info_assignment()`
-   `PathConflict.info_conflict()`
-   `PathFinderAdv.info_paths()`
-   commented-out prints in `find_best_paths()`

### Step 3 --- Revisit path-set selection

The current path selection is greedy: sort paths by cost, choose the
cheapest, then add later paths only if they do not conflict with already
chosen paths.

This can miss a better combination. A cheap path might conflict with two
slightly more expensive paths which, together, move all drones faster.

The next algorithmic milestone is to compare valid non-conflicting path
combinations as `PathSet` candidates and select based on total finishing
turns.

Do not generate combinations just to reject them blindly. Build/search
candidate sets while maintaining mutual compatibility, then evaluate
drone distribution for each valid set.

### Step 4 --- Test path allocation thoroughly

Add maps/tests for:

-   one path only,
-   two independent paths,
-   paths with conflicts,
-   several possible compatible path sets,
-   different path costs,
-   restricted and blocked zones,
-   more drones than paths,
-   one drone,
-   unreachable end,
-   cases where the cheapest individual path is not part of the best
    overall set.

### Step 5 --- Connect the plan to the simulation engine

The pathfinder should be the strategist: it decides which route each
drone should follow.

The simulation engine should remain the referee: it validates and
executes movement according to capacities, blocked zones, movement
costs, and simultaneous-turn rules.

Keep planned routes separate from `Drone.path`, because `Drone.path`
represents the route actually travelled.

### Step 6 --- Finish simulation rules

Complete and verify normal movement, restricted movement, simultaneous
movement, zone and connection conflicts, waiting, delivered drones, turn
processing, and termination.

### Step 7 --- Required output and visualization

Produce the required turn-by-turn movement output and visual feedback.
After the engine and pathfinder are stable, connect the simulation state
to the chosen visualization approach. Arcade remains an option for a
graphical UI, but a simpler compliant visualization can be completed
first if time is tight.

### Step 8 --- Final project pass

Before submission:

-   run `flake8`,
-   run `mypy`,
-   remove obsolete debugging code,
-   handle parser/map errors cleanly,
-   test multiple maps and edge cases,
-   verify output format,
-   document the algorithm and visualization,
-   prepare to explain and modify the code during evaluation.

## Estimated remaining time

This estimate assumes the parser, graph model, zones/connections, and a
substantial part of the simulation engine already exist, while path-set
optimization, integration, full rule testing, visualization, and final
cleanup remain.

  Work                                                 Estimate
  ---------------------------------------------- --------------
  Finish current pathfinder cleanup                      2--3 h
  Correct path-set selection/comparison                  5--8 h
  Pathfinder tests and edge cases                        3--5 h
  Integrate assignments with simulation engine           4--6 h
  Finish/verify movement and conflict rules              5--8 h
  Required output + basic visual feedback                3--5 h
  mypy/flake8, debugging, regression tests               3--5 h
  Documentation and evaluation preparation               2--3 h
  **Total**                                        **27--43 h**

A realistic planning target is about **35 focused hours**.

At roughly 3 focused hours/day, that is about **9--14 working days**. At
5 focused hours/day, about **6--9 working days**. At 7 focused
hours/day, about **4--7 working days**.

The largest uncertainty is path-set optimization plus simultaneous
simulation/conflict handling. If those expose architectural problems,
the project can take longer. If the existing simulation engine is
already close to complete and the visualizer stays simple, the lower end
is achievable.

## Recommended order

``` text
PathAssignment cleanup
        ↓
PathSet cleanup
        ↓
valid path-set selection
        ↓
drone distribution tests
        ↓
pathfinder ↔ simulation integration
        ↓
movement/conflict correctness
        ↓
required textual output
        ↓
visualization
        ↓
lint + typing + final tests + documentation
```

The immediate next task is **`PathSet` cleanup**, followed by fixing the
greedy path-selection limitation.
