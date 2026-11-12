"""Mini rclpy: init / ok / shutdown / spin / spin_once. El 'bus' de topicos vive en node.py."""
from .node import Node, _BUS  # noqa: F401

_ok = False
_params = {}        # parametros "del launch": {"vis_rect": True, ...}


def init(args=None):
    global _ok
    _ok = True


def ok():
    return _ok


def shutdown():
    global _ok
    _ok = False
    _BUS.wake_all()


def spin_once(node, timeout_sec=None):
    node._spin_once(0.05 if timeout_sec is None else timeout_sec)


def spin(node):
    while _ok:
        node._spin_once(0.05)
