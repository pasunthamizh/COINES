#!/bin/sh

# This script updates APP2.0 board with Development Desktop firmware
# To put the board to bootloader mode, press SW2 button and power on
if ! [ -f "../../tools/app20-flash/app20-flash" ]; then
    make -C ../../tools/app20-flash
fi

../../tools/app20-flash/app20-flash DevelopmentDesktop_2.0_Firmware_V3.4.fwu2
