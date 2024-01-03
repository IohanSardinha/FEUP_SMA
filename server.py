from DataInitializer import busData, gridResolution, busNetwork
from Model import BusNetworkModel
from Bus import STATE
import mesa
from math import sin, cos

def busPortrail(agent):

    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 1,
        "r": 0.5,
        "text": agent.line,

    }
    
    if agent.state == STATE.IN_STOP:
        portrayal["Color"] = "red"
        portrayal["text_color"] = "black"
    elif agent.state == STATE.BETWEEN_STOPS:
        portrayal["Color"] = "black"
        portrayal["text_color"] = "white"
    else:
        portrayal["Color"] = "green"
        portrayal["text_color"] = "black"

    agentsInCell = agent.model.grid.get_cell_list_contents([agent.pos])
    if len(agentsInCell) > 1:
        a = ((agentsInCell.index(agent)+1)/len(agentsInCell))*360
        portrayal["r"] = 0.4
        r = 0.7
        portrayal["xAlign"] = cos(a)*r
        portrayal["yAlign"] = sin(a)*r

    
    return portrayal

networkPortrail = {
    "Shape": "circle",
    "Color": "green",
    "Layer": 0,
    "r": 0.5,
    "text_color": "black"
}

networkPoints = []
for connection in busNetwork.network:
    networkPoints.append((connection._from.x,connection._from.y, connection._from.id))
    networkPoints.append((connection.to.x,connection.to.y, connection.to.id))
networkPoints = list(set(networkPoints))

class myGrid(mesa.visualization.CanvasGrid):
    def __init__(self, portrayal_method, grid_width, grid_height, canvas_width=500, canvas_height=500, extra_representations=[]):
        super().__init__(portrayal_method, grid_width, grid_height, canvas_width, canvas_height)
        self.extra_representations = extra_representations

    def render(self, model):
        grid_state =  super().render(model)

        for positions, portrayal in self.extra_representations:
            for position in positions:
                cell = dict(portrayal)
                cell["x"] = position[0]
                cell["y"] = position[1]
                if len(position) > 2:
                    cell["text"] = position[2]
                grid_state[cell["Layer"]].append(cell)

        return grid_state

grid = myGrid(busPortrail, gridResolution[0], gridResolution[1], 500, 500, [(networkPoints, networkPortrail)])

speedViz = mesa.visualization.BarChartModule([{"Label":"speed"}],"agent")

model_params = {
    "busData": busData,
    "gridRes": gridResolution,
    "network": busNetwork
}

server = mesa.visualization.ModularServer(
    BusNetworkModel, [grid, speedViz], "Bus Network Model", model_params
)
server.port = 8521
server.launch()
