from typing import Any
from mesa import Model
import mesa
from Bus import Bus, ACTIONS_S1, ACTIONS_S2
from DataInitializer import LoadData
from Config import *
from QLearning import Qlearning
from Helper import debug
import pandas as pd
from matplotlib import pyplot as plt

class BusNetworkModel(Model):
    def __init__(self, busData, gridRes, network, agentsQLearnings) -> None:
        self.num_agents = len(busData)
        self.grid = mesa.space.MultiGrid(gridRes[0], gridRes[1], False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.network = network
        self.agents = []
        self.max_steps = MAX_STEPS_PER_EPISODE

        for i, busInfo in enumerate(busData):
            busSchedule = busInfo["schedule"] 
            bus = Bus(i, self, busInfo["line"], busSchedule, agentsQLearnings[busInfo["line"]])
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
        debug("",1)
        debug("",1)
        debug(f"-----Step {self.schedule.steps}--------------------------------------------------------",1)
        self.datacollector.collect(self)
        self.schedule.step()
        if len(self.schedule.agents) < 1 or self.schedule.steps >= self.max_steps:
            self.running = False

def main(scenario = 1):
    busData, busNetwork, gridResolution = LoadData(f"data/scenario{scenario}/stops.csv",f"data/scenario{scenario}/connections.csv", f"data/scenario{scenario}/lines.csv")
    agentsQLearnings = {busInfo["line"]:Qlearning(MAX_STEPS_PER_EPISODE*2, max(len(ACTIONS_S1), len(ACTIONS_S2)))  for busInfo in busData}
    for qlearning in agentsQLearnings.values():
        qlearning.initialize_q_table()

    rewards = {busInfo["line"]:[] for busInfo in busData}

    model = None

    for episode_n in range(N_EPISODES):
        
        debug(f"{(episode_n/N_EPISODES)*100}%")
        
        for qlearning in agentsQLearnings.values():
            qlearning.update_episolon(episode_n)

        model = BusNetworkModel(busData, gridResolution, busNetwork, agentsQLearnings)
        for _ in range(MAX_STEPS_PER_EPISODE):
            model.step()
            if model.running == False:
                break
        
        for reward in rewards.keys():
            table = agentsQLearnings[reward].Qtable
            sum_rewards = sum([max(row) for row in table])
            rewards[reward].append(sum_rewards)

    debug(list(agentsQLearnings.values())[0].epsilon)

    for qlearning in agentsQLearnings.values():
        debug(qlearning.Qtable, 3)

    for name,lst in rewards.items():
        plt.plot(range(len(lst)), lst)
        plt.title(name)
        plt.show()

    for bus in model.agents:
        schedule = pd.DataFrame([(stop.id, time) for stop, time in bus.schedule.schedule])
        history = pd.DataFrame(bus.history)
        history = pd.merge(schedule, history, on=1, how="outer")
        history = history.fillna("-").sort_values(by=1).rename(columns={"0_x":"schedule", 1:"time", "0_y":"history"}).reset_index(drop=True)
        
        history.to_csv(f"./output/{bus.line}_history.csv", index=False)

    return agentsQLearnings

if __name__ == "__main__":
    main(1)
