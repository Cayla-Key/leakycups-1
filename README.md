# leaky cups
This is a project about making cups leak on command, over the internet.

It runs on a standalone ESP32-S2 board (tested with FeatherS2). This code is in the `esp32-s2` folder.

We also played with a version that used a base station running on a computer, communicating over Bluetooth LE with an nrf52840 board (tested with Adafruit Circuit Playground Bluefruit and Feather nrf52840 Express), but this was never completed. This code (which - again - is not complete) is in the `nrf52840` folder.

Either way you will need CircuitPython 7.0.0 or later installed on the board. Earlier versions will not work.

See the architecture subdir READMEs for additional requirements for each version.
