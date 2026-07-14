# docker容器查询
docker ps

# 启动容器
docker start ros2_VLA_robot

# 关闭容器
docker stop ros2_VLA_robot

# 进入容器
docker exec -it -u ros ros2_VLA_robot  bash

# 启动注册节点
ros2 run lab_robot_control registry_node 

# 启动转盘节点和注册节点
ros2 launch lab_turntable turntables.launch.py 

# 控制转盘转动

## 储液槽堆栈
ros2 topic pub --once /turntable/set_angle lab_turntable_interfaces/msg/TurntableSetAngle \
"{device_ids: [1], angle_degs: [0.0], speed: 0.0, accel: 0.0}"

## 混合堆栈
ros2 topic pub --once /turntable/set_angle lab_turntable_interfaces/msg/TurntableSetAngle \
"{device_ids: [2], angle_degs: [120.0], speed: 0.0, accel: 0.0}"

## 烧杯堆栈
ros2 topic pub --once /turntable/set_angle lab_turntable_interfaces/msg/TurntableSetAngle \
"{device_ids: [3], angle_degs: [60.0], speed: 0.0, accel: 0.0}"