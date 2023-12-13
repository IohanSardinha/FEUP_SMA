from Network import *
from Bus import *

s1  = Stop("S01", 0,0)
s2  = Stop("S02", 0,2)
s3  = Stop("S03", 2,2)
s4  = Stop("S04", 2,0)
s5  = Stop("S05", 2,4)
s6  = Stop("S06", 4,4)
s7  = Stop("S07", 4,2)
s8  = Stop("S08", 0,5)
s9  = Stop("S09", 5,5)
s10 = Stop("S10", 5,0)

connections = [
    Connection(s1,  s2, 1100, 1000),
    Connection(s2,  s3, 1100, 1000),
    Connection(s3,  s4, 1100, 1000),
    Connection(s4,  s1, 1100, 1000),
 
    Connection(s3,  s5, 1100, 1000),
    Connection(s5,  s6, 1100, 1000),
    Connection(s6,  s7, 1100, 1000),
    Connection(s7,  s3, 1100, 1000),

    Connection(s3,  s8, 1100, 2000),
    Connection(s8,  s9, 1100, 3000),
    Connection(s9, s10, 1100, 3000),
    Connection(s10, s3, 1100, 2000),
]


busNetwork =  Network(connections)

b1Schedule = [
    (s1, 0 ),
    (s2, 5 ),
    (s3, 10),
    (s4, 15),
    (s1, 20),
    (s2, 25),
    (s3, 30),
    (s4, 35),
    (s1, 40)
]

b2Schedule = [
    (s5, 0 ),
    (s6, 5 ),
    (s7, 10),
    (s3, 15),
    (s5, 20),
    (s6, 25),
    (s7, 30),
    (s3, 35),
    (s5, 40)
]

b3Schedule = [
    (s8,  0 ),
    (s9,  5 ),
    (s10, 10),
    (s3,  15),
    (s8,  20),
    (s9,  25),
    (s10, 30),
    (s3,  35),
    (s8,  40)
]

b1nfo = {
    "line": "B1",
    "schedule": Schedule(b1Schedule)
}

b2nfo = {
    "line": "B2",
    "schedule": Schedule(b2Schedule)
}

b3nfo = {
    "line": "B3",
    "schedule": Schedule(b3Schedule)
}

busData = [b1nfo, b2nfo, b3nfo]

gridResolution = (max([connection._from.x for connection in connections])+1,max([connection._from.y for connection in connections])+1)