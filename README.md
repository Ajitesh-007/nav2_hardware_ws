# Autonomous Rover: ROS 2 + Nav2 + RTAB-Map + ZED2i + GPS

This repository contains the complete ROS 2 (Humble) workspace for a custom autonomous rover. The software stack integrates a custom ESP32 hardware interface, Visual-Inertial Odometry (VIO), Global Positioning (GPS), 3D SLAM, and autonomous path planning.

## 🌟 System Architecture

The robot utilizes a modular sensor fusion and navigation stack:
* **Hardware Layer (ESP32)**: A custom `ros2_control` hardware interface (`SerialHardwareInterface`) translates velocity commands into PWM bytes sent over USB serial to an ESP32, which drives the physical motors.
* **Perception (ZED 2i)**: A stereo camera providing high-frequency Visual Odometry (`/zed/zed_node/odom`), IMU data, dense 3D point clouds, and RGB-D video streams.
* **Global Positioning (Quectel L89)**: A USB GPS module providing standard NMEA coordinates (`/gps/fix`).
* **Sensor Fusion (robot_localization)**: 
  * `ekf_local`: Fuses open-loop wheel odometry and ZED2i odometry/IMU to output a highly accurate `odom -> base_link` transform.
  * `navsat_transform_node`: Translates spherical GPS coordinates into a local Cartesian frame for global localization.
* **SLAM (RTAB-Map)**: Ingests 3D point clouds and fused odometry to simultaneously map the environment in dense 3D, while projecting a 2D occupancy grid for the planner. Loop closures are saved to an SQLite database.
* **Navigation (Nav2)**: Consumes the 2D map and local point clouds (Costmaps) to dynamically plan collision-free paths and send smooth velocity commands (`cmd_vel`) to the motors.

---

## 🛠️ Hardware Setup

1. **ESP32 Firmware**: 
   - Navigate to `src/my_robot_hardware/esp32_firmware/rover_firmware/rover_firmware.ino`.
   - Update the GPIO pin definitions to match your specific motor drivers.
   - Upload the firmware to your ESP32.
2. **Physical Connections**:
   - Plug the ESP32 into the host computer via USB (typically mounts at `/dev/ttyUSB0`).
   - Plug the ZED 2i camera into a **USB 3.0** port.
   - Plug the Quectel GPS module into a USB port (e.g., `/dev/ttyUSB1`).

---

## 💻 Dependencies

Ensure you have ROS 2 Humble installed, along with the following packages:
```bash
sudo apt install ros-humble-nav2-bringup ros-humble-rtabmap-slam ros-humble-robot-localization ros-humble-nmea-navsat-driver ros-humble-ros2-control ros-humble-diff-drive-controller
```
*(You will also need the ZED SDK and `zed-ros2-wrapper` installed in a separate workspace).*

---

## 🚀 Execution Guide (How to Run)

Build the workspace and source it in every terminal before running the commands below:
```bash
cd ~/nav2_hardware_ws
colcon build --symlink-install
source install/setup.bash
```

### Terminal 1: Hardware & Motor Control
Start the `ros2_control` nodes and establish serial communication with the ESP32.
```bash
ros2 launch my_robot_description hardware.launch.py
```
*(Ensure you see `Initialized. Port: /dev/ttyUSB0` in the logs).*

### Terminal 2: ZED 2i Perception
*(Source your ZED workspace first)*
```bash
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2i
```

### Terminal 3: GPS Driver (Optional for outdoor)
Read the raw satellite data from the Quectel module and publish to `/gps/fix`.
```bash
ros2 run nmea_navsat_driver nmea_serial_driver --ros-args -p port:=/dev/ttyUSB1 -p baud:=9600
```

### Terminal 4: The Brain (Fusion, RTAB-Map SLAM, Nav2)
Launch the Extended Kalman Filters, start generating the 3D map, and spin up the path planners.
```bash
ros2 launch my_robot_navigation navigation.launch.py
```

### Terminal 5: RViz2 Visualization & Command
Open the pre-configured RViz2 Digital Twin.
```bash
ros2 run rviz2 rviz2 -d src/my_robot_description/rviz/nav2.rviz
```

---

## 🎮 How to Navigate

1. **Explore & Map (Initial Phase)**: When starting in a new environment, manually drive the rover around using `teleop_twist_keyboard` to allow RTAB-Map to construct the floorplan.
2. **Autonomous Navigation**: Once a sufficient area is mapped, click the **"2D Goal Pose"** tool in RViz2 and place a target on the generated map. 
3. **Execution**: Nav2 will calculate a global path avoiding known obstacles, dynamically avoid moving objects (like people) using local costmaps, and smoothly drive the physical rover to the destination.
