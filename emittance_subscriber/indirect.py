from __future__ import print_function, absolute_import, unicode_literals

import socket

from emittance_common.const import MESSAGE_SERVER_PORT, STREAM_SERVER_PORT, RC_SERVER_PORT
from emittance_common.messaging import Messaging


class ServerConnection(object):

    entity_type = "subscriber"

    def __init__(self, serverIP, ID):
        self.ID = ID
        self.serverIP = serverIP
        self.messaging = Messaging(socket.create_connection((serverIP, MESSAGE_SERVER_PORT))[0],
                                   tag="{}-{}:".format(self.entity_type, self.ID).encode())

        # Validation should be done via the messaging channel:
        # - username/password check
        # - version check?
        # - server validation?

        self.dsocket = socket.create_connection((serverIP, STREAM_SERVER_PORT))[0]
        self.rcsocket = socket.create_connection((serverIP, RC_SERVER_PORT))[0]

    def _sendcmd(self, cmd, timeout=3):
        self.messaging.send(cmd)
        response = self.messaging.recv(timeout=timeout)
        return response

    def request_car_list(self):
        cars = self._sendcmd(b"cmd|cars", 3).split(", ")
        print(cars)
        return cars.split(", ")

    def request_car_connection(self, carID):
        framestring = self._sendcmd("cmd|connect {}".format(carID), 3).encode()
        print("DIRECT_CONN: frameshape received:", framestring)

    def observe_someone_else(self, ID):
        status = self._sendcmd("cmd|watch {}".format(ID), 3).encode()
        print("DIRECT_CONN: status received:", status)
