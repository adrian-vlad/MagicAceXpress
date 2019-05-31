import logging
import RPi.GPIO as GPIO

from officers.Enforcer import Agent as Enforcer


l = logging.getLogger(__name__)


class Agent(Enforcer):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        if "pin" not in warrant:
            l.error("Pin not found in warrant")
            return

        self._pin = int(warrant["pin"])

        def message_cb(topic, message):
            l.debug("New message: {0}".format(message))
            GPIO.output(self._pin, int(message))

        self.message_cb = message_cb

    def prepare(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup()
