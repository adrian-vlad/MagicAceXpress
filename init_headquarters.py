import config

from db import Writer

with Writer(config.DB_PATH) as db_write:
    db_write.write((
        "CREATE TABLE IF NOT EXISTS "
        "Station(ID INT PRIMARY KEY, PID STRING, Name STRING)"))

    db_write.write((
        "INSERT OR REPLACE INTO Station (ID, Name) "
        "VALUES ("
            "0, "
            "'headquarters'"
        ") "
        ))

    db_write.write((
        "CREATE TABLE IF NOT EXISTS "
        "Agents(Station STRING, Name STRING, Duty STRING, Warrant STRING, PRIMARY KEY (Station, Name))"))
