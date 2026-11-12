from .duration import Duration


class _TimeMsg:
    """builtin_interfaces/Time: el sello de tiempo de un mensaje."""

    def __init__(self, sec=0, nanosec=0):
        self.sec, self.nanosec = sec, nanosec


class Time:
    def __init__(self, nanoseconds=0):
        self.nanoseconds = int(nanoseconds)

    def __sub__(self, o):
        if isinstance(o, Time):
            return Duration(nanoseconds=self.nanoseconds - o.nanoseconds)
        return Time(self.nanoseconds - o.nanoseconds)

    def __add__(self, o): return Time(self.nanoseconds + o.nanoseconds)
    def __ge__(self, o): return self.nanoseconds >= o.nanoseconds
    def __lt__(self, o): return self.nanoseconds < o.nanoseconds
    def to_msg(self): return _TimeMsg(self.nanoseconds // 10**9, self.nanoseconds % 10**9)
