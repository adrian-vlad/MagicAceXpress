import sys
import config

from db import Writer


if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments")
    sys.exit(1)

station_name = sys.argv[1]

with Writer(config.DB_PATH) as db_write:
    db_write.write((
        "CREATE TABLE IF NOT EXISTS "
        "Station(ID INT PRIMARY KEY, PID STRING, Name STRING)"))

    db_write.write((
        "INSERT OR REPLACE INTO Station (ID, Name) "
        "VALUES ("
            "0, "
            "'" + station_name + "'"
        ") "
        ))
