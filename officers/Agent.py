import signal
import queue
import logging

import config

from messaging import MQTTWrap


l = logging.getLogger(__name__)


class Agent(object):
    def __init__(self, name, warrant):
        self._name = name
        self._warrant = warrant
        self._shutdown = False
        self._messages = queue.Queue()
        self._mqtt_client = None
        self._mqtt_topics = []
        self._mqtt_topic_status = ""
        self.message_cb = None

    def _say_hi(self):
        self._mqtt_client.publish(
            self._mqtt_topic_status,
            "1",
            True)

    def _say_bye(self):
        self._mqtt_client.publish(
            self._mqtt_topic_status,
            "0",
            True)

    def _prepare(self):
        # prepare mqtt client
        def mqtt_cb(message):
            self._messages.put(message)
        self._mqtt_client = MQTTWrap(self._name)
        self._mqtt_topic_status = config.topic_name_agent_status_get(config.station_name_get(), self._name)
        self._mqtt_topics.append(self._mqtt_topic_status)
        self._mqtt_client.init(self._mqtt_topics, mqtt_cb, self._mqtt_topic_status, "0")
        self._say_hi()

        # prepare signals
        def signal_handler(sig, frame):
            if sig == signal.SIGINT or sig == signal.SIGTERM:
                self._shutdown = True

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _cleanup(self):
        # cleanup mqtt client
        self._mqtt_client.uninit()
        self._mqtt_client = None

    def prepare(self):
        pass

    def cleanup(self):
        pass

    def perform(self):
        self._prepare()
        self.prepare()

        l.info("{0} going on the field".format(self._name))

        while not self._shutdown or not self._messages.empty():
            message = None
            try:
                message = self._messages.get(timeout=0.1)
            except queue.Empty:
                continue

            payload = str(message.payload.decode("utf-8"))
            topic = message.topic
            if topic == self._mqtt_topic_status:
                # status query message
                if payload == "s":
                    self._say_hi()
                # ignore the rest of the status messages
            else:
                # application message
                self.message_cb(topic, payload)

            self._messages.task_done()

        # mark the disconnect
        self._say_bye()

        l.info("{0} returned from the field".format(self._name))

        self.cleanup()
        self._cleanup()
