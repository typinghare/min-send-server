class Transmittable:
    """
    Transmittable object.
    :author: James Chan
    """

    def __init__(self, byte_stream: bytearray):
        self.byte_stream = byte_stream


class TransmittableString(Transmittable):
    """
    Transmittable string object.
    :author: James Chan
    """


class TransmittableFile(Transmittable):
    """
    Transmittable string object.
    :author: James Chan
    """
