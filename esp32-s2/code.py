import alarm
import digitalio
import board
import time
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# URLs to fetch from
# CEDAR RIVER AT RENTON, WA gage height
JSON_WATER_URL = "https://waterservices.usgs.gov/nwis/iv/?format=json&indent=on&sites=12119000&parameterCd=00065&siteStatus=all"

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)
log_feed = io.get_feed("leaker01.log")
gage_height_feed = io.get_feed("leaker01.gage-height")
log_valid = False

try:
    log_valid = True
    response = requests.get(JSON_WATER_URL)
    parsed = response.json()
    datum = parsed["value"]["timeSeries"][0]["values"][0]["value"][0]
    gage_height = float(datum["value"])
    datetime = datum["dateTime"]
    location = parsed["value"]["timeSeries"][0]["sourceInfo"]["geoLocation"]["geogLocation"]
    print(io.send_data(log_feed["key"],
                       "Fetching json from {}".format(JSON_WATER_URL)))
    io.send_data(gage_height_feed["key"], gage_height, {
                 "created_at": datetime, "lat": location["latitude"], "lon": location["longitude"]})
    print("gage height is {} at {}".format(gage_height, datetime))
    print("-" * 40)

    if gage_height > 7.0:
        print("buzz!")
        with digitalio.DigitalInOut(board.A2) as buzzer:
            buzzer.direction = digitalio.Direction.OUTPUT
            buzzer.value = True
            time.sleep(10)
            buzzer.value = False
    else:
        print("no buzz :-(")
except Exception as e:
    print(repr(e))
    if log_valid:
        print(io.send_data(log_feed["key"], repr(e)))


# Deep sleep until the alarm goes off. Then restart the program.
print("going to sleep")
alarm_time = 15 * 60
time_alarm = alarm.time.TimeAlarm(
    monotonic_time=time.monotonic() + alarm_time)
alarm.exit_and_deep_sleep_until_alarms(time_alarm)


print("done")
