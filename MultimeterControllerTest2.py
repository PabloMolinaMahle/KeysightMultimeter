# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:30:56 2022

@author: M0188337
"""

import pyvisa as visa
import time
import csv

from measure import Measure
from datetime import datetime

# Method to process time variable
def processTime():
    
    # Get current time
    currentTime = time.time()
    
    # Split time 
    realPart, decimalPart = str(currentTime).split(".")
    
    # Convert time Epoch to real time
    dateAndTime = datetime.fromtimestamp(int(realPart))
    
    # Convert date and time to excel format
    dateAndTime = str(datetime.fromtimestamp(int(realPart)).hour) + ":" + str(datetime.fromtimestamp(int(realPart)).minute) + ":" + str(datetime.fromtimestamp(int(realPart)).second)  + ","
    
    # Add decimal part
    dateAndTime += decimalPart
    
    return str(dateAndTime)

# Instrument connection
rm = visa.ResourceManager()
v34461A = rm.open_resource('USB0::0x2A8D::0x1301::MY59003715::0::INSTR')

# Configure instrument
v34461A.write(':CONFigure:VOLTage:DC')
v34461A.write(':SAMPle:COUNt %d' % (1))
# v34461A.write(':TRIGger:COUNt %G' % (1.0))
v34461A.write(':TRIGger:SOURce %s' % ('IMMediate'))

# Configure experiment
measureTime = 5 # total time measuring
measureTimeBetweenMeasures = 1 # Time between meassures

# Export file
f = open('csv_file.csv', 'w', newline='')
writer = csv.writer(f, delimiter=';')

# Reset timer
startTime = time.time()

# Take measures
while time.time() < startTime + measureTime:
    # Read Value
    temp_values = v34461A.query_ascii_values(':READ?')
    
    # Create the meassure
    currMeasure = Measure(processTime(), "{:f}".format(temp_values[0]))
    
    # write data line
    writer.writerow(currMeasure.GetMeasureAsList())
    
    print("Measure list: time: " + currMeasure.GetMeasureAsList()[0] + " value: " + currMeasure.GetMeasureAsList()[1])

# Close export file
f.close()

# for value in temp_values:
#     print("Value: " + str(value))


# v34461A.write(':MMEMory:DOWNload:FNAMe "%s"' % ('INT:\\MyVoltMeas'))
# v34461A.write(':MMEMory:STORe:DATA %s,"%s"' % ('RDG_STORE', 'INT:\\MyVoltMeas'))
# upload = v34461A.query_binary_values(':MMEMory:UPLoad? "%s"' % ('INT:\\MyVoltMeas.csv'),'B',False)
v34461A.close()
rm.close()
