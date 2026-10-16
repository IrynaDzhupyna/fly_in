*This project has been created as part of the 42 curriculum by irdzhupy.*

# Fly-In

## Description

Fly-in routes a fleet of drones from a start zone to an end zone through a
network of connected zones, in the **fewest possible simulation turns**,
while respecting every movement and capacity rule:

- a zone holds at most `max_drones` drones (1 by default; start and end
  zones are unlimited);
- a connection carries at most `max_link_capacity` drones per turn;
- entering a **restricted** zone takes 2 turns (one on the connection, one
  to arrive), and a drone may never wait on a connection;
- **blocked** zones can never be entered, **priority** zones are preferred.

The program reads a map file, plans every drone's moves, prints the moves
turn by turn, and shows the simulation in a graphical window.

Constraints from the subject: no graph libraries, fully object-oriented,
type-safe (flake8 + mypy clean).

## Instructions

### Requirements

- Python 3.10 or later
- [Poetry](https://python-poetry.org/) (installed automatically by `make install`
  if [pipx](https://pipx.pypa.io/) is available)

### Installation

```
git clone <repository> fly_in
cd fly_in
make install
```

### Running

| Command | What it does |
| --- | --- |
| `make run` | opens the interactive menu (choose a map, run it, open the visual) |
| `make map MAP=maps/hard/02_capacity_hell.txt` | runs one map: prints the simulation, then opens the window |
| `make easy` / `make medium` / `make hard` / `make chal` | runs one example map of that level |
| `python3 fly_in.py <map_file>` | same as `make map`, without make |
| `make test` | runs all tests |
| `make lint` | flake8 + mypy with the subject's flags |
| `make clean` | removes caches |

## Algorithm and implementation strategy

The program is a pipeline of small classes, each with one job:

```
map file -> Parser -> Graph -> PathFinder -> Scheduler -> SimulationEngine -> output / Visualizer
```

### 1. Parser (`parser.py`)

Reads and validates the map line by line and builds a `Graph` of `Zone` and
`Connection` objects. Any error stops the program with the line number and
the cause (for example `Error: Line 4: 'max_drones' must be an integer`).

### 2. PathFinder + A* (`path_finder.py`, `algorithm.py`)

Finds the **candidate routes**: the 40 cheapest simple paths from start to
end, cheapest first. The cost of a path is the number of turns a drone needs
to fly it without waiting (1 per normal/priority zone, 2 per restricted zone).

The search is **A\*** where the search state is a whole partial path, so the
same zone can appear in several different paths:

- **heuristic**: the number of moves from a zone to the end, computed once
  with a reverse BFS. Every move costs at least one turn, so the heuristic
  never overestimates and paths come out in increasing cost order. Map
  coordinates are not used, because two zones far apart on the map may be one
  move apart.
- **tie-break**: between equal costs, the path with more priority zones wins.
- blocked zones and zones that cannot reach the end are skipped, and a path
  never visits the same zone twice.

**Classic A*** finds the optimal route and stops
**AStar** remembers not only zones but the entire journey so far.

**heapq** can give back the smallest item. 
For cost it is what we want but if two zones have the same cost we need to choose the best path by max priority zones, so heapq will not work so to trick it we will treat each add every priority zone as -1 and the biggest negative number wins.

**cheapest_first()**
uses moves_from_start() to get excess to all zones distances from end to zone.

candidates is a list of CandidatePath which starts from start and then 

### 3. Scheduler (`scheduler.py`): the core

Before drone moves, it reserves the places and connections it will need at specific turn.

Deciding drone by drone at every turn makes drones wait for zones that
would actually be free by the time they arrive. Instead, the Scheduler
plans the **complete timetable of every drone before the simulation
starts**, with a **reservation table**:

- the table stores, for every turn, how many drones are in each zone at
  the end of the turn and how many use each connection during the turn;
- drones are planned one after another. For each drone and each candidate
  path, the scheduler tries a start delay `d = 0, 1, 2, ...`: the drone waits
  `d` turns in the start zone, then flies the path without stopping;
- every step of that timetable is checked against the table (zone capacity
  at the end of the turn, connection capacity during the turn). The first
  delay that fits is kept;
- among all paths, the timetable that reaches the end **earliest** wins
  (tie: more priority zones, then the cheaper path). Its steps are booked in
  the table, and the next drone plans around them.

**Why this is optimal on the shipped maps:** drones naturally follow each
other one turn apart (a "convoy"). Drone 2 enters every zone exactly on the
turn drone 1 leaves it, which the subject allows ("a space vacated this turn
is available in the same turn"). Through a bottleneck that lets one drone
pass per turn, one drone reaches the end every turn. Spreading drones over
several paths fills parallel routes the same way.

**Why every move is legal:** a timetable is only accepted if every zone and
connection stays within capacity at every turn, and restricted zones are
always entered as "connection turn, then arrival turn".

**Why it can never get stuck (no deadlock):** the start zone has no
capacity limit, so a drone can always wait there; once all earlier drones
are finished, nothing blocks it any more. Drones never wait in the middle
of the network, so two drones can never block each other.

### 4. SimulationEngine (`simulation_engine.py`)

Plays the timetables turn by turn. In each turn every moving drone first
leaves its zone or connection, then every drone takes its new place, so moves
are simultaneous. The engine keeps `Drone`, `Zone` and `Connection` objects up
to date for the visual, and after each turn it double-checks that no zone
holds too many drones (a safety net that raises `EngineError`).

### Results on the shipped maps

| Map | Turns | Optimum |
| --- | --- | --- |
| easy 01 linear path | 4 | 4 |
| easy 02 simple fork | 4 | 4 |
| easy 03 basic capacity | 4 | 4 |
| medium 01 dead end trap | 8 | 8 |
| medium 02 circular loop | 10 | 10 |
| medium 03 priority puzzle | 6 | 6 |
| hard 01 maze nightmare | 13 | 13 |
| hard 02 capacity hell | 16 | 16 |
| hard 03 ultimate challenge | 26 | 26 |
| challenger: the impossible dream | 43 | 43 |

## Example

Input (`maps/easy/01_linear_path.txt`):

```
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Output (one line per turn):

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

Restricted zones (`custom_maps/restricted_chain.txt`): `D1-start-r1` means
D1 is on the connection `start-r1`, and arrives in `r1` on the next turn.
The next drone starts crossing the same connection on that arrival turn:

```
D1-start-r1
D1-r1 D2-start-r1
D1-r1-r2 D2-r1 D3-start-r1
...
```

## Visual representation

The simulation is shown in an [Arcade](https://api.arcade.academy/) window:

- **zones** are circles in the colour given in the map file (unknown colours
  fall back to yellow), with their name above them;
- **drones** are white labels `D1`, `D2`, ... drawn inside their zone; a drone
  that is crossing towards a restricted zone is drawn halfway along the
  connection, so the 2-turn move is visible;
- the number next to each zone shows how many drones are in it;
- the top of the window shows the **turn counter** (`Turn 5 / 10`, playing,
  paused or finished) and the moves of the last turn, in the same format as
  the terminal output;
- **keys**: `SPACE` play/pause (one turn per second), `RIGHT` one turn
  forward, `ESC` close.

This makes the parts of the simulation that are hard to read in text easy to
follow: where drones queue, how restricted zones take two turns, and how
several routes are used at the same time.

## Tests

`make test` runs:

- `tests/test_parser.py`, `test_zone.py`, `test_connection.py`: map parsing
  and the basic classes;
- `tests/test_scheduler.py`: small hand-made maps (single-file column,
  restricted zones, link and zone capacity, parallel paths, priority tie-break);
- `tests/test_maps.py`: every shipped and custom map through the whole
  program. The output is checked by an **independent rule checker**
  (`tests/output_rules.py`) that shares no code with the scheduler or the
  engine, and the number of turns must equal the optimum;
- `custom_maps/error_*.txt`: broken maps must stop with one clear error line.

## Project structure

```
fly_in.py            entry point: menu or one map file
menu.py              interactive terminal menu
parser.py            map file -> Graph
graph.py zone.py connection.py drone.py   data model
path.py              Path: one route and its cost
algorithm.py         A* search: cheapest paths
path_finder.py       candidate paths for the scheduler
scheduler.py         timetables + reservation table
simulation_engine.py plays the timetables turn by turn
visual.py            Arcade window
maps/                maps shipped with the subject
custom_maps/         our own edge-case maps (error_* = must fail cleanly)
tests/               pytest tests and the output rule checker
```

## Resources

- [A* search algorithm (Wikipedia)](https://en.wikipedia.org/wiki/A*_search_algorithm)
- Hart, Nilsson, Raphael, *A Formal Basis for the Heuristic Determination of
  Minimum Cost Paths* (1968): the original A* paper
- [Red Blob Games: Introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- D. Silver, *Cooperative Pathfinding* (2005): planning several agents with a
  reservation table, the idea behind the scheduler
- [Multi-agent pathfinding (Wikipedia)](https://en.wikipedia.org/wiki/Multi-agent_pathfinding)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Arcade documentation](https://api.arcade.academy/)
- [mypy documentation](https://mypy.readthedocs.io/), [flake8 documentation](https://flake8.pycqa.org/)

### How AI was used

<!-- TODO irdzhupy: check this section and rewrite it in your own words. -->

AI (Claude) was used as a reviewer and assistant during development:

- **project review**: checking the code against the subject, finding rule
  violations in the simulation, and listing what was missing before
  submission;
- **lint**: help fixing flake8 and mypy errors;
- **algorithm design**: discussing the A* heuristic and the reservation-table
  scheduler (`scheduler.py`), and drafting first versions of `algorithm.py`
  and `scheduler.py` that were then reviewed and adapted;
- **testing**: writing the rule checker `tests/output_rules.py` and the map
  tests;
- **documentation**: drafting parts of this README.

All AI-produced code was read, tested, and is understood and explained by the
author.
