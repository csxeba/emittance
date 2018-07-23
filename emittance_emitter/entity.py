# Project imports
from .channel import TCPStreamer, RCReceiver
from .component import Commander
from .probeserver import ProbeServer, ProbeHandshake
from emittance_common.messaging import Messaging


class TCPEntity(object):

    entity_type = "emitter"

    def __init__(self, myID, myIP):
        self.ID = myID
        self.ip = myIP

        self.streamer = TCPStreamer()
        self.receiver = RCReceiver()
        self.messenger = None  # type: Messaging
        self.commander = None  # type: Commander
        self.server_ip = None
        self.online = False

    def mainloop(self):
        """
        Loop for the main thread
        """
        if not self.idle():
            self.shutdown()
            return
        if not self.connect():
            self.shutdown()
            return
        self.commander.mainloop()

    def idle(self):
        try:
            while not self.server_ip:
                self.server_ip = ProbeServer(self.ip, self.ID).mainloop()
        except KeyboardInterrupt:
            print("CAR: Cancelled connection! Exiting...")
            return False
        except Exception as E:
            print("CAR: ProbeServer failed with exception:", E)
            return False
        if self.server_ip is None:
            return False
        return True

    def connect(self, ip=None):
        """Establishes the messaging connection with a server"""
        if ip is None:
            ip = self.server_ip
        else:
            self.server_ip = ip
        mytag = "{}-{}:".format(self.entity_type, self.ID).encode()
        self.messenger = Messaging.connect_to(ip, timeout=1, tag=mytag)
        ProbeHandshake.perform(self.streamer, self.messenger)

        self.receiver.connect(ip)
        self.receiver.start()

        self.streamer.connect(ip)

        self.commander = Commander(
            self.messenger, stream=self.stream_command, shutdown=self.shutdown
        )
        self.out("connected to", ip)
        return True

    def out(self, *args, **kw):
        """Wrapper for print(). Appends emitter's ID to every output line"""
        sep, end = kw.get("sep", " "), kw.get("end", "\n")
        print("CAR {}:".format(self.ID), *args, sep=sep, end=end)

    def stream_command(self, switch):
        if switch == "on":
            self.streamer.start()
        elif switch == "off":
            self.streamer.stop()
        else:
            return

    def shutdown(self, msg=None):
        if msg is not None:
            self.out(msg)
        if self.receiver is not None:
            self.receiver.teardown(0)
        if self.streamer is not None:
            self.streamer.teardown(0)
        if self.messenger is not None:
            self.messenger.send("offline".encode())
            self.messenger.teardown(2)
        self.online = False
