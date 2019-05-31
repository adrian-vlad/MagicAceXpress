
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.service
import dbus.mainloop.glib
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject


AGENT_INTERFACE = "org.bluez.Agent1"
AGENT_PATH = "/test/agent"


g_connected = False
g_authorized = False

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"


class Agent(dbus.service.Object):
    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print("AuthorizeService (%s, %s)" % (device, uuid))
        global g_authorized
        if g_authorized:
            print("Already authorized")
            raise Rejected("Connection rejected")
        if uuid == "0000110d-0000-1000-8000-00805f9b34fb":
            print("Authorized A2DP Service")
            g_authorized = True
            return
        print("Rejecting non-A2DP Service")
        raise Rejected("Connection rejected")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        return "0000"

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        return dbus.UInt32("password")

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" %
                        (device, passkey, entered))

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        raise Rejected("Pairing rejected")

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")


class BluetoothAgent(object):
    def __init__(self, cb_connect, cb_disconnect):
        self._cb_connect = cb_connect
        self._cb_disconnect = cb_disconnect

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()

        self._agent_a2dp = Agent(bus, AGENT_PATH)

        obj = bus.get_object("org.bluez", "/org/bluez");
        manager = dbus.Interface(obj, "org.bluez.AgentManager1")
        manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

        print("A2DP Agent Registered")

        manager.RequestDefaultAgent(AGENT_PATH)

        def cbl(interface, changed, invalidated, path):
            if "Connected" in changed:
                if changed["Connected"]:
                    print("%s connected" % path)
                    self._cb_connect(path)
                else:
                    print("%s disconnected" % path)
                    self._cb_disconnect(path)

        bus.add_signal_receiver(cbl,
                    dbus_interface="org.freedesktop.DBus.Properties",
                    signal_name="PropertiesChanged",
                    path_keyword="path",
                    arg0="org.bluez.Device1")

        self._mainloop = GObject.MainLoop()

    def loop(self):
        self._mainloop.run()

    def stop(self):
        self._mainloop.quit()

    def connect(self, device):
        global g_connected
        g_connected = True

    def disconnect(self, device):
        global g_connected
        g_connected = False
        global g_authorized
        g_authorized = False

