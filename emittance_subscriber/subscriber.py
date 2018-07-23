import socket

from emittance_common.const import PORTS
from emittance_common.interface import InterfaceFactory


class Subscriber:

    def __init__(self, my_ip, server_ip):
        self.ip = my_ip
        self.emitterifc = None
        self.sockets = {t: socket.socket() for t in PORTS}
        for stype, sock in self.sockets.items():
            sock.connect((server_ip, PORTS[stype]))
