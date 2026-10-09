This project has been created as part
of the 42 curriculum by <irdzhupy>

# Fly-In

Fly-in is a system that efficiently routes a fleet of drones from central base (start) to a target location (end), while navigating this dynamic network under a set of strict constains and optimization goals.

## Description

Main problem: 
    deliver all drones from start to end in the fewest possible simulation turns while respecting movement constrains.

The main objective is to move all drones from the start zone to the end in the fewest possible simulation turns.

The constraints:
- No Graph Libraries
- 100% Object-Oriented
- Typesafe

### Architecture & Design

This project has modular, decoupled object-oriented architecture. It allows to isolate changes in one component from affecting others, making it is easier to modify, replace or extend parts.

***Algorithm***
It consist of three parts:
- PathFinder - planning and optimization
- MovementCoordinator - coordinates the movement of drones
- SimulationEngine - execuding and scheduling

PathFinder task:
1. Find all possibel paths from start to end
2. Select those that can reduce total finishing time
3. Distribute drones between tham to minin=mize the estimated number of turns

MovementCoordinator
1. Which drones want to move
2. Whether destination zones have capacity
3. Whether connection has capacity
4. Which drone must wait
5. Whether simultanious departure make room for arrivals

How it works:
- it collects all intended movements of all drones
- checks the capacity of zones the all want to move in and if it fine - make move by simulation engine


Simulation engine
1. Assigns drones to the path
2. Checks if the movement are legal
3. Exectes turns one by one
4. Handles the restricted zones movemt
5. Prevent collisions and deadlock
6. Sheduling the movents to shared zones if such appears
7. Calculates the real finishing time
8. Track if all drones have arrived


**Restricted movement**
D1 enters the connection towards B. B zone got a reservation so no other drones can enter this. D1 enters B, reservation is released and + 1 occupant added.

If the next zone is Restricted, we check the connection capacity and move the drone there on next turn. On Turn 3 we move the drone towards the Restricte zone and reduce the occupants the of connection.

if one of drones are on connction toward the zone, other drones should not enter this zone. So we have 'reserved' in zone to book a place for our drone in transit.

## Parser

**parser.py**

The parser reads and validates the input map file and converts it into a `Graph` used by the rest of the program.

It handles:

- `nb_drones` and ensures it is defined first and has a valid positive value.
- Start, end, and regular hub definitions with integer coordinates.
- Unique zone names and required naming restrictions.
- Zone metadata such as `zone`, `color`, and `max_drones`, including default values.
- Connection definitions between previously defined zones.
- Connection metadata such as `max_link_capacity`.
- Duplicate, self-referencing, malformed, or unknown connections.
- Comments and empty lines.
- Metadata fields in any valid order.

Invalid input raises a `ParserError` with the line number and a description of the problem. The parser stops immediately instead of creating a partially valid graph.

The parser is covered by pytest tests for valid input, invalid syntax, metadata, default values, capacities, naming rules, connections, and common edge cases.

**drone.py**
**zone.py**
#### Responsibilities:
- stores its coordinates
**connection**
#### Responsibilities:
- connects Zone A <-> Zone B
**graph**


## Instructions


### Prerequisites

- Python 3.10 or later
- pip

### Installation

The project includes Makefile to automate the setup

```
# Clone the repository
git clone <repository> fly_in
cd fly_in
```

Install project dependencies isolated in a virtual environment

```
make install
```


### Running the Simulator

Run the main script using the defult map :

# CHOOSE DEFAULT MAP LATER

```
make run
```

You can also choose the map from given with rules:
1. **maps/easy/01_linear_path.txt**

```make easy```

2. **maps/medium/01_dead_end_trap.txt**

```make medium```

3. **maps/hard/01_maze_nightmare.txt**

```make hard``` 


<!-- 

### Valid Path
- has start and end zone
- no deadends

## How it works

- detects one all valid paths
- checks if any zone in Path is shared with another Path
- if yes: merge them -->

## Usage Exampe

### Example Input (maps/easy/01_linear_path.txt)

nb_drones: 2

start_hub: start 0 0 [color=green]
end_hub: goal 0 3 [color=yellow]
hub: waypoint1 0 1 [color=blue]
hub: waypoint2 0 2 [color=blue]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal

### Expected Output

D0-<waypoint1>
D0-<waypoint2> D1-<waypoint1>
D0-<goal> D1-<waypoint2>
D0-<goal> D1-<goal>


### Visualization
** visualization.py**
The visualization is done with Arcade.

## Resources
- [gitignore](https://git-scm.com/docs/gitignore)
- [README manual](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
