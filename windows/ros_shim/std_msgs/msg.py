from dataclasses import dataclass, field
from rclpy.time import _TimeMsg


@dataclass
class Header:
    stamp: object = field(default_factory=_TimeMsg)
    frame_id: str = ""


@dataclass
class String:
    data: str = ""


@dataclass
class Bool:
    data: bool = False
