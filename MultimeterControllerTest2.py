# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:30:56 2022

@author: M0188337
"""


import pyvisa as visa
import time
import csv

from measure import Measure

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
writer = csv.writer(f)

# Reset timer
startTime = time.time()

# Take measures
while time.time() < startTime + measureTime:
    # Read Value
    temp_values = v34461A.query_ascii_values(':READ?')
    
    # Create the meassure
    currMeasure = Measure(time.time(), "{:f}".format(temp_values[0]))
    
    # write data line
    writer.writerow(currMeasure.GetMeasureAsList())
    
    print("Time: " + str(currMeasure.time) + " value: " + str(currMeasure.value))

# Close export file
f.close()

# for value in temp_values:
#     print("Value: " + str(value))


# v34461A.write(':MMEMory:DOWNload:FNAMe "%s"' % ('INT:\\MyVoltMeas'))
# v34461A.write(':MMEMory:STORe:DATA %s,"%s"' % ('RDG_STORE', 'INT:\\MyVoltMeas'))
# upload = v34461A.query_binary_values(':MMEMory:UPLoad? "%s"' % ('INT:\\MyVoltMeas.csv'),'B',False)
v34461A.close()
rm.close()