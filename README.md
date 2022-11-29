# MuHack-Badge
Official repository for MuHack Badge.

The board features an RP2040 as main microcontroller running micropython.
Its job is to setup and stream data from the Bosh Sensor Hub BHI106B, as well as controlling the LEDs.

```Hardware/``` folder contains the KiCad project

```Software/``` folder contains the BOSS system and the sketch for the ESP32

TODOs:
 - [ ] Connect the interrupt line of BHI to the RP2040
 - [ ] Invert TX/RX of UART between ESP32 and RP2040
 - [ ] Change to a bigger footprint of ESP32 debug port
 - [ ] Maybe add two button for boot sel and reset for the ESP32
 - [ ] Change button battery footprint
 - [ ] Improve silkscreen text size
 - [ ] Add silkscreen label for many things (pinout, battery polarity, etc)
 - [ ] Expose BHI's internal I2C and interrupt line (for future sensors)
 - [ ] Move I2C pull-up resistor
 - [ ] Add led polarity
 - [ ] Remove power inductor (or change to an available one)
 - [ ] Maybe add a way to switch LEDs data line to the ESP32 instead of the RP2040
 - [ ] Docs and code comments
 - [ ] Remove the D16 Schottky Diode from the battery line
 
 Special Thanks to:
 @gcammisa and Paolino
