from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import supervisor
import alarm
import digitalio
import board
import time

if supervisor.runtime.run_reason != supervisor.RunReason.SUPERVISOR_RELOAD:
    print("reloading")
    supervisor.reload()

supervisor.disable_ble_workflow()

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

while True:
    ble.start_advertising(advertisement)
    print("Waiting to connect")
    while not ble.connected:
        pass
    print("Connected")
    while ble.connected:
        s = uart.readline()
        if s:
            try:
                if s == b'buzz\n':
                    print("buzz!")
                    with digitalio.DigitalInOut(board.A2) as buzzer:
                        buzzer.direction = digitalio.Direction.OUTPUT
                        buzzer.value = True
                        time.sleep(10)
                        buzzer.value = False
                else:
                    print("Received ", s)
                uart.write("ok\n".encode("utf-8"))

                # wait for uart to finish writing before sleep
                time.sleep(1)

                # Deep sleep until the alarm goes off. Then restart the program.
                print("going to sleep")
                alarm_time = 15 * 60
                time_alarm = alarm.time.TimeAlarm(
                    monotonic_time=time.monotonic() + alarm_time)
                alarm.exit_and_deep_sleep_until_alarms(time_alarm)
            except Exception as e:
                result = repr(e)
                uart.write(result.encode("utf-8"))
