import abc
import socket

from emittance_common.const import EMITTER_PROBE_PORT


class Probe(object):
    """
    Mixin / Static class for entities with probing capabilities.
    """

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def probe(*ips):
        """
        Send a <probing> message to the specified IP addresses.
        If the target is a emitter, it will return its ID, or None otherwise.
        """
        return Probe._probe_all(b"probing", *ips)

    @staticmethod
    def initiate(*ips):
        """
        Send a <connect> message to the specified IP addresses.
        The target emitter will initiate connection to this server/subscriber.
        """
        got = Probe._probe_all(b"connect", *ips)
        return got if len(got) > 1 else got[0]

    @staticmethod
    def _validate_car_tag(tag, address=None):

        def missing_ampersand():
            if " @ " not in tag:
                return 1

        def warn_in_case_of_unexpected_remote_IP_address():
            if remote_addr != address:
                print("INVALID TAG: address invalid:")
                print("(expected) {} != {} (got)"
                      .format(address, remote_addr))

        def invalid_entity_type():
            if entity_type != "emitter":
                pass

        tag = tag.decode("utf-8")
        if missing_ampersand():
            return
        IDs, remote_addr = tag.split(" @ ")
        if address is not None:
            warn_in_case_of_unexpected_remote_IP_address()
        entity_type, ID = IDs.split("-")
        if invalid_entity_type():
            return
        return ID

    @staticmethod
    def _probe_all(msg, *ips):
        """
        Send a <probing> message to the specified IP addresses.
        If the target is a emitter, it will return its ID, or None otherwise.
        """
        reparsed = []
        for ip in ips:
            reparsed += Probe._reparse_and_validate_ip(ip)
        responses = [Probe._probe_one(ip, msg) for ip in reparsed]
        return responses

    @staticmethod
    def _probe_one(ip, msg):
        """
        Probes an IP address with a given message.
        This causes the remote emitter to send back its
        tag, which is validated, then the emitter ID is
        extracted from it and returned.
        """

        assert msg.decode("utf-8") in ("connect", "probing"), "Invalid message!"

        def create_connection():
            while 1:
                try:
                    sock.connect((ip, EMITTER_PROBE_PORT))
                except socket.timeout:
                    print("PROBE: waiting for remote...")
                except socket.error:
                    return 0
                else:
                    return 1

        def probe_and_receive_tag():
            sock.send(msg)
            for i in range(5, 0, -1):
                try:
                    network_tag = sock.recv(1024)
                except socket.timeout:
                    print("PROBE: no answer {}".format(i))
                else:
                    return network_tag
            else:
                print("PROBE: timed out on", ip)
                return None

        sock = socket.socket()
        sock.settimeout(0.1)

        success = create_connection()
        if not success:
            return ip, None
        tag = probe_and_receive_tag()
        if tag is None:
            return ip, None
        ID = Probe._validate_car_tag(tag, ip)
        return ip, ID

    @staticmethod
    def _reparse_and_validate_ip(ip):
        """
        Overly complicated method, used to parse IP address ranges,
        e.g. the conversion from 192.168.1.1-100 to actual addresses
        """

        def look_for_hyphen(index, part):
            if state_flag >= 0:
                print("PROBE: only one part of the IP can be set to a range!")
                return None
            if not all(r.isdigit() for r in part.split("-")):
                print(msg, "Found non-digit in range!")
                return None
            return index

        def split_ip(ipaddr):
            split = ipaddr.split(".")
            if len(split) != 4:
                return
            return split

        def calculate_state(iplist):
            for index, part in enumerate(iplist):
                if part == "*":
                    part = "0-255"
                if "-" in part:
                    return look_for_hyphen(index, part)
                if not part.isdigit():
                    print(msg, "Found non-digit:", part)
                    return None
            return -1

        msg = "PROBE: invalid IP!"
        splip = split_ip(ip)
        if splip is None:
            return [None]

        state_flag = -1
        state_flag = calculate_state(splip)

        if state_flag >= 0:
            start, stop = splip[state_flag].split("-")
            return [".".join(splip[:state_flag] + [str(i)] + splip[state_flag+1:])
                    for i in range(int(start), int(stop))]
        elif state_flag is None:
            return [None]
        else:
            return [ip]
