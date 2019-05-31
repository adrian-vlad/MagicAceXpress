import json
from flask import Flask, render_template, request

from messaging import MQTTWrap
from db import Reader, Writer

app = Flask(__name__)

DB_PATH = "test_orig.db"


with Writer(DB_PATH) as db_write:
    db_write.write((
        "CREATE TABLE IF NOT EXISTS "
        "Officers(Name String PRIMARY KEY, Assignment STRING)"))


@app.route("/")
def index():
    name = "haha"
    return render_template('hello.html', name=name)


#@app.route("/officer/<station>/", methods=["POST", "GET", "PUT", "DELETE"])
@app.route("/officer/", methods=["POST", "GET", "PUT", "DELETE"])
@app.route("/officer", methods=["POST", "GET", "PUT", "DELETE"])
#@app.route("/officer/", methods=["GET"])
#@app.route("/officer/", methods=["GET"])
def officer():
    content_str = request.data.decode('utf-8')

    station = request.args.get("station", None)
    # if station is None:
    #     return ""

    ret_str = ""
    if request.method == "POST":

        content_json = request.get_json(True)

        mqtt_client = MQTTWrap("ceva")
        mqtt_client.init()
        mqtt_client.publish(station, content_str)
        mqtt_client.uninit()

        print(content_json)

        name = content_json["name"]
        assignment = content_json["assignment"]
        with Writer(DB_PATH) as db_write:
            db_write.write((
                "INSERT INTO Officers (Name, Assignment) "
                "VALUES ("
                "?,"
                "?"
                ")"
            ), parameters=(name, json.dumps(assignment)))

    if request.method == "GET":
        ret = []
        with Reader(DB_PATH) as db_read:
            ret = db_read.read((
                "SELECT Name, Assignment "
                "FROM Officers "
            ))

        ret_str = json.dumps([{"name": row[0], "assignment": json.loads(row[1])} for row in ret])

    print(ret_str)
    return ret_str


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
