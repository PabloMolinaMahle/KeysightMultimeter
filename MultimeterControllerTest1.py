# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 12:26:44 2022

@author: M0188337
"""


import matplotlib.pyplot as plt

# NOTE: the default pyvisa import works well for Python 3.6+
# if you are working with python version lower than 3.6, use 'import visa' instead of import pyvisa as visa

import pyvisa as visa
import time

# Instrument connection
rm = visa.ResourceManager()
v34461A = rm.open_resource('USB0::0x2A8D::0x1301::MY59003715::0::INSTR')

v34461A.write(':CONFigure:VOLTage:DC')
v34461A.write(':SAMPle:COUNt %d' % (2))
v34461A.write(':TRIGger:COUNt %G' % (2.0))
v34461A.write(':TRIGger:SOURce %s' % ('IMMediate'))
temp_values = v34461A.query_ascii_values(':READ?')
read = temp_values[0]

for value in temp_values:
    print("Value: " + str(value))

temp_values = v34461A.query_ascii_values(':FETCh?')
readings1 = temp_values[0]

v34461A.write(':MMEMory:DOWNload:FNAMe "%s"' % ('INT:\\MyVoltMeas'))
v34461A.write(':MMEMory:STORe:DATA %s,"%s"' % ('RDG_STORE', 'INT:\\MyVoltMeas'))
upload = v34461A.query_binary_values(':MMEMory:UPLoad? "%s"' % ('INT:\\MyVoltMeas.csv'),'B',False)
v34461A.close()
rm.close()

# end of untitled
