# Connect to an "eval()" service over BLE UART.

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

import random
import time
import sys

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

ble = BLERadio()

uart_connection = None

while True:
    try:
        if not uart_connection:
            logging.info("Trying to connect...")
            for adv in ble.start_scan(ProvideServicesAdvertisement):
                if UARTService in adv.services:
                    if adv.complete_name != sys.argv[1]:
                        pass
                    logging.info("Advertisement: {}".format(adv))
                    uart_connection = ble.connect(adv)
                    logging.info("Connected")
                    break
            ble.stop_scan()

        if uart_connection and uart_connection.connected:
            uart_service = uart_connection[UARTService]
            # s = random.choice(("buzz","fizz"))
            s = "buzz"
            logging.info("Chose {} to send to board".format(s))
            uart_service.write(s.encode("utf-8"))
            uart_service.write(b'\n')
            logging.info(uart_service.readline().decode("utf-8"))
            uart_connection = None
            logging.info("Going to sleep")
            time.sleep(15 * 60)
    except Exception as e:
        logging.error("Caught error: {}".format(repr(e)))
        time.sleep(1)
