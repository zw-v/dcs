#!/usr/bin/python3
import json
import time, traceback, sys, datetime
import os
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
from telegraf.client import TelegrafClient

logger = TelegrafClient(host='localhost', port=8094)

last_checked = 0
interval_check = 10
sensors_fname = 'sensors.json'
settings_fname = 'settings.json'
sensor = []
data = []


def read_configs():
    global data
    with open(settings_fname, 'r') as f:
        try:
            settings = json.load(f)
        except:
            print("Failed to load settings.json")
    with open(sensors_fname, 'r') as f:
        try:
            data = json.load(f)
        except:
            print("Failed to load sensors_temp.json")

def init_sensors():
    global sensor, data
    for x in range(0, len(data)):
        try:
            sensor.append(W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, data[x]['id']))
        except:
            print("Failed to init sensor: %s" % data[x]['name'])

def read_and_push():
    global sensor, data
    for x in range(0, len(data)):
        data[x]['val'] = round(sensor[x].get_temperature(),2)
        if data[x]['val'] > data[x]['max']:
            data[x]['val'] = data[x]['max']
        if data[x]['val'] < data[x]['min']:
            data[x]['val'] = data[x]['min']
        logger.metric('temp', data[x]['val'], tags={'sensor': data[x]['name'] })
    print("sensors has been read and pushed to telegraf")


read_configs()
init_sensors()
while True:
    if time.time() - last_checked > interval_check:
        read_and_push()
        last_checked = time.time()
    time.sleep(5)