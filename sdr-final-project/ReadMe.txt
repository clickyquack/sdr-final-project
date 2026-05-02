Open Gazebo Simulation: ros2 launch sdr-final-project rect_world_gz.launch.py
Open Controller Input: ros2 launch sdr-final-project joy_teleop.launch.py
Open Camera: ros2 run sdr-final-project camera_viewer
Open Navigation (Physical): ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/turtlebot3_ws/src/sdr-final-project/map.yaml
Open Navigation (Simulation): ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/turtlebot3_ws/src/sdr-final-project/mapsim.yaml
