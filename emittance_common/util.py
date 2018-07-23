from .routine import white_noise


DUMMY_FRAMESIZE = (480, 640, 3)  # = 921,600 B in uint8


class CaptureDeviceMocker(object):

    """
    Mocks the interface of cv2.VideoCapture,
    produces a white noise stream.
    """

    @staticmethod
    def read():
        return True, white_noise(DUMMY_FRAMESIZE)

    def release(self):
        pass


class Table(object):

    def __init__(self, header, cell_widths):
        self.header = header
        self.widths = dict(zip(header, cell_widths))
        wd = self.widths
        self.headerrow = "|" + "|".join("{k:^{v}}".format(k=k, v=wd[k]) for k in header) + "|"
        self.separator = "+" + "+".join(("-" * wd[k] for k in header)) + "+"
        self.data = []

    def add(self, *data):
        if len(data) != len(self.header):
            raise ValueError("Invalid number of data elements. Expected: {}"
                             .format(len(self.header)))
        row = "".join("|{:^{}}".format(d, self.widths[k])
                      for d, k in zip(data, self.header))
        self.data.extend([self.separator, row + "|"])

    def get(self):
        if not self.data:
            return "Empty table"
        output = [self.separator, self.headerrow] + self.data + [self.separator]
        return "\n".join(output)
