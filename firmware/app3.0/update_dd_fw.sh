#!/bin/sh

# This script updates APP3.0 board with Development Desktop firmware
if ! [ -f "../../tools/app_switch/app_switch" ]; then
    make -C ../../tools/app_switch
fi

../../tools/app_switch/app_switch usb_dfu_bl
dfu-util --device -,108c:ab3d -a FLASH -D DevelopmentDesktop_2.0_Firmware_v1.9.bin -R
