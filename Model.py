from typing import Any
from mesa import Model
import mesa
from Bus import Bus

class BusNetworkModel(Model):
    def __init__(self, busData, gridRes, network) -> None:
        self.num_agents = len(busData)
        self.grid = mesa.space.MultiGrid(gridRes[0], gridRes[1], False)
        self.schedule = mesa.time.RandomActivation(self)
        self.network = network

        for i, busInfo in enumerate(busData):
            busSchedule = busInfo["schedule"] 
            bus = Bus(i, self, busInfo["line"], busSchedule)
            self.schedule.add(bus)
            self.grid.place_agent(bus, (busSchedule.schedule[0][0].x, busSchedule.schedule[0][0].y))

        self.datacollector = mesa.DataCollector()

    def getBusesHeadingToStop(self, stop):
        return [agent for agent in self.schedule.agents if agent.currentConnection.to == stop]

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()