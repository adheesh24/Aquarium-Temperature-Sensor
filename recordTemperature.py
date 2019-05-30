#!/usr/bin/env python
import os
import RPi.GPIO as GPIO
import sheetupdate
import datetime
from random import randint
from time import sleep
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
def sensor():
	for i in os.listdir('/sys/bus/w1/devices'):
		if i != 'w1_bus_master1':
			sensorID = i
	return sensorID

spreadsheetId = '16MJdHtQAgGz1gH5IqaWCCDCne3fU2OSi6u2NycaLXIY'
rangeName = 'A1:D'
values = {'values':[['Date','Time','Temp','Fan'],]}

sheetupdate.update_authenticate(spreadsheetId, rangeName,values)

def read(sensorID):
	fan_status = "off"
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	FAN_PIN = 21
	FAN_PIN2 = 20
	SENSOR_PIN = 4
    GPIO.setup(FAN_PIN,GPIO.OUT)
	GPIO.setup(FAN_PIN2,GPIO.OUT)

	location = '/sys/bus/w1/devices/' + sensorID + '/w1_slave'
	tfile = open(location)
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	temperatureData = secondline.split(" ")[9]
	temperature = float(temperatureData[2:])
	celsius = temperature / 1000
	fahrenheit = (celsius * 1.8) +32

	if(celsius>25):
		GPIO.output(FAN_PIN,True)
		GPIO.output(FAN_PIN2,True)
		print "Fans turned on"
		fan_status = "On"
	else:
		GPIO.output(FAN_PIN,False)
		GPIO.output(FAN_PIN2,False)
		print "Fans turned off"
		fan_status = "Off" 
	return celsius,fahrenheit,fan_status

def getTemp(sensorID):
	while True:
            for i in range(2,999):
                if read(sensorID) != None:
                        celsius = read(sensorID)[0]
			fanStatus = read(sensorID)[2]

			server = smtplib.SMTP('smtp.gmail.com',587)
			server.ehlo()
			server.starttls()
			server.ehlo()
			server.login('rasperrypiproject2019@gmail.com', 'Pi123456')
			msg = 'The water temperature is too cold. Please turn OFF the fans.'
			if(celsius <25):
				print "Notification sent"
				server.sendmail('rasperrypiproject2019@gmail.com','adheeshk93@gmail.com',msg)
				server.quit()
                        time = '{:%H:%M:%S}'.format(datetime.datetime.now())
			date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

                        values = {'values':[[date,time,celsius,fanStatus],]}
                        rangeName = 'A'+str(i) + ':D'

                        sheetupdate.update_authenticate(spreadsheetId,rangeName,values)
                        sleep(1)
			print "Current temperature : %0.3f C" %read(sensorID)[0]
			print" Current temperature:%0.3f F" %read(sensorID)[1]

def kill():
	quit()
if __name__ == '__main__':
	try:
		serialNum = sensor()
		getTemp(serialNum)
	except KeyboardInterrupt:
		kill()

