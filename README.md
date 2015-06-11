# mirrorpi
Raspberry Pi based Smart Mirror

![finished product](/product.jpg)

Based on the work of Michael Teeuw (http://michaelteeuw.nl/tagged/magicmirror). 
This is a Python version that uses:
- https://pypi.python.org/pypi/ntplib/ for getting accurate and date and time information
- https://pypi.python.org/pypi/python-forecastio/ for the weather forecast
- https://pypi.python.org/pypi/geolocation-python/0.2.0 to find out the geolocation lat and lon from a city name

The UI simply uses  tkinter

![screenshot](/screenshot.png?raw=true)

How it works is simple: a monitor is used to display the program ran by the Raspberry Pi. A 2-way mirror acrylic sheet is glued on the monitor screen. Where black is displayed, the mirror acts as a normal reflective mirror. When light coloured text or images are displayed, the light from the monitor goes through and can then be seen.
