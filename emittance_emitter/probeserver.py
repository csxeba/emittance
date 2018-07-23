from __future__ import print_function, absolute_import, unicode_literals

import socket

from emittance_common.routine import srvsock


class ProbeServer(object):

    """
    Cars enter this state initially, if no server IP is given for them.
    In the Idle state, they can be probed and if the probing message is
    valid, they send back their CarID and IP address to the probe.
    """

    def __init__(self, myIP, myID):
        self.IP = myIP
        self.ID = myID
        self.sock = None
        self.conn = None
        self.remote_address = None

    def _read_message_from_probe(self):
        try:
            m = self.conn.recv(1024).decode("utf-8")
        except socket.timeout:
            return
        else:
            return m if m in ("probing", "connect") else None

    def _new_connection_causes_loopbreak(self):
        msg = self._read_message_from_probe()
        if msg is None:
            print("PROBESRV: empty message from", self.remote_address[0])
            return False

        print("PROBESRV: probed by: {}; msg: {}".format(self.IP, msg))
        self._respond_to_probe(msg)
        return msg == "connect"

    def _respond_to_probe(self, msg):
        m = "emitter-{} @ {}".format(self.ID, self.IP)
        if msg in ("connect", "probing"):
            self.conn.send(m.encode())
        else:
            print("PROBESRV: invalid message received! Ignoring...")

    def mainloop(self):
        self.sock = srvsock(self.IP, channel="probe", timeout=1)
        print("PROBESRV: Awaiting connection... Hit Ctrl-C to break!".format(self.ID))
        while 1:
            try:
                self.conn, self.remote_address = self.sock.accept()
            except socket.timeout:
                pass
            else:
                if self._new_connection_causes_loopbreak():
                    break
                self.conn.close()
                self.conn = None
        return self.remote_address[0]


class ProbeHandshake(object):

    """
    Coordinates the probing protocol's handshake process on the emitter's side
    """

    @classmethod
    def perform(cls, streamer, messenger):
        cls._send_introduction(streamer, messenger)
        hello = cls._read_response(messenger)
        if not cls._validate_response(hello):
            print("PROBESRV: invalid server response:", hello)
            return None

    @staticmethod
    def _send_introduction(streamer, messenger):
        introduction = ("HELLO;" + streamer.frameshape).encode()
        print("PROBESRV: sending introduction:", introduction)
        messenger.send(introduction)

    @staticmethod
    def _read_response(messenger):
        for i in range(4, -1, -1):
            hello = messenger.recv(timeout=1)
            if hello is not None:
                return hello
        else:
            print("PROBESRV: didn't receive any response :(")

    @staticmethod
    def _validate_response(hello):
        return hello == "HELLO"
