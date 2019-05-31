
import config
import officers.Agent


class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        self._mqtt_topic_name = config.topic_name_officer_get(config.station_name_get(), self._name)

    def _publish(self, message):
        self._mqtt_client.publish(self._mqtt_topic_name, str(message))
