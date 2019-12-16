# sak [![kinetic](https://img.shields.io/badge/ros-melodic-blue.svg)](http://wiki.ros.org/melodic)

## prerequisites for running:
1.  Ryze Tello Edu
2.  OptiTrack camera system
3.  Robot Operating System Melodic version
4.  install tello_driver package
5.  install zbar_ros package
6.  install vrpn_client_ros or natnet_ros package

## how to use:
1.  launch **sak.launch** for starting every neccesary nodes and packages
````bash
roslaunch sak sak.launch
````
2.  run **fly_controller.py** for starting the autonomous control and the controller

## keyboard controller using:
1.  allow flip - (b)
2.  disallow flip - (n)
3.  take off - (y)
4.  land - (x)
5.  go forward - (w)
6.  go backward - (s)
7.  go left - (a)
8.  go right - (d)
9.  turn left - (q)
10. turn right - (e)
11. go up - (r)
12. go down - (f)
13. flip forward - (z)
14. flip backward - (h)


