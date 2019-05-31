import json
import logging

import config
import officers.Agent

from db import Reader


l = logging.getLogger(__name__)
HEARTBEAT_1_MINUTE = "headquarters/syncro1m"


class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant = None):
        super().__init__(name, warrant)

        # listen for heartbeat
        self._mqtt_topics.append(HEARTBEAT_1_MINUTE)

        # check for all the vitals
        self._mqtt_topics.append(config.topic_name_agent_status_get("+", "+"))

        self._vitals = {}
        self._is_first = True

        def message_cb(topic, message):
            if topic == HEARTBEAT_1_MINUTE:
                if self._is_first:
                    # delay the check
                    self._is_first = False
                    return

                # go through all the recorded agents and ask them their message status
                agents = []
                with Reader(config.DB_PATH) as db_read:
                    agents = db_read.read((
                        "SELECT Station, Name, Duty, Warrant "
                        "FROM Agents "
                    ))
                for agent in agents:
                    agent_status_topic_name = config.topic_name_agent_status_get(agent[0], agent[1])

                    # check previous status
                    status = self._vitals.get(agent_status_topic_name, "0")
                    if status != "1":
                        l.warn("Agent {0}/{1} is not alive".format(agent[0], agent[1]))

                        # try to revive the agent
                        dispatcher_topic_name = config.topic_name_officer_get(config.station_name_get(), "dispatcher")
                        data = {"station": agent[0], "name": agent[1], "duty": agent[2], "warrant": json.loads(agent[3])}
                        self._mqtt_client.publish(dispatcher_topic_name, json.dumps(data))

                    # ask for the current one
                    self._mqtt_client.publish(agent_status_topic_name, "s")

                # reset the vitals
                self._vitals = {}
            else:
                if message != "s":
                    # someone's status
                    self._vitals[topic] = message

        self.message_cb = message_cb
