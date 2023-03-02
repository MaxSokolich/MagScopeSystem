#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the Velocity class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

from math import sqrt

def get_magnitude(x:float, y:float, z:float) -> float:
    """
    Return the magnitude of this velocity vector

    Args:
        None
    Returns:
        Velocity's magnitude as a float
    """
    return sqrt(x**2 + y**2 + z**2)

class Velocity:
    """
    Contains information on a Robot's x and y velocity, alongside
    its "z" velocity, represented by its blurring measure.

    Args:
        x: velocity along the x coordinate
        y: velocity along the y coordinate
        z: velocity along the z coordinate
    """

    def __init__(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z
        self.mag = get_magnitude(x, y, z)




