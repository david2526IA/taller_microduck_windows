class Duration:
    def __init__(self, seconds=0, nanoseconds=0):
        self.nanoseconds = int(seconds * 1e9) + int(nanoseconds)

    def __add__(self, o): return Duration(nanoseconds=self.nanoseconds + o.nanoseconds)
    def __sub__(self, o): return Duration(nanoseconds=self.nanoseconds - o.nanoseconds)
    def __lt__(self, o): return self.nanoseconds < o.nanoseconds
    def __ge__(self, o): return self.nanoseconds >= o.nanoseconds
