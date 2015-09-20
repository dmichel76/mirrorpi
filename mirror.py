#!/usr/bin/python

import Tkinter as tk
from Tkinter import *
import tkFont
from PIL import ImageTk, Image
import time, os, sys

WEATHER_CLOCK = 300000 # every 5 minutes (in ms) - used for updating weather info
TIME_CLOCK = 60000 # every 1 minute (in ms) - used for displaying clock
DAY_CLOCK = 1800000 # every 30 minutes - used for week forecast

LOCATION="Grove Oxfordshire" #keywords used for geolocation api

ICONS_DIR="./icons" #directory where icons are stored


def reboot():
	command = '/usr/bin/sudo /sbin/shutdown -r now'
	import subprocess
	process = subprocess.Popen(command.split(),stdout=subprocess.PIPE)
	output = process.communicate()[0]

def get_geolocation():
	# get Geolocation (lat,lng) from google
	from geolocation.google_maps import GoogleMaps
	google_maps = GoogleMaps(api_key='AIzaSyBEQ64NGaq3p_kXC7DuCj55FZdLhpPCMO8')
	location = google_maps.search(location=LOCATION)
	my_location = location.first()
	return my_location


def get_forecast(location):
	# get current temperature from forecastio
	import forecastio
	api_key = "96fde71e4fb18660642950e15945ed9f"
	forecast = forecastio.load_forecast(api_key, location.lat, location.lng)
	return forecast


def make_image(filePath, width, height):
	filePath = os.path.join(ICONS_DIR,filePath)
	img = Image.open(filePath)
	img = img.resize((width,height),Image.ANTIALIAS)
	img = ImageTk.PhotoImage(img)
	return img


def get_datetime():
	#format = "%H:%m - %A %-d %B %Y" # e.g. 20:15 - Tuesday 3 April 2015
	time_format = "%H:%M"
	date_format = "%A %-d %B %Y"
	try:	
		# get clock from internet
		import ntplib
		client = ntplib.NTPClient()
		response = client.request('pool.ntp.org')
		clock = time.strftime(time_format,time.localtime(response.tx_time))
		date = time.strftime(date_format,time.localtime(response.tx_time))
	except:
		# if internet if not available, get clock from host
		import datetime
		clock = datetime.datetime.now().strftime(time_format)
		date = datetime.datetime.now().strftime(date_format)
	return clock, date


def is_network_available():
	import shlex
	import subprocess 
	cmd=shlex.split("ping -c1 google.com")
	try:
	   output = subprocess.check_output(cmd)
	except subprocess.CalledProcessError,e:
	   return 1
	else:
	   return 0


def get_wifi_signal():
	file="/proc/net/wireless"
	fo = open(file,"r")
	lines=fo.readlines()
	fo.close()
	wifi_signal = int(float(lines[2].split()[2]))
	return wifi_signal


class App():

	def __init__(self):

		self.start_time = time.time()

		# init gui
		self.root =tk.Tk()
		self.root.attributes("-fullscreen", True) # fullscreen
		self.root.config(cursor="none")           # no mouse cursor
		self.root.configure(background='black')

		# get geolocation
		self.location = get_geolocation()

		# weather frame
		self.left_frame = self.make_frame(self.root)
		#self.left_frame.configure(background='blue')
		self.left_frame.pack(side=tk.LEFT, fill=Y, anchor=NW, padx=0, pady=50)

		self.left_frame_inner = self.make_frame(self.left_frame)
		self.left_frame_inner.pack(fill=Y)

		self.summary_label = self.make_label(self.left_frame,20)
		self.summary_label.pack(anchor=W)

		self.rain_label = self.make_label(self.left_frame,12,fg="grey")
		self.rain_label.pack(anchor=W)
	
		self.wind_label = self.make_label(self.left_frame,12,fg="grey")
		self.wind_label.pack(anchor=W)

		self.humidity_label = self.make_label(self.left_frame,12,fg="grey")
		self.humidity_label.pack(anchor=W)

		self.hourly_label = self.make_label(self.left_frame,20)
		self.hourly_label.pack(anchor=W,pady=20)

		self.weather_icon = self.make_icon(self.left_frame_inner)
		self.weather_icon.pack(side=tk.LEFT, anchor=NW,padx=0,pady=0)

		self.temperature_label = self.make_label(self.left_frame_inner,50)
		self.temperature_label.pack(side=tk.LEFT,anchor=NW,padx=50,pady=10)
		
		self.last_update_label = self.make_label(self.left_frame,12)
		self.last_update_label.pack(side=tk.BOTTOM, anchor=W)
	
		# week weather frame (days name)
		self.frame_week = self.make_frame(self.left_frame)
		#self.frame_week.configure(background='yellow')
		self.frame_week.pack(anchor=W,pady=50)

		self.frame_day=[]
		self.day_label = []
		self.day_icon = []
		self.day_img = []
		self.day_temp_max = []
		self.day_temp_min = []

		for x in range(0,7):
			self.frame_day.append(self.make_frame(self.frame_week))
			self.frame_day[x].pack(side=LEFT, padx=(0,15))

			self.day_label.append(self.make_label(self.frame_day[x],12,weight="bold"))
			self.day_label[x].pack()

			self.day_icon.append(self.make_icon(self.frame_day[x], width=35, height=35))
			self.day_img.append(make_image("default.png",35,35))
			self.day_icon[x].configure(image=self.day_img[0])		
			self.day_icon[x].pack(pady=10)

			self.day_temp_max.append(self.make_label(self.frame_day[x],12,weight="bold"))
			self.day_temp_max[x].pack()

			self.day_temp_min.append(self.make_label(self.frame_day[x],12,fg="grey"))
			self.day_temp_min[x].pack()

		# datetime frame
		self.right_frame = self.make_frame(self.root)
		#self.right_frame.configure(background='red')
		self.right_frame.pack(side=tk.RIGHT, fill=Y, anchor=NW, padx=0, pady=60)

		self.clock_label = self.make_label(self.right_frame,50)
		self.clock_label.pack(anchor=E)

		self.date_label = self.make_label(self.right_frame,20)
		self.date_label.pack(anchor=E)

		self.wifi_icon = self.make_icon(self.right_frame, width=40, height=30)
		self.wifi_icon.pack(side=tk.BOTTOM, anchor=E)

		# update loops
		self.update_weather()
		self.update_weather_week()
		self.update_datetime()
		self.update_wifi()

		# tk gui loop
		self.root.mainloop()


	def make_icon(self, parent, filePath="default.png", width=100, height=100):
		img = make_image(filePath, width=width, height=height)
		return Label(parent, image=img, width=width, height=height, background='black')		

	def make_frame(self, parent):
		f = Frame(parent, bg="black")
		return f

	def make_label(self, parent, size, fg="white", weight="normal"):
		return Label(parent, text="", bg="black", fg=fg, font=("Helvetica Neue",size, weight))


	def update_wifi(self):

		try:
			signal = get_wifi_signal()
		except:
			signal = 0

		if signal<100: 
			wifi_file="wifi_excellent.png"
			if signal<75:
				wifi_file="wifi_good.png"
				if signal<50:
					wifi_signal="wifi_fair.png"
					if signal<25:
						wifi_signal="wifi_weak.png"
						if signal<1:
							wifi_signal="wifi_no.png"

		self.wifi_img = make_image(wifi_file,40,30)
		self.wifi_icon.configure(image=self.wifi_img)		
		self.root.after(TIME_CLOCK, self.update_wifi)


	def update_weather(self):
		forecast = get_forecast(self.location)
		day_forecast = forecast.currently()
		hour_forecast = forecast.hourly()

		self.weather_img = make_image(day_forecast.icon + ".png",100,100)
		self.weather_icon.configure(image=self.weather_img)

		temperature = day_forecast.temperature
		temp = '{0:.1f}'.format(temperature)
		temp_str = str(temp) + u" \N{DEGREE SIGN}C"
		self.temperature_label.configure(text=temp_str)

		summary = day_forecast.summary
		self.summary_label.configure(text=summary)

		rain = int(day_forecast.precipProbability * 100)
		rain_str = "Chance of rain: " + str(rain) + "%"
		self.rain_label.configure(text=rain_str)

		wind = day_forecast.windSpeed #in miles/hour
		wind_str = "Wind speed: " + '{0:.1f}'.format(wind) + " mph"
		self.wind_label.configure(text=wind_str)

		humidity = int(day_forecast.humidity * 100)
		humidity_str = "Humidity: " + str(humidity) + "%"
		self.humidity_label.configure(text=humidity_str)

		hourly = hour_forecast.data[1].summary
		hourly_str = "Next hour: " + str(hourly)
		self.hourly_label.configure(text=hourly_str)

		self.start_time = time.time()
		self.root.after(WEATHER_CLOCK, self.update_weather)

	def update_weather_week(self):
		forecast = get_forecast(self.location).daily()

		for x in range(0,7):
			day_name = forecast.data[x].time.strftime("%a").upper()		
			self.day_label[x].configure(text=day_name)
			self.day_img[x] = make_image(forecast.data[x].icon + ".png",35,35)
			self.day_icon[x].configure(image=self.day_img[x])
			day_temp_max = '{0:.1f}'.format(forecast.data[x].temperatureMax)
			day_temp_max_str = str(day_temp_max) + u"\N{DEGREE SIGN}"
			self.day_temp_max[x].configure(text=day_temp_max_str)
			day_temp_min = '{0:.1f}'.format(forecast.data[x].temperatureMin)
			day_temp_min_str = str(day_temp_min) + u"\N{DEGREE SIGN}"
			self.day_temp_min[x].configure(text=day_temp_min_str)

		self.root.after(DAY_CLOCK, self.update_weather_week)

	def update_datetime(self):
		datetime = get_datetime()
		self.date_label.configure(text=datetime[1])
		self.clock_label.configure(text=datetime[0])

		# calculate elapsed time since last update
		elapsed_time = time.time() - self.start_time
		elapsed_time = int(elapsed_time/60)

		# if stuck for more than 15 mins, reboot
		if elapsed_time > 15: reboot()

		maybe_plural = "s" if elapsed_time > 1 else ""
		self.last_update_label.configure(text="last updated " + str(elapsed_time) + " min" + maybe_plural + " ago")

		self.root.after(TIME_CLOCK, self.update_datetime)

app=App()
