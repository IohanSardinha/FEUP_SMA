from dataclasses import dataclass

@dataclass
class Stop:
    id: str
    x: int
    y: int

@dataclass
class Connection:
    _from: Stop
    to:    Stop
    speedLimit: int
    length: int
    capacity: int
    occupancy: int = 0

@dataclass
class Network:
    network: list[Connection]