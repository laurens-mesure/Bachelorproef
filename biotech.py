#!/usr/bin/python
import os
import time
import glob
import smtplib, ssl

import RPi.GPIO as GPIO

# Prepare temperature readout
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

probe_dir='/sys/bus/w1/devices/'
therm_sensor_folder = glob.glob(probe_dir + '28*')[0]
temperature_file = therm_sensor_folder + "/temperature"

# GPIO SETUP
water_pin=2
light_pin=17

GPIO.setmode(GPIO.BCM)

GPIO.setup(water_pin, GPIO.IN)
GPIO.setup(light_pin, GPIO.IN)

# Email setup
smtp_port=587 # SSL
smtp_server="smtp-mail.outlook.com"
sender_email=input("Type your email and press enter: ")
password = input("Type your password and press enter: ")
context = ssl.create_default_context()
message = """\
Subject: Deepwater culture system notification

The deepwater culture system needs to be topped up with water!"""

notified_state=False

def detect_water(pin):
    global notified_state

    if GPIO.input(pin):
        print("\U0001f4a6: No water detected")
        if not notified_state:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender_email, password)
                server.sendmail(sender_email, sender_email, message)
            
            notified_state=True
    else:
        print("\U0001f4a6: Water detected")
        notified_state=False

def detect_light(pin):
    if GPIO.input(pin):
        print("\U0001f4a1: Not enough light detected, turning on grow light")
    else:
        print("\U0001f4a1: Sufficient light detected, turning grow light off")

def read_temp_raw():
    f = open(temperature_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def detect_temp():
    lines = read_temp_raw()
    temp_c = float(lines[0]) / 1000.0
    print("\U0001f321: The current temperature is: %s\n" % (temp_c))

while True:
    detect_water(water_pin)
    detect_light(light_pin)
    detect_temp()

    time.sleep(10)