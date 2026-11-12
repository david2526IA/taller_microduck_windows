# ROS 2 en miniatura (solo Windows)

ROS 2 Humble pide Ubuntu 22.04. Estos ficheros **imitan la parte de ROS 2 que usan los nodos de la Rayuela**
(`rclpy`, `geometry_msgs`, `std_msgs`, `sensor_msgs`, `rayuela_msgs`) dentro de un solo proceso de Python.
Con eso, `vision_node.py`, `control_node.py` y `teleop_keyboard.py` del repo oficial se ejecutan **sin cambiar
ni una linea**.

Nodo, topico, publicar y suscribirse funcionan como en ROS 2: `rclpy/node.py` es, en pequeño, lo que en ROS 2
hace el middleware (una cola por suscripcion). No es ROS 2 de verdad: no hay red entre procesos, ni
`ros2 topic`, ni `colcon`.
