import threading as thr

from emittance_common.abstract import AbstractListener, AbstractCommander
from emittance_common.interface import InterfaceFactory


class Listener(AbstractListener):

    """
    Listens for incoming emitter connections for the server.
    Runs in a separate thread.
    """

    def __init__(self, master):
        AbstractListener.__init__(self, master.ip)
        self.master = master
        self.worker = None

    def start(self):
        """
        Creates a new worker thread in case Listener needs to be
        restarted.
        self.run is inherited from AbstractListener
        """
        if self.worker is not None:
            print("ABS_LISTENER: Attempted start while already running!")
            return
        self.worker = thr.Thread(target=self.mainloop, name="Server-Listener")
        self.worker.start()

    def teardown(self, sleep=2):
        super(Listener, self).teardown(sleep)
        self.worker = None

    def callback(self, msock):
        """
        Builds an interface and puts it into the server's appropriate
        container for later usage.
        :param msock: connected socket used for message connection
        """
        print("LISTENER: called callback on incoming connection!")
        ifc = InterfaceFactory(msock, self.dlistener, self.rclistener).get()
        if not ifc:
            print("LISTENER: no interface received!")
            return
        print("LISTENER: received {} interface: {}".format(ifc.entity_type, ifc))
        if ifc.entity_type == "emitter":
            self.master.emitters[ifc.ID] = ifc
        else:
            self.master.subscribers[ifc.ID] = ifc


class Console(AbstractCommander):

    def read_cmd(self):
        c = input(self.prompt).split(" ")
        cmd = c[0].lower()
        if len(c) > 1:
            args = c[1:]
        else:
            args = []
        return cmd, args
