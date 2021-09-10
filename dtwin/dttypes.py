# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:57:11 2021

@author: marynaw
"""
from enum import Enum, unique

# these are types for modelling the factory. We need to distinguish between nodes that can be different types
# of factory objects. Processes are also modelled as nodes.
@unique
class dtTypes(Enum):
    NONE = 0
    MACHINE = 1
    SOURCE = 2
    EXIT = 3
    PROCESS = 4
    SENSOR = 5
    SINGLE_PART=6
    PROCESSED_PART=7
    PART=8
    TEMPERATURE=9
    VIBRATION=10
    BUFFER=11
    UNKNOWN=12
