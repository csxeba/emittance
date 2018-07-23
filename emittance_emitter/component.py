# stdlib imports
import os

# 3rd party imports
import cv2

# Project imports
from emittance_common.util import CaptureDeviceMocker
from emittance_common.abstract import AbstractCommander


class CaptureDevice(object):
    """
    Methods used for setting up a video capture device.
    """

    # noinspection PyArgumentList
    def __init__(self, dev=None, dummyfile=None):
        if dev is None:
            if not dummyfile:
                self.device = lambda: cv2.VideoCapture(0)
            elif not os.path.exists(dummyfile):
                self.device = CaptureDeviceMocker
            else:
                self.device = lambda: cv2.VideoCapture(dummyfile)
        else:
            self.device = dev

        self._eye = None

    def open(self):
        self._eye = self.device()

    def read(self):
        if self._eye is None:
            self.open()
        return self._eye.read()

    def stream(self):
        if self._eye is None:
            self.open()
        while self._eye:
            yield self._eye.read()

    def close(self):
        self._eye.release()
        self._eye = None


class Commander(AbstractCommander):
    """
    Receives commands from the Aggregator
    """

    def __init__(self, messenger, **commands):
        super().__init__("Emitter", commands_dict=commands)
        self.messenger = messenger
        print("COMMANDER: online!")

    def read_cmd(self):
        m = self.messenger.recv(timeout=1)
        if m is None:
            return None, ()
        m = m.split(" ")
        return m[0], m[1:]
