import time
import json
import multiprocessing
import importlib
import logging

import config
from db import Reader, Writer
import reaper as Reaper


l = logging.getLogger(__name__)


def _org_chart_init():
    with Writer(config.DB_PATH) as db_write:
        db_write.write((
            "CREATE TABLE IF NOT EXISTS "
            "Officers(Name String PRIMARY KEY, Duty STRING, Warrant STRING)"))


def _org_chart_list():
    ret = []
    with Reader(config.DB_PATH) as db_read:
        ret = db_read.read((
            "SELECT Name, Duty, Warrant "
            "FROM Officers "
        ))

    return [(row[0], row[1], json.loads(row[2])) for row in ret]


def _org_chart_add(name, duty, warrant):
    with Writer(config.DB_PATH) as db_write:
        db_write.write((
            "INSERT INTO Officers (Name, Duty, Warrant) "
            "VALUES ("
            "?,"
            "?,"
            "?"
            ")"
        ), parameters=(name, duty, json.dumps(warrant)))


def _org_chart_remove(name):
    with Writer(config.DB_PATH) as db_write:
        db_write.write((
            "DELETE FROM Officers "
            "WHERE Name = ? "
        ), parameters=(name,))


def perform(name, duty, warrant):
    try:
        import_obj = importlib.import_module("officers.{0}".format(duty))
        agent_class = getattr(import_obj, "Agent", None)
    except Exception as e:
        l.error("Agent duty {0} not found: {1}".format(duty, e))
        return

    try:
        agent = agent_class(name, warrant)
    except Exception as e:
        l.error("Agent duty {0} failed to initialize: {1}".format(duty, e), exc_info=True)
        return

    while not agent._shutdown:
        try:
            agent.perform()
        except Exception as e:
            l.error("Agent could not perform: {0}".format(e), exc_info=True)


def _officer_dispatch(name, duty, warrant):
    p = multiprocessing.Process(name=name, target=perform, args=(name, duty, warrant))
    p.start()
    Reaper.watch(p)


def _officer_return(name):
    Reaper.kill(name)


def _officer_hire(name, duty, warrant):
    # save the new position
    _org_chart_add(name, duty, warrant)

    # dispatch the officer
    _officer_dispatch(name, duty, warrant)


def _officer_fire(name):
    # call the officer back from the assignment
    _officer_return(name)

    # remove the position
    _org_chart_remove(name)


def _dispatch_all():
    for name, duty, warrant in _org_chart_list():
        _officer_dispatch(name, duty, warrant)


def dispatch(data):
    name = data.get("name", None)
    duty = data.get("duty", None)
    warrant = data.get("warrant", None)

    if name is None:
        l.error("Message does not contain a name")
        return

    _officer_fire(name)

    if duty is not None:
        _officer_hire(name, duty, warrant)


def shift_start():
    multiprocessing.set_start_method("fork")

    Reaper.summon()

    _org_chart_init()

    _dispatch_all()


def shift_end():
    Reaper.banish()
