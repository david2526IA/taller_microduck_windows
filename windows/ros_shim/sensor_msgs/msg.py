from dataclasses import dataclass, field
from std_msgs.msg import Header


@dataclass
class Image:
    header: Header = field(default_factory=Header)
    height: int = 0
    width: int = 0
    encoding: str = ""
    is_bigendian: int = 0
    step: int = 0
    data: object = b""


@dataclass
class CameraInfo:
    header: Header = field(default_factory=Header)
    height: int = 0
    width: int = 0
    distortion_model: str = ""
    d: list = field(default_factory=list)
    k: list = field(default_factory=list)
    r: list = field(default_factory=list)
    p: list = field(default_factory=list)
