import time
import paho.mqtt.client as mqtt

import config


# TODO: tls + check server cert
class MQTTWrap():
    def __init__(self, name):
        self._mqtt_client = mqtt.Client(client_id=name, clean_session=False, protocol=mqtt.MQTTv311)

    def init(self, topic_names=[], message_cb=None, last_will_topic=None, last_will_message=None):
        self._mqtt_client.reinitialise()

        mqtt_client_connected = False

        def on_connect(client, userdata, flags, rc):
            nonlocal mqtt_client_connected
            mqtt_client_connected = True

        def on_message(client, userdata, message):
            message_cb(message)

        self._mqtt_client.on_connect = on_connect
        self._mqtt_client.on_message = on_message

        if last_will_topic is not None:
            self._mqtt_client.will_set(last_will_topic, last_will_message, 2, True)
        self._mqtt_client.connect(config.MQTT_BROKER_IP, keepalive=5)
        self._mqtt_client.loop_start()

        while not mqtt_client_connected:
            time.sleep(0.01)

        if  message_cb is not None:
            for topic_name in topic_names:
                # TODO
                (result, mid) = self._mqtt_client.subscribe(topic_name, qos=2)

    def uninit(self):
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()

    def publish(self, topic_name, message, retain=False, qos=2):
        self._mqtt_client.publish(topic_name, message, qos, retain)
