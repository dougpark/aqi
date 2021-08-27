# -*- coding: utf-8 -*-

# Show air quality from PurpleAir sensor network
# https://www2.purpleair.com/community/faq#hc-access-the-json
# https://api.purpleair.com

# based on project Pi-Hole ad blocker from Adafruit
# https://learn.adafruit.com/pi-hole-ad-blocker-with-pi-zero-w?view=all#install-mini-pitft

# learn Adafruit Mini PiTFT 1.14 - mini display
# https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-setup


# Import Python System Libraries
import time
import json
import subprocess
import logging

# Import Requests Library
import requests

# Import Blinka
import digitalio
import board

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Import Colored https://pypi.org/project/colored/
# from colored import fore, back, style

# logging configuration
# debug, info, warning, error, critical
logging.basicConfig(filename='stats.log', filemode='w',
                    level=logging.WARNING, format='%(asctime)s %(message)s')
logging.info('Started')
logging.info('running stats.py')

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE,
                     width=135, height=240, x_offset=53, y_offset=40)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding + 2
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
y = top

aqiColor = "#00FF00"

# activity blinker
blinker = 0

#api_url = 'http://localhost/admin/api.php'
api_url = 'https://www.purpleair.com/json?show=104402'

# read from the api first time
api_data = requests.get(api_url)

# refresh read from url
refresh_rate = 300  # 300=60*5 = 5 minutes
refresh = refresh_rate
logging.info("Refresh rate: " + str(refresh_rate))

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype(
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
font12 = ImageFont.truetype(
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
font36 = ImageFont.truetype(
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 72)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Add buttons as inputs
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input()
buttonB = digitalio.DigitalInOut(board.D24)
buttonB.switch_to_input()

# blink activity indicator on screen


def blink():
    global blinker

    if blinker == 0:
        bx = width - font.getsize("*")[0]
        # draw.text((bx, top), "*", font=font, fill="#0000FF")
        draw.rectangle((0+40, height-10, width-40, height-7),
                       outline=0, fill=aqiColor)
        blinker = 1
    else:
        blinker = 0


def sys_info():
    global y
    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "hostname | tr -d \'\\n\'"
    HOST = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'"  # pylint: disable=line-too-long

    draw.text((x, y), IP, font=font, fill="#FFFF00")
    y += font.getsize(IP)[1]
    draw.text((x, y), CPU, font=font, fill="#FFFF00")
    y += font.getsize(CPU)[1]
    draw.text((x, y), MemUsage, font=font, fill="#00FF00")
    y += font.getsize(MemUsage)[1]
    draw.text((x, y), Disk, font=font, fill="#0000FF")
    y += font.getsize(Disk)[1]
    # draw.text((x, y), "DNS Queries: {}".format(DNSQUERIES), font=font, fill="#FF00FF")
    return


# http://tech.thejoestory.com/2020/09/air-quality-calculation-purple-air-api.html
def calcAQ(Cp, Ih, Il, BPh, BPl):
    a = (Ih - Il)
    b = (BPh - BPl)
    c = (Cp - BPl)
    aq = ((a/b) * c + Il)
    return aq


def purpleAir():
    global y, aqiColor
    global api_data, refresh

    # countdown to next api refresh
    refresh -= 1

    # PurpleAir data!
    try:
        # read from api at refresh_rate interval
        if refresh <= 0:
            refresh = refresh_rate
            api_data = requests.get(api_url)
            logging.info('New data received from PurpleAir api.')

        data = json.loads(api_data.text)
        results = data['results'][0]
        sensor_label = results['Label']
        # "humidity":"43","temp_f":"90","pressure":"995.51"
        PM25 = results['PM2_5Value']
        humidity = "Humidity: " + results['humidity']
        temp = results['temp_f']
        pressure = "Pressure: " + results['pressure']

        # http://tech.thejoestory.com/2020/09/air-quality-calculation-purple-air-api.html
        pm2 = 0.0

        # aqiColor = fore.WHITE
        for row in data["results"]:
            pm2 = float(row["PM2_5Value"])
            pm2 = pm2 + pm2
        pm2 = pm2 / 2

        if (pm2 > 350.5):
            aq = calcAQ(pm2, 500, 401, 500, 350.5)
            # aqiColor = fore.RED_3a
            aqiColor = "#FF0000"
        elif (pm2 > 250.5):
            aq = calcAQ(pm2, 400, 301, 350.4, 250.5)
            # aqiColor = fore.RED_3a
            aqiColor = "#FF0000"
        elif (pm2 > 150.5):
            aq = calcAQ(pm2, 300, 201, 250.4, 150.5)
            # aqiColor = fore.RED_3a
            aqiColor = "#FF0000"
        elif (pm2 > 55.5):
            aq = calcAQ(pm2, 200, 151, 150.4, 55.5)
            # aqiColor = fore.RED
            aqiColor = "#FF0000"
        elif (pm2 > 35.5):
            aq = calcAQ(pm2, 150, 101, 55.4, 35.5)
            # aqiColor = fore.ORANGE_1
            aqiColor = "#FF4500"
        elif (pm2 > 12.1):
            aq = calcAQ(pm2, 100, 51, 35.4, 12.1)
            # aqiColor = fore.YELLOW
            aqiColor = "#FFFF00"
        elif (pm2 > 0):
            aq = calcAQ(pm2, 50, 0, 12, 0)
            # aqiColor = fore.GREEN
            aqiColor = "#00FF00"
        #aqi = "AQI: " + str(round(aq))
        aqi = str(round(aq))
    except Exception as e:
        logging.warning('Error getting data from PurpleAir api.', e)
        time.sleep(1)
        return

    dx = width/2 - .5*(font.getsize(sensor_label)[0])
    draw.text((dx, y), sensor_label, font=font, fill="#FFFF00")
    y += font.getsize(sensor_label)[1]

    dx = width/2 - .5*(font36.getsize(aqi)[0])
    dy = height/2 - .5*(font36.getsize(aqi)[1])
    draw.text((dx, dy), aqi, font=font36, fill=aqiColor)
    y += font36.getsize(aqi)[1]
    # draw.text((x, y), humidity, font=font, fill="#00FF00")
    # y += font.getsize(humidity)[1]
    # draw.text((x, y), pressure, font=font, fill="#00FF00")
    # y += font.getsize(pressure)[1]

    # display time to next refresh
    # bx = width - font12.getsize(str(round(refresh)))[0]
    # draw.text((bx, top), str(round(refresh)), font=font12, fill="#0000FF")

    return


# main loop
while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # draw.rectangle((0, 0, width-1, height-1), outline="#00FF00", fill=0)

    # reset y to top
    y = top

    # if buttonA.value and buttonB.value:
    #     backlight.value = False  # turn off backlight
    # else:
    #     backlight.value = True  # turn on backlight

    if not buttonA.value:  # just button A pressed
        # display system info stats
        sys_info()
    else:
        # display purpleAir stats
        purpleAir()

    # blink activity indicator on screen
    blink()

    # draw.text((x, y), "Ads Blocked: {}".format(str(ADSBLOCKED)), font=font, fill="#00FF00")
    #y += font.getsize(str(ADSBLOCKED))[1]
    # draw.text((x, y), "Clients: {}".format(str(CLIENTS)), font=font, fill="#0000FF")
    #y += font.getsize(str(CLIENTS))[1]
    # draw.text((x, y), "DNS Queries: {}".format(str(DNSQUERIES)), font=font, fill="#FF00FF")
    #y += font.getsize(str(DNSQUERIES))[1]

    # Display image.
    disp.image(image, rotation)
    time.sleep(1)
