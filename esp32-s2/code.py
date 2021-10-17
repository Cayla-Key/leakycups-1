import alarm
import digitalio
import board
import time
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import math
from adafruit_datetime import datetime
from adafruit_datetime import timedelta

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# URLs to fetch from
JSON_WATER_URL = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=%s&parameterCd=00060&siteStatus=all" % secrets[
    "usgs_id"]
HISTORICAL_URL = "https://nwis.waterservices.usgs.gov/nwis/iv/?format=json&sites=%s&startDT=%d-%d-%dT%d:%d-0700&endDT=%d-%d-%dT%d:%d-0700&parameterCd=00060&siteStatus=all"


def historical_url(struct):
    current_time = datetime(year=struct.tm_year, month=struct.tm_mon,
                            day=struct.tm_mday, hour=struct.tm_hour, minute=struct.tm_min)
    old_start = current_time.replace(
        year=current_time.year - secrets["time_warp_years"])
    old_end = old_start + timedelta(minutes=60)
    return HISTORICAL_URL % (secrets["usgs_id"], old_start.year, old_start.month, old_start.day, old_start.hour, old_start.minute, old_end.year, old_end.month, old_end.day, old_end.hour, old_end.minute)


print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
AIO_USERNAME = secrets["aio_username"]
AIO_KEY = secrets["aio_key"]

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(AIO_USERNAME, AIO_KEY, requests)
log_feed = io.get_feed("cup%d-dot-log" % secrets["participant_id"])
log_valid = False


def log(message):
    """log sends the string to adafruit io"""
    if log_valid:
        io.send_data(log_feed["key"], message)
        print(message)


def discharge(url):
    """gets the discharge from the given url"""
    log("Fetching json from {}".format(url))
    response = requests.get(url)
    parsed = response.json()
    datum = parsed["value"]["timeSeries"][0]["values"][0]["value"][0]
    dis = float(datum["value"])
    datum_datetime = datum["dateTime"]
    log("discharge is {} at {}".format(dis, datum_datetime))
    return dis


def buzz(seconds):
    print("buzzing for %ds" % seconds)
    with digitalio.DigitalInOut(board.A2) as buzzer:
        buzzer.direction = digitalio.Direction.OUTPUT
        buzzer.value = True
        time.sleep(seconds)
        buzzer.value = False


current_hour = 0
try:
    log_valid = True
    now_discharge = discharge(JSON_WATER_URL)

    current_time = io.receive_time()
    current_hour = current_time.tm_hour
    old_discharge = discharge(historical_url(current_time))

    old_buzz_seconds = math.sqrt(old_discharge) * secrets["scaling_factor"]
    buzz(old_buzz_seconds)

    time.sleep(4)

    now_buzz_seconds = math.sqrt(now_discharge) * secrets["scaling_factor"]
    buzz(now_buzz_seconds)

except Exception as e:
    print(repr(e))
    if log_valid:
        log(repr(e))


# Deep sleep until the alarm goes off. Then restart the program.
alarm_time = 60 * 60
if current_hour >= secrets["sleep_hour"] or current_hour < secrets["wake_hour"]:
    if current_hour > 12:
        # if the current hour is before midnight, the wake hour is actually tomorrow
        secrets["wake_hour"] += 24
    sleep_hours = secrets["wake_hour"] - current_hour
    alarm_time = sleep_hours * 60 * 60
    print("it's bed time! going to sleep for %d hours" % sleep_hours)
else:
    print("napping...")

time_alarm = alarm.time.TimeAlarm(
    monotonic_time=time.monotonic() + alarm_time)
alarm.exit_and_deep_sleep_until_alarms(time_alarm)


print("done")
