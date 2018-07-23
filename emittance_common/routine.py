from __future__ import unicode_literals, print_function, absolute_import

import socket

import numpy as np

from .const import (
    DTYPE, STREAM_SERVER_PORT, MESSAGE_SERVER_PORT, RC_SERVER_PORT, EMITTER_PROBE_PORT
)


def white_noise(shape):
    return (np.random.randn(*shape) * 255.).astype(DTYPE)


def my_ip():
    """Hack to obtain the local IP address of an entity"""
    from socket import socket, AF_INET, SOCK_DGRAM
    tmp = socket(AF_INET, SOCK_DGRAM)
    tmp.connect(("8.8.8.8", 80))
    address = tmp.getsockname()[0]
    if address is None:
        raise RuntimeError("Unable to determine the local IP address!")
    return address


def srvsock(ip, channel, timeout=None):
    assert channel[0] in "dsmrp"
    port = {
        "d": STREAM_SERVER_PORT,
        "s": STREAM_SERVER_PORT,
        "m": MESSAGE_SERVER_PORT,
        "r": RC_SERVER_PORT,
        "p": EMITTER_PROBE_PORT
    }[channel[0]]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if timeout is not None:
        s.settimeout(timeout)
    s.bind((ip, port))
    s.listen(1)
    return s
