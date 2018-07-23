"""
Coordinates the first part of the bootstrap process of a car.
Parses arguments (readargs) and waits for server probes (idle).
"""

import sys

from emittance_emitter.entity import TCPEntity


def readargs():
    if len(sys.argv) == 3:
        return sys.argv[1:3]

    pleading = "Please supply "
    question = ["the local IP address of this Car",
                "a unique ID for this Car"]
    return [input(pleading + q + " > ") for q in question]


def main():
    localIP, carID = readargs()
    lightning_mcqueen = TCPEntity(myID=carID, myIP=localIP)
    lightning_mcqueen.mainloop()


if __name__ == '__main__':
    main()
    print(" -- END PROGRAM --")
