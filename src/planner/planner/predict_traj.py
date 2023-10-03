#!/usr/bin/env python3

import math
import numpy as np
from custom_message.msg import ControlInputs, State, FullState, Coordinate, Path
import time
import matplotlib.pyplot as plt

"""
The intent of this file is to predict the trajectory of a pure pursuit controller given the start, end position and car model
"""

# Controller Params
WB = 2.9  # [m] Wheel base of vehicle
Lf = 20  # [m] look-ahead distance

# Model params
max_steer = np.radians(30.0)  # [rad] max steering angle
max_speed = 10 # [m/s]
min_speed = 0.0 # [m/s]
L = 2.9  # [m] Wheel base of vehicle
Lr = L / 2.0  # [m]
Lf = L - Lr
Cf = 160.0 * 2.0  # N/rad
Cr = 170.0 * 2.0  # N/rad
Iz = 225.0  # kg/m2
m = 150.0  # kg
c_a = 1.36
c_r1 = 0.01

def predict_trajectory(initial_state: State, target):
    traj = []
    traj.append(Coordinate(x=initial_state.x, y=initial_state.y))
    cmd = ControlInputs()
    old_time = time.time()

    cmd.throttle, cmd.delta = pure_pursuit_steer_control(target, initial_state)
    new_state, old_time = nonlinear_model_callback(initial_state, cmd, old_time)
    traj.append(Coordinate(x=new_state.x, y=new_state.y))

    while dist(point1=(traj[-1].x, traj[-1].y), point2=target) > 5:

        cmd.throttle, cmd.delta = pure_pursuit_steer_control(target, new_state)
        new_state, old_time = nonlinear_model_callback(new_state, cmd, old_time)
        traj.append(Coordinate(x=new_state.x, y=new_state.y))

    return traj

def nonlinear_model_callback(initial_state: State, cmd: ControlInputs, old_time: float):
        dt = 0.1
        state = State()
        #dt = time.time() - old_time
        cmd.delta = np.clip(np.radians(cmd.delta), -max_steer, max_steer)

        beta = math.atan2((Lr * math.tan(cmd.delta) / L), 1.0)
        vx = initial_state.v * math.cos(beta)
        vy = initial_state.v * math.sin(beta)

        Ffy = -Cf * ((vy + Lf * initial_state.omega) / (vx + 0.0001) - cmd.delta)
        Fry = -Cr * (vy - Lr * initial_state.omega) / (vx + 0.0001)
        R_x = c_r1 * abs(vx)
        F_aero = c_a * vx ** 2 # 
        F_load = F_aero + R_x #
        state.omega = initial_state.omega + (Ffy * Lf * math.cos(cmd.delta) - Fry * Lr) / Iz * dt
        vx = vx + (cmd.throttle - Ffy * math.sin(cmd.delta) / m - F_load / m + vy * state.omega) * dt
        vy = vy + (Fry / m + Ffy * math.cos(cmd.delta) / m - vx * state.omega) * dt

        state.yaw = initial_state.yaw + state.omega * dt
        state.yaw = normalize_angle(state.yaw)

        state.x = initial_state.x + vx * math.cos(state.yaw) * dt - vy * math.sin(state.yaw) * dt
        state.y = initial_state.y + vx * math.sin(state.yaw) * dt + vy * math.cos(state.yaw) * dt

        state.v = math.sqrt(vx ** 2 + vy ** 2)
        state.v = np.clip(state.v, min_speed, max_speed)

        return state, time.time()

def pure_pursuit_steer_control(target, pose):
        
    alpha = normalize_angle(math.atan2(target[1] - pose.y, target[0] - pose.x) - pose.yaw)

    # this if/else condition should fix the buf of the waypoint behind the car
    if alpha > np.pi/2.0:
        delta = max_steer
    elif alpha < -np.pi/2.0: 
        delta = -max_steer
    else:
        # ref: https://www.shuffleai.blog/blog/Three_Methods_of_Vehicle_Lateral_Control.html
        delta = normalize_angle(math.atan2(2.0 * WB *  math.sin(alpha), Lf))
    
    # decreasing the desired speed when turning
    if delta > math.radians(10) or delta < -math.radians(10):
        desired_speed = 3
    else:
        desired_speed = 6

    delta = math.degrees(delta)
    throttle = 3 * (desired_speed-pose.v)
    return throttle, delta

@staticmethod
def dist(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)

    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance

def normalize_angle(angle):
    """
    Normalize an angle to [-pi, pi].
    :param angle: (float)
    :return: (float) Angle in radian in [-pi, pi]
    """
    while angle > np.pi:
        angle -= 2.0 * np.pi

    while angle < -np.pi:
        angle += 2.0 * np.pi

    return angle






