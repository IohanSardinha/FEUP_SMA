from typing import Any
from mesa import Model
import mesa
from Bus import Bus
from DataInitializer import s3

class BusNetworkModel(Model):
    def __init__(self, busData, gridRes, network) -> None:
        self.num_agents = len(busData)
        self.grid = mesa.space.MultiGrid(gridRes[0], gridRes[1], False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.network = network

        for i, busInfo in enumerate(busData):
            busSchedule = busInfo["schedule"] 
            bus = Bus(i, self, busInfo["line"], busSchedule)
            self.schedule.add(bus)
            self.grid.place_agent(bus, (busSchedule.schedule[0][0].x, busSchedule.schedule[0][0].y))

        self.datacollector = mesa.DataCollector(agent_reporters={"speed":lambda b: b.speed})
        self.datacollector.collect(self)
        self.running = True

    def getBusesHeadingToStopEventually(self, stop):
        agents = []
        for agent in self.schedule.agents:
            for i in range(agent.scheduleIndex + 1, len(agent.schedule.schedule)):
                if agent.schedule.schedule[i][0] == stop:
                    agents.append(agent)
                    break
        return agents
    
    def getBusesHeadingToStopNow(self, stop):
        agents = []
        for agent in self.schedule.agents:
            if agent.currentConnection.to == stop:
                agents.append(agent)
                break
        return agents

    def step(self):
        print()
        print()
        print(f"-----Step {self.schedule.steps}--------------------------------------------------------")
        self.datacollector.collect(self)
        self.schedule.step()
        if len(self.schedule.agents) < 1:
            self.running = False