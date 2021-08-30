
import sys
import platform
import os

print(os.uname().machine)

print(platform.python_version())

height = {
    'OLO': 120,
    'Daniil': 185,
    'Thay': 180
}

for key, length in height.items():
    meters = length / 100
    min_height = min(height.values())
    print("The height of " + f"{key}" + " is " + f"{meters}" + " meters")
    if length == min_height:
        print(f"{key}" + " is the shortest of them all!")
