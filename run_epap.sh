#!/bin/bash

sleep 30

cd /home/amos
source epap/bin/activate
cd Desktop/weather_epaper/
python display.py

/bin/bash