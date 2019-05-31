from db import Reader

MQTT_BROKER_IP = "192.168.111.185"
DB_PATH = "/var/tmp/magicacexpress.db"

LOG_FILE_PATH = "/var/tmp/magicacexpress.log"

MQTT_TOPIC_STATION = "{0}"
MQTT_TOPIC_OFFICER = "{0}/{1}"
MQTT_TOPIC_AGENT_STATUS = "{0}/{1}/status"


def station_name_get():
    with Reader(DB_PATH) as db_read:
        return db_read.read((
            "SELECT Name "
            "FROM Station "
            "WHERE ID = 0 "))[0][0]


def topic_name_station_get(station_name):
    return MQTT_TOPIC_STATION.format(station_name)


def topic_name_officer_get(station_name, officer_name):
    return MQTT_TOPIC_OFFICER.format(station_name, officer_name)

def topic_name_agent_status_get(station_name, agent_name):
    return MQTT_TOPIC_AGENT_STATUS.format(station_name, agent_name)
