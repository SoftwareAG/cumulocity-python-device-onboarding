'''
Created on 2 nov. 2019

@author: sagfcp
'''

from threading import Thread
import time, random

class sensor(Thread):
    def __init__(self, connection, fragment, series, unit, interval, initial_value, min, max, label):
        Thread.__init__(self)
        self.connection = connection
        self.fragment = fragment
        self.series = series
        self.unit = unit
        self.interval = interval
        self.value = initial_value
        self.value_setpoint = initial_value
        self.min = min
        self.max = max
        self.label = label
        self.daemon = True
        self.alarms = {}
        self.start()
    def run(self):
        while True:
            self.value = random.gauss(self.value, abs(1 - abs(self.value_setpoint - self.value) / self.value_setpoint) * 5 + 1)
            self.connection.publish("s/us", "200," + self.fragment + "," + self.series + "," + str(round(self.value, 1)) + "," + self.unit, True)
            if self.value > self.max and not self.alarms.has_key(self.label + "TooHigh"):
                self.connection.publish("s/us", "302," + self.label + "TooHigh," + self.label + " is too high!", True)
                self.alarms[self.label + "TooHigh"] = True
            if self.value <= self.max and self.alarms.has_key(self.label + "TooHigh"):
                self.connection.publish("s/us", "306," + self.label + "TooHigh", True)
                del self.alarms[self.label + "TooHigh"]
            if self.value < self.min and not self.alarms.has_key(self.label + "TooLow"):
                self.connection.publish("s/us", "302," + self.label + "TooLow," + self.label + " is too low!", True)
                self.alarms[self.label + "TooLow"] = True
            if self.value >= self.min and self.alarms.has_key(self.label + "TooLow"):
                self.connection.publish("s/us", "306," + self.label + "TooLow", True)
                del self.alarms[self.label + "TooLow"]
            time.sleep(self.interval)
        