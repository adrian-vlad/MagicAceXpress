
import config
import officers.Agent


class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant = None):
        super().__init__(name, warrant)

        nick1 = config.topic_name_officer_get("first_client", "nick1")
        nick2 = config.topic_name_officer_get("first_client", "nick2")
        nick3 = config.topic_name_officer_get("first_client", "nick3")
        nick4 = config.topic_name_officer_get("first_client", "nick4")

        def message_cb(topic, message):
            if topic == nick3:
                self._mqtt_client.publish(nick2, message)
            if topic == nick4:
                self._mqtt_client.publish(nick1, message)

        self._mqtt_topics.append(nick3)
        self._mqtt_topics.append(nick4)
        self.message_cb = message_cb
