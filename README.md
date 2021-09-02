# leaky cups
This is a project about making cups leak on command, over the internet. It runs one of two ways:
* With a base station running on a computer, communicating over Bluetooth LE with an nrf52840 board (tested with Adafruit Circuit Playground Bluefruit and Feather nrf52840 Express)
* On a standalone ESP32-S2 board (tested with FeatherS2)

Either way you will need CircuitPython 7.0.0rc0 or later installed on the board. Earlier versions will not work.

See the architecture subdir READMEs for additional requirements for each version.
