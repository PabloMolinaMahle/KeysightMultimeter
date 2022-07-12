# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 16:22:03 2022

@author: M0188337
"""
from PyQt5 import QtWidgets, uic
import sys


from PyQt5.QtWidgets import QApplication, QWidget,QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem, QHeaderView
from PyQt5 import QtCore


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback

import pyvisa as visa
import time
import csv

from measure import Measure
from datetime import datetime


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done



class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('GUI.ui', self) # Load the .ui file
        
        # 
        self.isTakingMeasures = False
        
        # Database and data files
        self.dataFile = '(\",\")'
        
        # Subscribe to button events
        self.selectFileBtn.clicked.connect(self.SelectFile)
        self.newFileBtn.clicked.connect(self.NewFie)
        self.startBtn.clicked.connect(self.StartReading)

        # Clean plain text edit
        self.outputPlainTextEdit.clear()
        
        # Show the GUI on screen
        self.show() # Show the GUI
        
        self.threadpool = QThreadPool()
        
    def StartReading(self):
        # Instrument connection
        rm = visa.ResourceManager()
        v34461A = rm.open_resource('USB0::0x2A8D::0x1301::MY59003715::0::INSTR')
        
        if self.isTakingMeasures:
            self.isTakingMeasures = False
        
        if v34461A is None:
            self.outputPlainTextEdit.appendPlainText("DEVICE NOT CONNECTED!")
        else:
            self.outputPlainTextEdit.appendPlainText("Device detected: v34461A")
            
            if not self.isTakingMeasures:
                
                # Set flag
                self.isTakingMeasures = True
                
                # Change button text
                self.startBtn.setText("Pause")
                
                app.processEvents()
                
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
    
                # # Take measures
                print("LLamada al threat.")
                worker = Worker(self.TakeAMeassure, v34461A, writer) # Any other args, kwargs are passed to the run function
                worker.signals.result.connect(self.print_output)
                worker.signals.finished.connect(self.thread_complete)
                worker.signals.progress.connect(self.progress_fn)
                
                # Execute
                self.threadpool.start(worker)
                
                print("LLamada al threat.")
                
                # while time.time() < startTime + measureTime:
                #     thread = Thread(target = self.TakeAMeassure, args = (v34461A, writer))
                
                #     thread.start()
                
                #     # Wait fo thread to finish
                #     thread.join()
                
                # self.TakeAMeassure(v34461A, writer)
        
                # Close export file
                f.close()
        
                # for value in temp_values:
                #     print("Value: " + str(value))
        
        
                # v34461A.write(':MMEMory:DOWNload:FNAMe "%s"' % ('INT:\\MyVoltMeas'))
                # v34461A.write(':MMEMory:STORe:DATA %s,"%s"' % ('RDG_STORE', 'INT:\\MyVoltMeas'))
                # upload = v34461A.query_binary_values(':MMEMory:UPLoad? "%s"' % ('INT:\\MyVoltMeas.csv'),'B',False)
                v34461A.close()
                rm.close()
    
    def progress_fn(self, n):
        print("%d%% done" % n)
        
    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")
    
    def SelectFile(self):
        pass
    
    def NewFie(self):
        
        pass
    
    
    def TakeAMeassure(self, device, writer, progress_callback):

        # Read Value
        temp_values = device.query_ascii_values(':READ?')
        
        # Create the meassure
        currMeasure = Measure(self.processTime(), "{:f}".format(temp_values[0]))
        
        # write data line
        # writer.writerow(currMeasure.GetMeasureAsList())
        
        print("Measure list: time: " + currMeasure.GetMeasureAsList()[0] + " value: " + currMeasure.GetMeasureAsList()[1])
        progress_callback.emit(currMeasure.GetMeasureAsList()[1])
        # app.processEvents()
        
        # if self.isTakingMeasures:
        #     self.TakeAMeassure(device, writer)
    
    # Method to process time variable
    def processTime(self):
        
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
    
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()