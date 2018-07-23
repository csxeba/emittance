# stdlib imports
import time
from datetime import datetime

# project imports
from .component import Listener, Console

from emittance_common.subsystem import StreamDisplayer
from emittance_common.util import Table
from emittance_common.probeclient import Probe


# noinspection PyUnusedLocal
class Aggregator(object):

    """
    Class of the main server.
    Groups together the following concepts:
    - Console is run in the main thread, waiting for and parsing input commands.
    - Listener is listening for incomming emitter connections in a separate thread.
    It also coordinates the creation and validation of new emitter interfaces.
    - EmitterInterface instances are stored in the .emitters dictionary.
    - StreamDisplayer objects can be attached to EmitterInterface objects and
    are run in a separate thread each.
    - Aggregator itself is responsible for sending commands to EmitterInterfaces
    and to coordinate the shutdown of the emitters on this side, etc.
    """

    def __init__(self, myIP):
        self.ip = myIP
        self.clients = {}
        self.emitters = {}
        self.watchers = {}
        self.since = datetime.now()

        self.status = "Idle"
        self.console = Console(
            master_name="Aggregator-Server",
            status_tag=self.status,
            commands_dict={
                "emitters": self.printout_emitters,
                "kill": self.kill_emitter,
                "watch": self.watch_emitter,
                "unwatch": self.stop_watch,
                "shutdown": self.shutdown,
                "status": self.report,
                "message": self.message,
                "probe": self.probe,
                "connect": Probe.initiate,
                "sweep": self.sweep
            }
        )

        self.listener = Listener(self)
        self.listener.start()
        print("AGGREGATOR: online")

    def mainloop(self):
        self.console.mainloop()

    def printout_emitters(self, *args):
        """List the current emitter-connections"""
        print("Emitters online:\n{}\n".format("\n".join(self.emitters)))

    @staticmethod
    def probe(*ips):
        """Probe the supplied ip address(es)"""
        IDs = dict(Probe.probe(*ips))
        for ID, IP in IDs.items():
            print("{:<15}: {}".format(IP, ID if ID else "-"))

    def message(self, ID, *msgs):
        """Just supply the emitter ID, and then the message to send."""
        self.emitters[ID].send(" ".join(msgs).encode())

    @staticmethod
    def sweep(*ips):
        """Probe the supplied ip addresses and print the formatted results"""

        def get_status(dID):
            status = ""
            if dID is None:
                status = "offline"
            else:
                status = "available"
            return status

        if not ips:
            print("[sweep]: please specify an IP address range!")
            return
        IDs = dict(Probe.probe(*ips))
        tab = Table(["IP", "ID", "status"],
                    [3*5, max(len(v) for v in IDs.values()), 11])
        for IP, ID in IDs.items():
            tab.add(IP, ID, get_status(ID))

        print(tab.get())

    def kill_emitter(self, ID, *args):
        """Sends a shutdown message to a remote emitter, then tears down the connection"""
        if ID not in self.emitters:
            print("SERVER: no such emitter:", ID)
            return
        if ID in self.watchers:
            self.stop_watch(ID)
        success = self.emitters[ID].teardown(sleep=1)
        if success:
            del self.emitters[ID]

    def watch_emitter(self, ID, *args):
        """Launches the stream display in a separate thread"""
        if ID not in self.emitters:
            print("SERVER: no such emitter:", ID)
            return
        if ID in self.watchers:
            print("SERVER: already watching", ID)
            return
        self.emitters[ID].send(b"stream on")
        time.sleep(1)
        self.watchers[ID] = StreamDisplayer(self.emitters[ID])

    def stop_watch(self, ID, *args):
        """Tears down the StreamDisplayer and shuts down a stream"""
        if ID not in self.watchers:
            print("SERVER: {} is not being watched!".format(ID))
            return
        self.emitters[ID].send(b"stream off")
        self.watchers[ID].teardown(sleep=1)
        del self.watchers[ID]

    def shutdown(self, *args):
        """Shuts the server down, terminating all threads nicely"""

        self.listener.teardown(1)

        rounds = 0
        while self.emitters:
            print("SERVER: Emitter corpse collection round {}/{}".format(rounds+1, 4))
            for ID in self.emitters:
                if ID in self.watchers:
                    self.stop_watch(ID)
                self.kill_emitter(ID)

            if rounds >= 3:
                print("SERVER: emitters: [{}] didn't shut down correctly"
                      .format(", ".join(self.emitters.keys())))
                break
            rounds += 1
        else:
            print("SERVER: All emitters shut down correctly!")

        print("SERVER: Exiting...")

    def report(self, *args):
        """
        Prints a nice server status report
        """
        repchain = "FIPER Server @ {}\n".format(self.ip)
        repchain += "-" * (len(repchain) - 1) + "\n"
        repchain += "Up since " + self.since.strftime("%Y.%m.%d %H:%M:%S") + "\n"
        repchain += "Emitters online: {}\n".format(len(self.emitters))
        print("\n" + repchain + "\n")

    def __enter__(self):
        """Context enter method"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context exit method, ensures proper shutdown"""
        self.shutdown()
