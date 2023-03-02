#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing the FPSCounter class

@authors: Max Sokolich, Brennan Gallamoza, Luke Halko, Trea Holley,
          Alexis Mainiero, Cameron Thacker, Zoe Valladares
"""

import time


class FPSCounter:
    """
    Class for managing the FPS of the microbot tracker

    Args:
        None
    """

    def __init__(self):
        self.t0 = time.time()
        self.t1 = self.t0
        self.fps = 0

    def update(self):
        """
        Updates the current FPS of the tracker based on the curren time

        Args:
            None
        """
        self.t1 = time.time()
        try:
            self.fps = 1 / (self.t1 - self.t0)
        except ZeroDivisionError:
            self.fps = 0
        self.t0 = self.t1

    def get_fps(self):
        """
        Returns the current FPS of the tracker

        Args:
            None
        """
        return self.fps

