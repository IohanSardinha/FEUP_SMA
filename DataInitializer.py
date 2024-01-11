from Network import *
from Bus import *
import pandas as pd

def LoadData(stopsFile="data/stops.csv", connectionsFile="data/connections.csv", linesFile="data/lines.csv"):

    stopsDF = pd.read_csv(stopsFile)
    stops = []
    for _, stop in stopsDF.iterrows():
        stops.append(Stop(stop["id"], stop["x"], stop["y"]))

    connectionsDF = pd.read_csv(connectionsFile)
    connections = []
    for _, connection in connectionsDF.iterrows():
        _from = [stop for stop in stops if stop.id == connection["from"]][0]
        to = [stop for stop in stops if stop.id == connection["to"]][0]
        connections.append(Connection(_from, to, connection["speed_limit"], connection["length"]))

    busNetwork =  Network(connections)

    linesDF = pd.read_csv(linesFile)
    linesNames = linesDF["line"].unique()
    busData = []
    for lineName in linesNames:
        lineDF = linesDF[linesDF["line"] == lineName].sort_values(by="time")
        schedule = []
        for _, stop_time in lineDF.iterrows():
            stop = [stop for stop in stops if stop.id == stop_time["stop"]][0]
            schedule.append((stop, stop_time["time"]))
        busData.append({
            "line":lineName,
            "schedule":Schedule(schedule)
        })

    gridResolution = [max([connection._from.x for connection in connections])+1, max([connection._from.y for connection in connections])+1]
    
    return busData, busNetwork, gridResolution