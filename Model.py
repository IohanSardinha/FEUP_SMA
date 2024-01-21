from typing import Any
from mesa import Model
import mesa
from Bus import Bus
from DataInitializer import LoadData
import pandas as pd

class BusNetworkModel(Model):
    def __init__(self, busData, gridRes, network) -> None:
        self.num_agents = len(busData)
        self.grid = mesa.space.MultiGrid(gridRes[0], gridRes[1], False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.network = network
        self.agents = []

        for i, busInfo in enumerate(busData):
            busSchedule = busInfo["schedule"] 
            bus = Bus(i, self, busInfo["line"], busSchedule)
            self.schedule.add(bus)
            self.grid.place_agent(bus, (busSchedule.schedule[0][0].x, busSchedule.schedule[0][0].y))
            self.agents.append(bus)

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


def main(scenario=1):
    busData, busNetwork, gridResolution = LoadData(f"data/scenario{scenario}/stops.csv",f"data/scenario{scenario}/connections.csv", f"data/scenario{scenario}/lines.csv")
    model = BusNetworkModel(busData, gridResolution, busNetwork)

    steps = 0
    while model.running:
        print(steps)
        model.step()
        steps += 1

    for bus in model.agents:
        schedule = pd.DataFrame([(stop.id, time) for stop, time in bus.schedule.schedule])
        history = pd.DataFrame(bus.history)
        history = pd.merge(schedule, history, on=1, how="outer")
        history = history.fillna("-").sort_values(by=1).rename(columns={"0_x":"schedule", 1:"time", "0_y":"history"}).reset_index(drop=True)
        
        history.to_csv(f"./output/scenario{scenario}/{bus.line}_history.csv", index=False) 

if __name__ == "__main__":
    for i in range(1,4):
        main(i)