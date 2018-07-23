import sys
import time

from emittance_subscriber.direct import DirectConnection


def run():

    from random import choice

    def probe_and_connect(dc, IP):

        # Probe emitter up to 3 times
        for probe in range(3, -1, -1):
            ID = dc.probe(IP)
            print("PROBE-{}: reponse: {} from {}"
                  .format(probe, IP, ID))
            time.sleep(3)
            if ID is not None:
                break
        else:
            # If noone answers, return False success code
            return False

        # Try to build connection, return the success code
        return dc.connect(IP)

    def test_stream(dc):
        print("STREAM TEST online...")
        dc.display_stream()
        while 1:
            # noinspection PyUnboundLocalVariable
            input("Hit <enter> to stop! ")
            dc.stop_stream()
            break
        print("STREAM TEST offline...")

    def test_rc(dc):
        msgs = b">", b"<", b"A", b"V"
        choices = []
        print("RC TEST online...")
        while 1:
            try:
                chc = choice(msgs)
                choices.append(chc)
                dc.rc_command(chc)
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception as E:
                print("RC Test caught exception:", E)
                break
            if len(choices) >= 10:
                print("".join(choices))
                choices = []
        print("RC TEST offline...")

    car_IP = ("127.0.0.1" if len(sys.argv) == 1 else sys.argv[1])
    connection = DirectConnection(car_IP)

    success = probe_and_connect(connection, car_IP)
    if not success:
        return
    test_stream(connection)
    test_rc(connection)
    print(" -- TEARING DOWN -- ")
    connection.teardown(3)
    print(" -- END PROGRAM -- ")


if __name__ == '__main__':
    run()
