# Raspberry Pi
# SysInfo
# August 2021

import subprocess
import sys
import platform
import os

print("OS machine: " + os.uname().machine)
print("OS: " + str(os.uname()))
print("platform: ", platform.platform())
print("Processor: ", platform.processor())
print("Architecture: ", platform.architecture())

print("Python Impl: ", platform.python_implementation())

print("Python verson: " + platform.python_version())

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

print(IP)
print("Host: " + HOST)
print("CPU: " + CPU)
print("Mem: " + MemUsage)
print("Disk: " + Disk)
