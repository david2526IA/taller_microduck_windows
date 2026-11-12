import enum


class QoSDurabilityPolicy(enum.Enum):
    VOLATILE = 0
    TRANSIENT_LOCAL = 1


class QoSProfile:
    def __init__(self, depth=10, durability=QoSDurabilityPolicy.VOLATILE, **kw):
        self.depth = depth
        self.durable = durability == QoSDurabilityPolicy.TRANSIENT_LOCAL
