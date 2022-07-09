import json
import RPi.GPIO as GPIO
import requests as requests

import database
from weather import getRainThisDay

with open("/home/pi/smartGardenScheduler/environment.json") as f:
    d = json.load(f)
    rainThreshold = d["rainThreshold"]
    channel = d["GPIOchannel"]
    base_url = d["base_url_Backend"]


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)


def disableAllChannels():
    GPIO.output(channel, GPIO.HIGH)


def outputServer(channel, state):
    print('outputServer')
    if state:
        if checkBeforeExecution():
            informBackend(channel, state)
            print(f"GPIO {channel}: {state}")
            GPIO.output(channel, GPIO.LOW)
    else:
        print(f"GPIO {channel}: {state}")
        informBackend(channel, state)
        GPIO.output(channel, GPIO.HIGH)


def outputWithoutInformBackend(channel, state):
    print('outputServer')
    if state:
        GPIO.output(channel, GPIO.LOW)
    else:
        GPIO.output(channel, GPIO.HIGH)


def checkBeforeExecution():
    return not (database.getStatusRuhemodus()) and getRainThisDay() < rainThreshold


def informBackend(channel, status):
    payload = {"channel": channel, "status": status}
    complete_url = base_url + '/update_status_from_py'
    requests.post(complete_url, json=payload)
