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

    def get_avg_speed(self):
        dt = max(self.schedule.schedule[self.scheduleIndex+1][1] - self.model.schedule.steps,1)
        speed=  self.currentConnection.length/dt
        print("--->",self.line,dt, speed)
        return speed
    def get_schedule(self):
        return self.schedule.schedule[self.scheduleIndex+1][1] - 1
    
    def get_ETA(self):
        if self.state == STATE.BETWEEN_STOPS:
            return self.model.schedule.steps + ((1-self.progressInConnection)*self.currentConnection.length)/self.speed
        
        return self.model.schedule.steps + (self.currentConnection.length/self.get_avg_speed())
    

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
        
        self.speed = min(self.currentConnection.speedLimit, self.get_avg_speed())

        newPosition = self.midlle_point(self.currentConnection._from.x, self.currentConnection.to.x, self.currentConnection._from.y, self.currentConnection.to.y)
        self.model.grid.move_agent(self, newPosition)

        self.keep_speed()

    def arrived(self):
        print("arrived")
        self.state = STATE.IN_STOP
        self.lastStop = self.currentConnection.to
        self.scheduleIndex += 1 

        if self.scheduleIndex + 2 > len(self.schedule.schedule):
            self.state = STATE.FINISHED
            self.model.grid.move_agent(self, (self.lastStop.x, self.lastStop.y))
            self.model.schedule.remove(self)
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
        print(f"keep_speed {self.progressInConnection}")
        if self.progressInConnection >= 1:
            self.arrived()

    def step(self):
        ETA = self.get_ETA()
        ScheduledTime = self.get_schedule()
        print(f"{str(self)}, ETA: {ETA}, ScheduledTime: {ScheduledTime}")
        match self.state:
            case STATE.BETWEEN_STOPS:
                if self.progressInConnection >= 1:
                    self.arrived()
                elif ETA > ScheduledTime:
                    self.accelerate(10)
                elif ETA < ScheduledTime:
                    self.decelerate(10)
                else:
                    self.keep_speed()

            case STATE.IN_STOP:
                if ETA >= ScheduledTime:
                    self.start_trip()
                else:
                    self.wait()

