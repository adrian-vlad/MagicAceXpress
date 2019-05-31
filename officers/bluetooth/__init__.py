import os
import time
import threading
import alsaaudio
import logging

import config
import officers.Agent
from officers.bluetooth.a2dp_agent import BluetoothAgent


l = logging.getLogger(__name__)


# TODO: implement singleton for this class and the a2dp_agent

# Example of device name: /org/bluez/hci0/dev_40_88_05_B8_E9_8A
BLUEZ_DEVICE_PREFIX = "dev_"


class Agent(officers.Agent.Agent):
    def __init__(self, name, warrant):
        super().__init__(name, warrant)

        self._mqtt_topic_name = config.topic_name_officer_get(config.station_name_get(), self._name)
        self._device = None

        # bluetooth connection
        def cb_connect(device):
            if self._device is None:
                device = os.path.basename(device)[len(BLUEZ_DEVICE_PREFIX):].replace("_", ":")
                self._device = device
                l.debug("New device %s" % (device))
                self._bl.connect(self._device)

                # start sending audio
                self._streaming = True

        def cb_disconnect(device):
            device = os.path.basename(device)[len(BLUEZ_DEVICE_PREFIX):].replace("_", ":")
            if device == self._device:
                self._bl.disconnect(self._device)
                self._device = None
                l.debug("Disconnected device %s" % (device))

                # stop sending audio
                self._streaming = False

        self._bl = BluetoothAgent(cb_connect, cb_disconnect)
        self._th_bl = threading.Thread(target=self._bl.loop)
        self._th_bl.start()

        # bluetooth audio streaming
        self._streaming = False
        self._stop = False
        def stream():
            while not self._stop:
                if self._streaming:
                    try:
                        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device="bluealsa:HCI=hci0,DEV={0},PROFILE=a2dp".format(self._device))
                        inp.setchannels(2)
                        inp.setrate(48000)
                        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                        inp.setperiodsize(2000)

                        while self._streaming:
                            ln, data = inp.read()
                            self._stream_audio(data)
                    except Exception as e:
                        l.error("Error while streaming: {0}".format(type(e).__name__))
                        time.sleep(1)
                else:
                    time.sleep(1)

        self._th_stream = threading.Thread(target=stream)
        self._th_stream.start()

    def cleanup(self):
        self._stop = True
        self._streaming = False
        self._th_stream.join()

        self._bl.stop()
        self._th_bl.join()

    def _publish(self, message):
        self._mqtt_client.publish(self._mqtt_topic_name, str(message))

    def _stream_audio(self, chunk):
        self._mqtt_client.publish("{0}/{1}".format(self._mqtt_topic_name, "audio"), chunk, retain=False, qos=0)
