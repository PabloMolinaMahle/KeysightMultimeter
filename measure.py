# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 15:03:09 2022

@author: M0188337
"""

class Measure:
    # Constructor
    def __init__(myMeasure, time, value):
        myMeasure.time = time
        myMeasure.value = value
        
    def GetMeasureAsList(myMeasure):
        
        measureList = []
        measureList.append(myMeasure.time)
        measureList.append(myMeasure.value.replace(".", ","))
        
        return measureList