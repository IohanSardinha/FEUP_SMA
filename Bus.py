from dataclasses import dataclass

from mesa.model import Model
from Network import Stop
from mesa import Agent
from enum import Enum
from math import sqrt

STATE = Enum("STATE", ["BETWEEN_STOPS", "IN_STOP", "FINISHED"])

@dataclass
class Schedule:
    schedule: list[tuple]

class Bus(Agent):
    scheduleIndex = 0
    def __init__(self, unique_id: int, model: Model, line: str, schedule: Schedule) -> None:
        super().__init__(unique_id, model)
        self.history = []
        self.line = line
        self.schedule = schedule
        self.state = STATE.IN_STOP
        self.lastStop = schedule.schedule[0][0]

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
        print("--->",self.line,dt, speed)
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
        return self.schedule.schedule[self.scheduleIndex+1][1]

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
        print("wait")
        

    def start_trip(self):
        print("start_trip")

        self.state = STATE.BETWEEN_STOPS
        self.progressInConnection = 0
        
        self.speed = self.currentConnection.speedLimit

        newPosition = self.midlle_point(self.currentConnection._from.x, self.currentConnection.to.x, self.currentConnection._from.y, self.currentConnection.to.y)
        self.model.grid.move_agent(self, newPosition)

        self.keep_speed()

    def arrived(self):
        print("arrived")
        self.state = STATE.IN_STOP
        self.lastStop = self.currentConnection.to
        self.scheduleIndex += 1 
        self.speed = 0

        if self.scheduleIndex + 2 > len(self.schedule.schedule):
            self.state = STATE.FINISHED
            self.model.grid.move_agent(self, (self.lastStop.x, self.lastStop.y))
            self.model.schedule.remove(self)

            history = (self.schedule.schedule[self.scheduleIndex][0].id, self.model.schedule.steps+1)
            self.history.append(history)
            history = ("(FINISH)", self.model.schedule.steps+2)
            self.history.append(history)

            return

        self.currentConnection = self.get_current_connection()

        self.model.grid.move_agent(self, (self.lastStop.x, self.lastStop.y))

    def accelerate(self, increase):
        print("accelerate")
        self.speed = min(self.currentConnection.speedLimit, self.speed + increase)
        self.keep_speed()

    def decelerate(self, decrease):
        print("decelerate")
        self.speed = max(1, self.speed - decrease)
        self.keep_speed()

    def keep_speed(self):
        self.progressInConnection += self.speed/self.currentConnection.length
        print(f"keep_speed speed: {self.speed} {self.progressInConnection}")
        if self.progressInConnection >= 1:
            self.arrived()

    def advance(self):

        history = (self.schedule.schedule[self.scheduleIndex][0].id if self.state == STATE.IN_STOP else "moving", self.model.schedule.steps)
        self.history.append(history)

        headingStop = self.schedule.schedule[self.scheduleIndex+1][0]
        ETA = self.get_ETA(headingStop)
        ScheduledTime = self.get_schedule()
        
        otherAgentsHeadingToMyStop = self.model.getBusesHeadingToStopNow(self.lastStop)
        furthestAgentHeadingToStopETA = max([agent.get_ETA(self.lastStop) for agent in otherAgentsHeadingToMyStop]) if len(otherAgentsHeadingToMyStop) > 0 else None
        print()
        print(f"> {str(self)}, ETA: {ETA}, ScheduledTime: {ScheduledTime}, scheduleIndex: {round(self.scheduleIndex, 3)}, action: ", end="")
        print([a.line for a in otherAgentsHeadingToMyStop])
        match self.state:
            case STATE.BETWEEN_STOPS:
                if ETA + 1 > ScheduledTime:
                    self.accelerate(10)
                elif ETA + 1 < ScheduledTime:
                    self.decelerate(10)
                else:
                    self.keep_speed()

            case STATE.IN_STOP:
                if ETA + 1 < ScheduledTime or (furthestAgentHeadingToStopETA != None and furthestAgentHeadingToStopETA < ETA):
                    self.wait()
                else:
                    self.start_trip()