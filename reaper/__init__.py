import threading
import queue
import time
import logging


l = logging.getLogger(__name__)

g_the_reaper = None
g_officers_list = queue.Queue()
g_stopping = False
g_killing = False
g_reaping = False


def the_reaping():
    l.info("Reaping started")

    while True:
        time.sleep(0.1)

        # the reaper is killing something
        if g_killing:
            continue

        global g_reaping
        g_reaping = True

        # if nothing to do, then stop
        if g_officers_list.empty():
            g_reaping = False

            if g_stopping:
                break
            continue

        # select a new officer from the list
        p = g_officers_list.get()
        if not p.is_alive():
            # reap the dead officer
            l.info("Reaped officer " + p.name)
            p.join()

            # TODO: signal somehow that an officer has died unexpectedly
        else:
            if g_stopping:
                # kill the officer
                l.info("Killed officer " + p.name)
                p.terminate()

            # the officer is not dead, so leave it alone for a while
            g_officers_list.put(p)
        g_officers_list.task_done()

        g_reaping = False

    l.info("Reaping finished")


def summon():
    l.debug("Summoning Reaper")

    global g_the_reaper
    g_the_reaper = threading.Thread(target=the_reaping)
    g_the_reaper.start()


def watch(process):
    if g_stopping:
        return

    l.debug("Watching officer {0}".format(process.name))
    g_officers_list.put(process)


def kill(name):
    if g_stopping:
        return

    l.debug("Killing officer {0}".format(name))

    global g_killing
    g_killing = True

    while g_reaping:
        time.sleep(0.001)

    # get the officer
    list_number = g_officers_list.qsize()
    p = None
    while list_number > 0:
        p = g_officers_list.get()
        g_officers_list.task_done()
        if p.name == name:
            break

        g_officers_list.put(p)
        p = None

        list_number -= 1

    # kill him
    if p is not None:
        p.terminate()
        p.join()
        l.info("Killed and reaped officer {0}".format(name))
    else:
        l.error("Officer not found {0}".format(name))

    g_killing = False


def banish():
    l.debug("Banishing Reaper")

    global g_stopping
    g_stopping = True

    global g_officers_list
    g_officers_list.join()

    global g_the_reaper
    g_the_reaper.join()

    l.info("Reaper banished")
