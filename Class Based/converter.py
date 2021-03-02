
# class to store and convert the nano value you work with
class Nanos:

    def __init__(self, nano=None, raw=None):
        if nano is not None:
            self.raw = nano
        elif raw is not None:
            self.nano = raw
        else:
            pass

    # getter and setter so convert from nano to raw
    @property
    def raw(self):
        return self.__raw

    @raw.setter
    def raw(self, nano):
        self.__raw = int(nano) * 1000000000000000000000000000000
        self.__nano = nano

    # getter and setter to convert from raw to nano
    @property
    def nano(self):
        return self.__nano

    @nano.setter
    def nano(self, raw):
        self.__nano = int(raw) / 1000000000000000000000000000000
        self.__raw = raw
