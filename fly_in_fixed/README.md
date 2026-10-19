*This project has been created as part of the 42 curriculum by irdzhupy.*

# Fly-in

## Description

Fly-in is a drone-routing simulation. A map describes a network of zones
(hubs) linked by connections. All drones start in the start hub and must
reach the end hub in the **fewest possible simulation turns**, while
respecting every rule of the network:

- each zone holds at most `max_drones` drones (default 1; the start and end
  hubs have no limit);
- each connection carries at most `max_link_capacity` drones per turn
  (default 1);
- zone types change the cost of entering a zone: `normal` and `priority`
  cost 1 turn, `restricted` costs 2 turns (the drone spends one turn on the
  connection and must land on the next one), `blocked` cannot be entered;
- all moves of a turn happen simultaneously, and a place freed during a
  turn can be used in that same turn.

The program parses the map, plans a timetable for every drone, prints the
simulation turn by turn and can replay it in a graphical window.

## Instructions

Requirements: Python 3.10+ and [Poetry](https://python-poetry.org/).

```bash
make install            # install dependencies (pydantic, arcade, flake8, mypy)
make run                # interactive menu: choose a level and a map
make map                # run the default map (maps/easy/01_linear_path.txt)
make map MAP=maps/hard/03_ultimate_challenge.txt
make debug              # run the default map under pdb
make lint               # flake8 + mypy with the flags required by the subject
make lint-strict        # flake8 + mypy --strict
make clean              # remove caches
```

Without Make:

```bash
poetry run python3 fly_in.py                 # menu
poetry run python3 fly_in.py <map_file>      # simulate, then open the window
```

With a map argument the program prints the simulation in the terminal and
then opens the visualization. Exit codes: `0` success, `1` invalid or
unsolvable map, `2` wrong usage.

### Map format

```
nb_drones: 4                                   # must be the first line
start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: roof 2 1 [zone=restricted]                # normal | priority | restricted | blocked
end_hub: goal 3 0 [color=red]
connection: start-junction [max_link_capacity=2]
connection: junction-roof
connection: roof-goal
```

Lines starting with `#` and empty lines are ignored. Any other error stops
the program with the line number and the cause, for example
`Error: Line 3: Invalid zone type: 'lava'`.

## Example

Input, `maps/easy/02_simple_fork.txt` (4 drones):

```
nb_drones: 4
start_hub: start 0 0
hub: junction 1 0 [max_drones=2]
hub: path_a 2 1
hub: path_b 2 -1
end_hub: goal 3 0
connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

Output (4 turns, the optimum):

```
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal
```

A drone flying toward a restricted zone is printed with the connection name
for the first of its two turns (`maps/custom/01_restricted_chain.txt`):

```
D1-s-r1
D1-r1 D2-s-r1
D1-r1-r2 D2-r1 D3-s-r1
D1-r2 D2-r1-r2 D3-r1 D4-s-r1
D1-e D2-r2 D3-r1-r2 D4-r1
D2-e D3-r2 D4-r1-r2
D3-e D4-r2
D4-e
```

## Algorithm choices and implementation strategy

The work is split into three independent steps:

```
Parser -> Graph -> PathFinder (A*) -> Scheduler (reservation table) -> SimulationEngine
```

### 1. Candidate routes: A* (`algorithm.py`, `path_finder.py`)

- The cost of a route is the sum of the costs of the zones it enters
  (1 for normal/priority, 2 for restricted). Blocked zones are skipped.
- The heuristic is the number of hops from a zone to the end, computed once
  with a reverse BFS from the end. Every hop costs at least 1 turn, so the
  heuristic never overestimates and A* returns the cheapest routes first.
  The BFS also removes zones that cannot reach the end at all (dead ends).
- A* does not stop at the first route: it keeps popping the priority queue
  until it has collected `MAX_CANDIDATE_PATHS` (5) loop-free routes, cheapest
  first. Several routes let drones spread out when one route is congested.
- Tie-breaks between candidates with the same estimated cost:
  1. more `priority` zones first (the subject says they should be preferred);
  2. deeper partial routes first, so a map with many equal-cost routes
     (a big grid) finds complete routes quickly instead of exploring them
     breadth-first;
  3. insertion order, so results are the same on every run.
- `MAX_EXPANSIONS` is a safety limit so that no map can make the search run
  forever.

### 2. Timetables: reservation table (`scheduler.py`)

This is the idea of *cooperative pathfinding*: drones are planned one after
another, and every planned drone books the places it will use in a table
indexed by `(place, turn)`.

- For a route and a start delay, `_timeline` builds the drone's moves turn by
  turn. A move into a restricted zone becomes two steps: turn *t* on the
  connection, turn *t+1* in the zone.
- `ReservationTable.fits` checks every step against what earlier drones
  booked: zone occupancy on the arrival turn (`max_drones`, ignored for start
  and end) and connection usage on the crossing turn (`max_link_capacity`).
  A restricted connection is only booked for its first turn, because the
  subject frees it on the turn the drone lands.
- For each drone and each candidate route, the scheduler increases the start
  delay until the timeline fits, then keeps the route with the earliest
  arrival (ties: more priority zones, then the cheaper route).
- Drones only wait in the start hub (unlimited capacity). After take-off a
  drone never stops, so it is in a zone exactly on the turn it arrives there,
  and checking that one turn is enough to guarantee the capacity rules.
  Because every drone is booked before the next one is planned, two drones
  can never deadlock.

Planning everything up front means the turn-by-turn rules (simultaneous
moves, space freed in the same turn) are satisfied by construction: a zone
is counted as occupied only by the drones that are in it at the end of the
turn.

### 3. Replay (`simulation_engine.py`)

The engine replays the timetables one turn at a time. It first removes every
moving drone from its old place, then puts it in the new one (simultaneous
moves), prints one line of moves per turn, and checks after each turn that no
zone holds more drones than allowed. A drone that reaches the end is marked
delivered and no longer moves.

### Results on the provided maps

| Map | Drones | Turns | Optimum |
| --- | --- | --- | --- |
| easy/01 linear path | 2 | 4 | 4 |
| easy/02 simple fork | 4 | 4 | 4 |
| easy/03 basic capacity | 4 | 4 | 4 |
| medium/01 dead end trap | 5 | 8 | 8 |
| medium/02 circular loop | 6 | 10 | 10 |
| medium/03 priority puzzle | 5 | 6 | 6 |
| hard/01 maze nightmare | 8 | 13 | 13 |
| hard/02 capacity hell | 12 | 16 | 16 |
| hard/03 ultimate challenge | 15 | 26 | 26 |
| challenger/01 the impossible dream | 25 | 43 | 43 |

Every map is solved in under a second.

## Visual representation

The visualization uses [Arcade](https://api.arcade.academy/). It opens after
the terminal output, or from option 2 of the menu.

- Zones are drawn as circles in the colour given in the map (yellow when no
  colour is given) with their name, and connections as lines.
- The map is scaled separately on X and Y to fill the window, so a long flat
  map like the challenger stays readable; circles and labels shrink when
  zones are close together.
- Every drone is a `D<ID>` label inside its zone; a drone flying toward a
  restricted zone is drawn halfway along its connection.
- Each zone shows how many drones it holds. On crowded maps only one label
  per zone is drawn and the counter shows the rest.
- The top of the window shows the current turn, the total number of turns,
  the state (playing, paused, finished) and the moves of the last turn,
  exactly as printed in the terminal.
- Controls: `SPACE` play/pause (one turn per second), `RIGHT` next turn,
  `ESC` close the window.

Seeing the drones move makes it easy to check the rules visually: queues in
front of capacity-1 zones, drones splitting across parallel routes, and the
extra turn spent on restricted connections.

## Resources

- [A* search algorithm, Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Introduction to A*, Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- David Silver, *Cooperative Pathfinding* (AIIDE 2005), the reservation
  table approach used by the scheduler
- [Breadth-first search, Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `heapq`](https://docs.python.org/3/library/heapq.html) and
  [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) documentation
- [Arcade documentation](https://api.arcade.academy/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [mypy](https://mypy.readthedocs.io/) and [flake8](https://flake8.pycqa.org/) documentation

### How AI was used

Claude (Anthropic) was used as a reviewer and assistant:

- reviewing the code against the subject and listing what was missing;
- finding bugs after the move to the A* + scheduler design (typos, a missing
  `main()` call, link capacity not checked for normal moves) and fixing them;
- writing an independent checker that replays the printed output against the
  subject rules, plus edge-case maps (large grid, disconnected graph,
  restricted chain, invalid files);
- drafting this README.

The overall architecture (parser, graph model, A*, reservation-table
scheduler, engine and visualization) was designed and written by me. Every
AI-suggested change was read, tested and understood before it was kept.
