from dataclasses import dataclass, field
from geometry_msgs.msg import Point
from std_msgs.msg import Header


@dataclass
class TargetCasilla:          # mismo contenido que rayuela_msgs/msg/TargetCasilla.msg del repo oficial
    header: Header = field(default_factory=Header)
    casilla_id: int = 0
    center: Point = field(default_factory=Point)
    landing_point: Point = field(default_factory=Point)
