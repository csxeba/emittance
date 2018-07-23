from __future__ import print_function, unicode_literals, absolute_import

import time

from emittance_aggregator.server import Aggregator


def readargs():
    import sys

    if len(sys.argv) == 2:
        return sys.argv[1]
    else:
        return input("Please supply the local IP address of this server > ")


def main():
    """Does the argparse and launches a server"""
    serverIP = readargs()

    # Context manager ensures proper shutdown of threads
    # see FleetHandler.__enter__ and __exit__ methods!
    with Aggregator(serverIP) as server:
        server.mainloop()

    time.sleep(3)
    print("OUTSIDE: Exiting...")


if __name__ == '__main__':
    main()
