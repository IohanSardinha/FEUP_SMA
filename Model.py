from typing import Any
from mesa import Model
import mesa
from Bus import Bus, ACTION_S1, ACTION_S2
from DataInitializer import busData, gridResolution, busNetwork
from Config import *
from QLearning import Qlearning

class BusNetworkModel(Model):
    def __init__(self, busData, gridRes, network, agentsQLearnings) -> None:
        self.num_agents = len(busData)
        self.grid = mesa.space.MultiGrid(gridRes[0], gridRes[1], False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.network = network
        self.max_steps = MAX_STEPS_PER_EPISODE

        for i, busInfo in enumerate(busData):
            busSchedule = busInfo["schedule"] 
            bus = Bus(i, self, busInfo["line"], busSchedule, agentsQLearnings[busInfo["line"]])
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
        if len(self.schedule.agents) < 1 or self.schedule.step >= self.max_steps:
            self.running = False

def main():
    agentsQLearnings = {busInfo["line"]:Qlearning(MAX_STEPS_PER_EPISODE*2, max(len(ACTION_S1), len(ACTION_S2)))  for busInfo in busData}
    for qlearning in agentsQLearnings.values():
        qlearning.initialize_q_table()

    for _ in range(N_EPISODES):
        model = BusNetworkModel(busData, gridResolution, busNetwork, agentsQLearnings)
        for _ in MAX_STEPS_PER_EPISODE:
            model.step()
            if model.running == False:
                break

if __name__ == "__main__":
    main()
