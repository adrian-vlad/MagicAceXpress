import json
import logging

import config
import officers.Agent
from db import Writer


l = logging.getLogger(__name__)


class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        def message_cb(topic, message):
            try:
                data = json.loads(message)

                # station, name, duty, warrant
                station = data.get("station", None)
                name = data.get("name", None)
                duty = data.get("duty", None)
                warrant = data.get("warrant", None)

                if station is None or name is None:
                    raise Exception("Invalid message: {0}".format(message))

                # TODO: check if station is valid
                # TODO: check if duty is valid
                # TODO: check if warrant is valid

                # send the message to the specified station
                station_topic = config.topic_name_station_get(station)
                del data["station"]
                self._publish(station_topic, json.dumps(data))

                # remove the agent that the station should call back
                with Writer(config.DB_PATH) as db_write:
                    db_write.write((
                        "DELETE FROM Agents "
                        "WHERE (Station = ?) "
                        "AND (Name = ?) "
                    ), parameters=(station, name))
                if duty is not None:
                    # save the agent that the station should dispatch
                    with Writer(config.DB_PATH) as db_write:
                        db_write.write((
                            "INSERT INTO Agents (Station, Name, Duty, Warrant) "
                            "VALUES (?, ?, ?, ?)"
                        ), parameters=(station, name, duty, json.dumps(warrant)))

            except Exception as e:
                l.error("Unable to process message '{0}': {1}".format(message, str(e)))

        self.message_cb = message_cb
        self._mqtt_topics.append(config.topic_name_officer_get(config.station_name_get(), "dispatcher"))

    def _publish(self, topic_name, message):
        self._mqtt_client.publish(topic_name, str(message))
