import numpy as np

# Ports
STREAM_SERVER_PORT = 1235
MESSAGE_SERVER_PORT = 1234
EMITTER_PROBE_PORT = 1233
RC_SERVER_PORT = 1232

PORTS = {"m": 1234, "d": 1235, "rc": 1232}

# Stream's tick time:
FPS = 15

# Standard RGB data type, 0-255 unsigned int
DTYPE = np.uint8
SSEP = b"ROGER"
