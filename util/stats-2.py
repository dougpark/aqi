# Copyright (c) 2017 Adafruit Industries
# Author: Ladyada, Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

# Import Python System Libraries
import json
import subprocess
import time

# Import Requests Library
import requests

# Import Blinka
from board import SCL, SDA
import busio
import adafruit_ssd1306

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont

# Import Colored https://pypi.org/project/colored/
from colored import fore, back, style

# api_url = 'http://localhost/admin/api.php'
api_url = 'https://www.purpleair.com/json?show=104402'

print ('running stats.py')


# Create the I2C interface.
# i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
# disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Leaving the OLED on for a long period of time can damage it
# Set these to prevent OLED burn in
DISPLAY_ON  = 10 # on time in seconds
DISPLAY_OFF = 50 # off time in seconds

# Clear display.
# disp.fill(0)
# disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
# width = disp.width
# height = disp.height
# image = Image.new('1', (width, height))

# Get drawing object to draw on image.
# draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
# draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
# padding = -2
# top = padding
# bottom = height - padding
# Move left to right keeping track of the current x position
# for drawing shapes.
x = 0

# Load nice silkscreen font
font = ImageFont.truetype('/home/pi/slkscr.ttf', 8)

# while True:
    # Draw a black filled box to clear the image.
# draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here :
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
cmd = "hostname -I | cut -d\' \' -f1 | tr -d \'\\n\'"
IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "hostname | tr -d \'\\n\'"
HOST = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "top -bn1 | grep load | awk " \
        "'{printf \"CPU Load: %.2f\", $(NF-2)}'"
CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "free -m | awk 'NR==2{printf " \
        "\"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "df -h | awk '$NF==\"/\"{printf " \
        "\"Disk: %d/%dGB %s\", $3,$2,$5}'"
Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")


# https://stackoverflow.com/a/55876665
colors = {'red':'\033[31m', 'blue':'\033[34m', 'green':'\033[32m'}
def colorprint(string, text_color = 'default', bold = False, underline = False):
    if underline == True:
            string = '\033[4m' + string
    if bold == True:
            string = '\033[1m' + string
    if text_color == 'default' or text_color in colors:
            for color in colors:
                    if text_color == color:
                            string = colors[color] + string
    else:
            raise ValueError ("Colors not in:", colors.keys())

    print(string + '\033[0m')

# http://tech.thejoestory.com/2020/09/air-quality-calculation-purple-air-api.html
def calcAQ (Cp, Ih, Il, BPh, BPl):
    a = (Ih - Il)
    b = (BPh - BPl)
    c = (Cp - BPl)
    aq = ((a/b) * c + Il)
    return aq


try:
    r = requests.get(api_url)
    data = json.loads(r.text)
    results = data['results'][0]
    SENSORLABEL = results['Label']
    # "humidity":"43","temp_f":"90","pressure":"995.51"
    PM25 = results['PM2_5Value']
    HUMIDITY = results['humidity']
    TEMP = results['temp_f']
    PRESSURE = results['pressure']

    # http://tech.thejoestory.com/2020/09/air-quality-calculation-purple-air-api.html
    pm2 = 0.0
    aqiColor = fore.WHITE
    for row in data["results"]:
        pm2 = float(row["PM2_5Value"])
        pm2 = pm2 + pm2
    pm2 = pm2 /2
    if (pm2 > 350.5):
        aq = calcAQ(pm2, 500, 401, 500, 350.5)
        aqiColor = fore.RED_3a
    elif (pm2 > 250.5):
        aq = calcAQ(pm2, 400, 301, 350.4, 250.5)
        aqiColor = fore.RED_3a
    elif (pm2 > 150.5):
        aq = calcAQ(pm2, 300, 201, 250.4, 150.5)
        aqiColor = fore.RED_3a
    elif (pm2 > 55.5):
        aq = calcAQ(pm2, 200, 151, 150.4, 55.5)
        aqiColor = fore.RED
    elif (pm2 > 35.5):
        aq = calcAQ(pm2, 150, 101, 55.4, 35.5)
        aqiColor = fore.ORANGE_1
    elif (pm2 > 12.1):
        aq = calcAQ(pm2, 100, 51, 35.4, 12.1)
        aqiColor = fore.YELLOW
    elif (pm2 > 0):
        aq = calcAQ(pm2, 50, 0, 12, 0)
        aqiColor = fore.GREEN

    DNSQUERIES = data['dns_queries_today']
    ADSBLOCKED = data['ads_blocked_today']
    CLIENTS = data['unique_clients']
except KeyError:
    time.sleep(1)
    # continue
print ("Station: " + str(SENSORLABEL))
print ("PM2.5: " + str(round(pm2)))

print (aqiColor + back.BLACK + style.BOLD + "AQI: " + str(round(aq)) + style.RESET)
#colorprint ("AQI: " + str(round(aq)),'green',True,True)
print ("Humidity: " + str(HUMIDITY))
print ("TEMP: " + str(TEMP))
print ("PRESSURE: " + str(PRESSURE))




print ("IP: " + str(IP) + " (" + HOST + ")")
print ("CPU: " + str(CPU))
print ("MEM: " + str(MemUsage))
print ("DISK: " + str(Disk))
# print ("Ads Blocked: " + str(ADSBLOCKED))
# print ("Clients:     " + str(CLIENTS))
# print ("DNS Queries: " + str(DNSQUERIES))

# draw.text((x, top), "IP: " + str(IP) +
#            " (" + HOST + ")", font=font, fill=255)
# draw.text((x, top + 8), "Ads Blocked: " +
#           str(ADSBLOCKED), font=font, fill=255)
# draw.text((x, top + 16), "Clients:     " +
#           str(CLIENTS), font=font, fill=255)
# draw.text((x, top + 24), "DNS Queries: " +
#           str(DNSQUERIES), font=font, fill=255)

# skip over original stats
# draw.text((x, top+8),     str(CPU), font=font, fill=255)
# draw.text((x, top+16),    str(MemUsage),  font=font, fill=255)
# draw.text((x, top+25),    str(Disk),  font=font, fill=255)

# Display image.
# disp.image(image)
# disp.show()
# time.sleep(DISPLAY_ON)
# disp.fill(0)
# disp.show()
# time.sleep(DISPLAY_OFF)

