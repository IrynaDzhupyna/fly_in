# we got graph from parser
# now we need to initialize the simulation engine with this graph

class SimulationEngine:
    """ Simulation engine for running drone simulations.
        Referee not strategist:
        - turn counter
        - the current occupancy of each zone and connection
        - in-transit state of restricted zones moves
        - which drones have been delivered"""
    def __init__(self, graph):
        self.graph = graph

    def run(self):
        # Placeholder for simulation logic
        print("Running simulation with the following graph:")
        print(f"Zones: {len(self.graph.zones)}")
        print(f"Connections: {len(self.graph.connections)}")
        print(f"Start Zone: {self.graph.start.name}")
        print(f"End Zone: {self.graph.end.name}")
