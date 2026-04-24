# sdr-final-project
on first installation run these in the directory first:
```
cd src
git clone -b jazzy https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b jazzy https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b jazzy https://github.com/ROBOTIS-GIT/turtlebot3.git
cd ..
colcon build --symlink-install
```

every time you open a new terminal for this run:
```
source install/setup.bash
export ROS_DOMAIN_ID=10
export TURTLEBOT3_MODEL=waffle
```
