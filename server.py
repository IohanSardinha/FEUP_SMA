from DataInitializer import busData, gridResolution, busNetwork
from Model import BusNetworkModel
from Bus import STATE
import mesa

def busPortrail(agent):

    if agent.state == STATE.IN_STOP:
        color = "red"
        text_color = "black"
    elif agent.state == STATE.BETWEEN_STOPS:
        color = "black"
        text_color = "white"
    else:
        color = "green"
        text_color = "blackc"

    portrayal = {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "Layer": 1,
        "r": 0.5,
        "text": agent.line,
        "text_color": text_color

    }
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

model_params = {
    "busData": busData,
    "gridRes": gridResolution,
    "network": busNetwork
}

server = mesa.visualization.ModularServer(
    BusNetworkModel, [grid], "Bus Network Model", model_params
)
server.port = 8521
server.launch()
