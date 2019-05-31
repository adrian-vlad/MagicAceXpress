import logging
import RPi.GPIO as GPIO

from officers.Detective import Agent as Detective


l = logging.getLogger(__name__)


class Agent(Detective):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        if "pin" not in warrant:
            l.error("Pin not found in warrant")
            return

        self._pin = int(warrant["pin"])

    def prepare(self):
        def gpio_callback(channel):
            self._publish(GPIO.input(channel))

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self._pin, GPIO.BOTH, callback=gpio_callback)

    def cleanup(self):
        GPIO.cleanup()
