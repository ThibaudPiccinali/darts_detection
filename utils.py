import numpy as np

def rot_x(degree):
    return np.array([[1, 0, 0],[0, np.cos(np.radians(degree)), -np.sin(np.radians(degree))],[0, np.sin(np.radians(degree)), np.cos(np.radians(degree))]])

def rot_y(degree):
    return np.array([[np.cos(np.radians(degree)), 0, np.sin(np.radians(degree))],[0, 1, 0],[-np.sin(np.radians(degree)), 0, np.cos(np.radians(degree))]])

def rot_z(degree):
    return np.array([[np.cos(np.radians(degree)), -np.sin(np.radians(degree)), 0],[np.sin(np.radians(degree)), np.cos(np.radians(degree)), 0],[0, 0, 1]])

