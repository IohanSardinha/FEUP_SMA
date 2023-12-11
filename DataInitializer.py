from Network import *
from Bus import *

s1 = Stop("S1", 0,0)
s2 = Stop("S2", 0,2)
s3 = Stop("S3", 2,2)
s4 = Stop("S4", 2,0)
s5 = Stop("S5", 2,4)
s6 = Stop("S6", 4,4)
s7 = Stop("S7", 4,2)

connections = [
    Connection(s1, s2, 120, 1, 99),
    Connection(s2, s3, 120, 1, 99),
    Connection(s3, s4, 120, 1, 99),
    Connection(s4, s1, 120, 1, 99),

    Connection(s3, s5, 120, 1, 99),
    Connection(s5, s6, 120, 1, 99),
    Connection(s6, s7, 120, 1, 99),
    Connection(s7, s3, 120, 1, 99),
]

busNetwork =  Network(connections)

b1Schedule = [
    (s1, 0),
    (s2, 1),
    (s3, 2),
    (s4, 3),
    (s1, 4),
    (s2, 5),
    (s3, 6),
    (s4, 7),
    (s1, 8)
]

b2Schedule = [
    (s5, 0),
    (s6, 1),
    (s7, 2),
    (s3, 3),
    (s5, 4),
    (s6, 5),
    (s7, 6),
    (s3, 7),
    (s5, 8)
]

b1nfo = {
    "line": "B1",
    "schedule": Schedule(b1Schedule)
}

b2nfo = {
    "line": "B2",
    "schedule": Schedule(b2Schedule)
}

busData = [b1nfo, b2nfo]

gridResolution = (10,10)