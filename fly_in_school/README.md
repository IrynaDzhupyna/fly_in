This project has been created as part
of the 42 curriculum by <irdzhupy>

# Fly-In

Fly-in is a system that efficiently routes a fleet of drones from central base (start) to a target location (end), while navigating this dynamic network under a set of strict constains and optimization goals.

Table of Contents
1. Description
    - Architecture & Design
2. Instructions
3. Usage Example
4. Resources

## Description

The main objective is to move all drones from the start zone to the end in the fewest possible simulation turns.

The constraints:
- No Graph Libraries
- 100% Object-Oriented
- Typesafe

### Architecture & Design

This project has modular, decoupled object-oriented architecture. It allows to isolate changes in one component from affecting others, making it is easier to modify, replace or extend parts.

**parser.py**
#### Responsibilities:
- check if all zones have unique names
- checks if all coordinates are integers
- check if all zones in connections are known
- checks if no duplicates in connections

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

## Resources
- [gitignore](https://git-scm.com/docs/gitignore)
- [README manual](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

