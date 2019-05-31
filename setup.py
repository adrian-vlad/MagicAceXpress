
from messaging import MQTTWrap

mqtt_client = MQTTWrap("haha")
mqtt_client.init()

agents = [
#     '{"station": "first_client", "name": "nick1", "duty": "gpio_out", "warrant": {"pin": "23"}}',
#     '{"station": "first_client", "name": "nick2", "duty": "gpio_out", "warrant": {"pin": "24"}}',
#     '{"station": "first_client", "name": "nick3", "duty": "gpio_in", "warrant": {"pin": "17"}}',
#     '{"station": "first_client", "name": "nick4", "duty": "gpio_in", "warrant": {"pin": "27"}}',
    '{"station": "first_client", "name": "bl1", "duty": "bluetooth", "warrant": {}}',

#     '{"station": "headquarters", "name": "dum1", "duty": "Dummy", "warrant": {}}',
#     '{"station": "headquarters", "name": "dum2", "duty": "Dummy", "warrant": {}}',
#     '{"station": "headquarters", "name": "dum3", "duty": "Dummy", "warrant": {}}',
#     '{"station": "headquarters", "name": "dum4", "duty": "Dummy", "warrant": {}}',
#     '{"station": "headquarters", "name": "dum5", "duty": "Dummy", "warrant": {}}',
#     '{"station": "headquarters", "name": "dum6", "duty": "Dummy", "warrant": {}}',
#     '{"station": "headquarters", "name": "dum7", "duty": "Dummy", "warrant": {}}',
]

for agent in agents:
    mqtt_client.publish("headquarters/dispatcher", agent)


mqtt_client.uninit()
