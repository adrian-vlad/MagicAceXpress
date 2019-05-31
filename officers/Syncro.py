import threading

from officers.Detective import Agent as Detective


class Agent(Detective):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        self._timer_seconds = int(warrant)
        self._timer = None

    def prepare(self):
        def timer_callback():
            self._publish("1")

            self._timer = threading.Timer(self._timer_seconds, timer_callback)
            self._timer.start()

        timer_callback()

    def cleanup(self):
        if self._timer is not None:
            self._timer.cancel()
