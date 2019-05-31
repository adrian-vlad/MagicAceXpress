import pyaudio

import config
import officers.Agent


channels = 2
framerate=48000


class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        if "stream" not in warrant:
            raise Exception("stream not found in warrant")

        self.stream = pyaudio.PyAudio().open(
            format = pyaudio.paInt16,
            channels = channels,
            rate = framerate,
            output = True)

        self._mqtt_topics.append(warrant["stream"])

        def message_cb(topic, message):
            self.stream.write(message)

        self.message_cb = message_cb
