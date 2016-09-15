#!/usr/bin/python
'''*****************************************************************************************************************
    Pi Temperature Station
    By John M. Wargo
    www.johnwargo.com

    This is a Raspberry Pi project that measures weather values (temperature, humidity and pressure) using
    the Astro Pi Sense HAT then uploads the data to a Weather Underground weather station.
********************************************************************************************************************'''

from __future__ import print_function

import datetime
import sys
import time
from urllib import urlencode

import urllib2

from config import Config

# ============================================================================
# Constants
# ============================================================================
# specifies how often to measure values from the Sense HAT (in minutes)
MEASUREMENT_INTERVAL = 10  # minutes
# Set to False when testing the code and/or hardware
# Set to True to enable upload of weather data to Weather Underground
WEATHER_UPLOAD = True
# the weather underground URL used to upload weather data
WU_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
# some string constants
SINGLE_HASH = "#"
HASHES = "########################################"
SLASH_N = "\n"


def c_to_f(input_temp):
    return (input_temp * 1.8) + 32


def main():
    # initialize the lastMinute variable to the current time to start
    last_minute = datetime.datetime.now().minute
    # on startup, just use the previous minute as lastMinute
    if last_minute == 0:
        last_minute = 59
    else:
        last_minute -= 1
    # infinite loop to continuously check weather values
    while 1:
        # get the current minute
        current_minute = datetime.datetime.now().minute
        # is it the same minute as the last time we checked?
        if current_minute != last_minute:
            # reset last_minute to the current_minute
            last_minute = current_minute
            # is minute zero, or divisible by 10?
            # we're only going to take measurements every MEASUREMENT_INTERVAL minutes
            if (current_minute == 0) or ((current_minute % MEASUREMENT_INTERVAL) == 0):
                # get the reading timestamp
                now = datetime.datetime.now()
                print("\n%d minute mark (%d @ %s)" % (MEASUREMENT_INTERVAL, current_minute, str(now)))

                # ========================================================
                # read the values from the sensor
                # ========================================================

                temp_c = round(calc_temp, 1)
                temp_f = round(c_to_f(calc_temp), 1)
                humidity = round(sense.get_humidity(), 2)
                # convert pressure from millibars to inHg before posting
                pressure = round(sense.get_pressure() * 0.0295300, 2)
                print("Temp: %sF (%sC), Pressure: %s inHg, Humidity: %s%%" % (temp_f, temp_c, pressure, humidity))

                # ========================================================
                # Upload the weather data to Weather Underground
                # ========================================================
                # is weather upload enabled (True)?
                if WEATHER_UPLOAD:
                    # From http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol
                    print("Uploading data to Weather Underground")
                    # build a weather data object
                    weather_data = {
                        "action": "updateraw",
                        "ID": wu_station_id,
                        "PASSWORD": wu_station_key,
                        "dateutc": "now",
                        "tempf": str(temp_f),
                        "humidity": str(humidity),
                        "baromin": str(pressure),
                    }
                    try:
                        upload_url = WU_URL + "?" + urlencode(weather_data)
                        response = urllib2.urlopen(upload_url)
                        html = response.read()
                        print("Server response:", html)
                        # do something
                        response.close()  # best practice to close the file
                    except:
                        print("Exception:", sys.exc_info()[0], SLASH_N)
                else:
                    print("Skipping Weather Underground upload")

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)  # this should never happen since the above is an infinite loop

    print("Leaving main()")


# ============================================================================
# here's where we start doing stuff
# ============================================================================
print(SLASH_N + HASHES)
print(SINGLE_HASH, "Pi Weather Station                  ", SINGLE_HASH)
print(SINGLE_HASH, "By John M. Wargo (www.johnwargo.com)", SINGLE_HASH)
print(HASHES)

# make sure we don't have a MEASUREMENT_INTERVAL > 60
if (MEASUREMENT_INTERVAL is None) or (MEASUREMENT_INTERVAL > 60):
    print("The application's 'MEASUREMENT_INTERVAL' cannot be empty or greater than 60")
    sys.exit(1)

# ============================================================================
#  Read Weather Underground Configuration Parameters
# ============================================================================
print("\nInitializing Weather Underground configuration")
wu_station_id = Config.STATION_ID
wu_station_key = Config.STATION_KEY
if (wu_station_id is None) or (wu_station_key is None):
    print("Missing values from the Weather Underground configuration file\n")
    sys.exit(1)

# we made it this far, so it must have worked...
print("Successfully read Weather Underground configuration values")
print("Station ID:", wu_station_id)
# print("Station key:", wu_station_key)

print("Initialization complete!")

# Now see what we're supposed to do next
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting application\n")
        sys.exit(0)
