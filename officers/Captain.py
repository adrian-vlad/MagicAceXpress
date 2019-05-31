import json
import logging

import config
import officers.Agent


l = logging.getLogger(__name__)


#TODO: resurrect fallen agents
# make reaper send a message
class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant = None):
        super().__init__(name, warrant)

        def message_cb(topic, message):
            try:
                officers.dispatch(json.loads(message))
            except Exception as e:
                l.error("Unable to process message '{0}': {1}".format(message, str(e)))

        self._mqtt_topics.append(config.topic_name_station_get(self._name))
        self.message_cb = message_cb
