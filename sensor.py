'''
Created on 2 nov. 2019

@author: sagfcp
'''

from threading import Thread
import time, random
import multiprocessing as mp

class sensor(Thread):
    def __init__(self, queue, fragment, series, unit, interval, initial_value, min, max, label):
        Thread.__init__(self)
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
        self.task_queue = queue
        self.start()
    def run(self):
        while True:
            self.value = random.gauss(self.value, abs(1 - abs(self.value_setpoint - self.value) / self.value_setpoint) * 5 + 1)
            message = "200," + self.fragment + "," + self.series + "," + str(round(self.value, 1)) + "," + self.unit
            try:
                #self.connection.publish("s/us", message, True)
                print(f"Will send {message}")
                self.task_queue.put(message)
            except Exception as e:
                print(f"Unable to publish {message}. Reason is: {e}")
            if self.value > self.max and not self.label + "TooHigh" in self.alarms:
                #self.connection.publish("s/us", "302," + self.label + "TooHigh," + self.label + " is too high!", True)
                self.task_queue.put(f"302,{self.label}TooHigh,{self.label} is too high!")
                self.alarms[self.label + "TooHigh"] = True
            if self.value <= self.max and self.label + "TooHigh" in self.alarms:
                #self.connection.publish("s/us", "306," + self.label + "TooHigh", True)
                self.task_queue.put(f"306,{self.label}TooHigh")
                del self.alarms[self.label + "TooHigh"]
            if self.value < self.min and not self.label + "TooLow" in self.alarms:
                #self.connection.publish("s/us", "302," + self.label + "TooLow," + self.label + " is too low!", True)
                self.task_queue.put(f"302,{self.label}TooLow,{self.label} is too low!")
                self.alarms[self.label + "TooLow"] = True
            if self.value >= self.min and self.label + "TooLow" in self.alarms:
                #self.connection.publish("s/us", "306," + self.label + "TooLow", True)
                self.task_queue.put(f"306,{self.label}TooLow")
                del self.alarms[self.label + "TooLow"]
            time.sleep(self.interval)
        