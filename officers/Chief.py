
import officers
from officers.Captain import Agent as Captain


class Agent(Captain):
    def __init__(self, name, warrant = None):
        super().__init__(name, warrant)

        officers._officer_dispatch("tech1", "Technician", None)
        officers._officer_dispatch("dispatcher", "Dispatcher", None)
        officers._officer_dispatch("syncro1m", "Syncro", 5)
        officers._officer_dispatch("phys", "Physician", None)
