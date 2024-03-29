# coding: utf-8
'''
Created on 12 nov. 2019

@author: sagfcp
'''

from c8y_onboard import Onboard
from sensor import sensor
from requests import ConnectionError
import sys, time, requests
import multiprocessing as mp

device_id = sys.argv[1]
device_name = sys.argv[2]

def updateFirmware(name, version, url):
    print("Updating firmware with " + name + " version " + version + " from url " + url)
    try:
        res = requests.get(url, auth = o.getAuth())
        if res.status_code != 200:
            o.publish("s/us", "502,c8y_Firmware,Unable to access firmware at URL " + url + ". Reason is: " + res.text)
        else:
            o.publish("s/us", "503,c8y_Firmware")
            o.publish("s/us", "115," + name + "," + version + "," + url)
    except (ConnectionError) as e:
        o.publish("s/us", "502,c8y_Firmware,Unable to access firmware at URL " + url + ". Reason is: " + e.strerror)
        

def updateSoftware(name, version, url):
    print("Updating software with " + name + " version " + version + " from url " + url)
    try:
        res = requests.get(url, auth = o.getAuth())
        if res.status_code != 200:
            o.publish("s/us", "502,c8y_Software,Unable to access software at URL " + url + ". Reason is: " + res.text)
        else:
            o.publish("s/us", "503,c8y_Software")
            o.publish("s/us", "116," + name + "," + version + "," + url)
    except (ConnectionError) as e:
        o.publish("s/us", "502,c8y_Software,Unable to access software at URL " + url + ". Reason is: " + e.strerror)

def operation_callback(client, userdata, message):
    message.payload = message.payload.decode("utf-8")
    values = message.payload.split(",")
    print("Received operation " + message.payload)
    if (message.payload.startswith("515,")):
        print("Processing firmware update")
        o.publish("s/us", "501,c8y_Firmware")
        updateFirmware(values[2], values[3], values[4])
    if (message.payload.startswith("516,")):
        print("Processing software update")
        o.publish("s/us", "501,c8y_Software")
        updateSoftware(values[2], values[3], values[4])


o = Onboard(device_id)
o.connect()
o.message_callback_add("s/ds", operation_callback)

o.publish("s/us", "100," + device_name + ",simpleDevice", True)
o.publish("s/us", "114,c8y_Firmware,c8y_Software", True)
o.publish("s/us", "115,factory_firmware,0.0,", True)
o.publish("s/us", "116,factory_os,0.0,,factory_ui,0.0", True)
o.publish("s/us", "117,1", True)

o.subscribe("s/ds")

task_queue = mp.Queue()

sensor(task_queue, "Temperature", "T", "°C", 5, 20, 18, 22, "Temperature")
sensor(task_queue, "Humidity", "RH", "%", 5, 50, 40, 60, "Humidity")

while True:
    print(f"Getting message from queue...")
    message = task_queue.get()
    print(f"Received {message} from queue, publishing it...")
    o.publish("s/us", message, True)

