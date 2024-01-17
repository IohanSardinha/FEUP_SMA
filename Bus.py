from dataclasses import dataclass

from mesa.model import Model
from Network import Stop
from mesa import Agent
from enum import Enum
from math import sqrt
from QLearning import Qlearning

from Helper import debug

STATE = Enum("STATE", ["BETWEEN_STOPS", "IN_STOP", "FINISHED"])
ACTIONS_S1 = ["ACCELERATE", "DECELERATE", "KEEP_SPEED"]
ACTIONS_S2 = ["WAIT", "START"]

@dataclass
class Schedule:
    schedule: list[tuple]

class Bus(Agent):
    scheduleIndex = 0
    def __init__(self, unique_id: int, model: Model, line: str, schedule: Schedule, qlearning: Qlearning) -> None:
        super().__init__(unique_id, model)
        self.line = line
        self.schedule = schedule
        self.state = STATE.IN_STOP
        self.lastStop = schedule.schedule[0][0]
        self.qlearning = qlearning

        self.currentConnection = self.get_current_connection()
        self.progressInConnection = 0
        self.scheduleIndex = 0
        self.speed = 0

    def __str__(self) -> str:
        return f"""{self.line}, State: {self.state}, last-stop: {self.lastStop}, scheduleIndex: {self.scheduleIndex}, speed: {self.speed}, tripPerc: {self.progressInConnection}"""

    def get_current_connection(self):
        for connection in self.model.network.network:
            if connection._from == self.lastStop and connection.to == self.schedule.schedule[self.scheduleIndex+1][0]:
                return connection
        raise Exception("DID NOT FIND CONNECTION")

    def get_avg_speed(self, connection):
        dt = max(self.schedule.schedule[self.scheduleIndex+1][1] - self.model.schedule.steps,1)
        speed =  connection.length/dt
        debug(f"---> {self.line},{dt}, {speed}", 3)
        return speed
    
    def getConnectionTime(self, connection):
        return connection.length/connection.speedLimit
    
    def getConnectionsUntill(self, stop):
        connections = []
        for i in range(self.scheduleIndex, len(self.schedule.schedule)-1):
            for connection in self.model.network.network:
                if connection._from == self.schedule.schedule[i][0] and connection.to == self.schedule.schedule[i+1][0]:
                    connections.append(connection)
                    break
            if self.schedule.schedule[i+1][0] == stop:
                break
        return connections

    def get_schedule(self):
        return self.schedule.schedule[self.scheduleIndex][1]

    def get_ETA(self, stop):
        now = self.model.schedule.steps
        
        path = self.getConnectionsUntill(stop)

        pathETAs = [self.getConnectionTime(connection) for connection in path]

        if self.state == STATE.BETWEEN_STOPS:
            return now + ((1-self.progressInConnection) * pathETAs[0]) + sum(pathETAs[1:])
        
        return now + sum(pathETAs)
    

    def midlle_point(self, x1,x2, y1, y2):
        x = x2 - x1
        y = y2 - y1
        return (int(x1+x/2), int(y1+y/2))

    def wait(self):
        debug("wait",1)
        pass
        
    def start_trip(self):
        debug("start_trip",1)

        self.state = STATE.BETWEEN_STOPS
        self.progressInConnection = 0
        
        self.speed = self.currentConnection.speedLimit#min(self.currentConnection.speedLimit, self.get_avg_speed(self.currentConnection))

        newPosition = self.midlle_point(self.currentConnection._from.x, self.currentConnection.to.x, self.currentConnection._from.y, self.currentConnection.to.y)
        self.model.grid.move_agent(self, newPosition)

        self.keep_speed()

    def arrived(self):
        debug("arrived",1)
        self.state = STATE.IN_STOP
        self.lastStop = self.currentConnection.to
        self.scheduleIndex += 1 
        self.speed = 0

        if self.scheduleIndex + 2 > len(self.schedule.schedule):
            self.state = STATE.FINISHED
            self.model.grid.move_agent(self, (self.lastStop.x, self.lastStop.y))
            self.model.schedule.remove(self)
            return

        self.currentConnection = self.get_current_connection()

        self.model.grid.move_agent(self, (self.lastStop.x, self.lastStop.y))

    def accelerate(self, increase):
        debug("accelerate",1)
        self.speed = min(self.currentConnection.speedLimit, self.speed + increase)
        self.keep_speed()

    def decelerate(self, decrease):
        debug("decelerate",1)
        self.speed = max(1, self.speed - decrease)
        self.keep_speed()

    def keep_speed(self):
        self.progressInConnection += self.speed/self.currentConnection.length
        debug(f"keep_speed speed: {self.speed} {self.progressInConnection}",1)
        if self.progressInConnection >= 1:
            self.arrived()

    def compute_reward(self, ETA, ScheduledTime):
        x = ScheduledTime - ETA
        c1 = 200
        c2 = 100
        return -x + c1 if x >=0 else x + c2

    def compute_state(self):
        step = self.model.schedule.steps
        return step * 2 if self.state == STATE.BETWEEN_STOPS else step*2 + 1
    
    def advance(self):

        headingStop = self.schedule.schedule[self.scheduleIndex][0]
        ETA = self.get_ETA(headingStop)
        ScheduledTime = self.get_schedule()


        curr_state = self.compute_state()
        match self.state:
            case STATE.BETWEEN_STOPS:
                actionIdx = self.qlearning.epsilon_greedy_policy(curr_state, len(ACTIONS_S1))
                action = ACTIONS_S1[actionIdx]

                match action: 
                    case "ACCELERATE":
                        self.accelerate(10)
                    case "DECELERATE":
                        self.decelerate(10)
                    case "KEEP_SPEED":
                        self.keep_speed()
                    
            case STATE.IN_STOP:
                actionIdx = self.qlearning.epsilon_greedy_policy(curr_state, len(ACTIONS_S2))
                action = ACTIONS_S2[actionIdx]

                match action:
                    case "WAIT":
                        self.wait()
                    case "START":
                        self.start_trip()

        
        # otherAgentsHeadingToSameStop = self.model.getBusesHeadingToStopNow(headingStop)
        # if self in otherAgentsHeadingToSameStop: otherAgentsHeadingToSameStop.remove(self)
        #otherAgentsHeadingToMyStop = self.model.getBusesHeadingToStopNow(self.lastStop)
        #furthestAgentHeadingToStopETA = max([agent.get_ETA(self.lastStop) for agent in otherAgentsHeadingToMyStop]) if len(otherAgentsHeadingToMyStop) > 0 else None
        
        reward = self.compute_reward(ETA, ScheduledTime)
        debug("",1)
        debug(f"> {str(self)},reward: {reward}, ETA: {ETA}, ScheduledTime: {ScheduledTime}, scheduleIndex: {round(self.scheduleIndex, 3)}, action: ", 1, ending="")
        debug(self.qlearning.Qtable[curr_state],1)
        #debug(str([a.line for a in otherAgentsHeadingToMyStop]),3)

        new_state = self.compute_state()
        self.qlearning.update_qtable(curr_state, actionIdx, new_state, reward)
