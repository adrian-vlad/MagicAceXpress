import logging

from officers.Enforcer import Agent as Enforcer


l = logging.getLogger(__name__)


class Agent(Enforcer):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        def message_cb(topic, message):
            l.debug("New message: {0}".format(message))

        self.message_cb = message_cb
