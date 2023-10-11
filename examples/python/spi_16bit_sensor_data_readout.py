#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=no-member

import sys
import time
import coinespy as cpy
from coinespy import ErrorCodes

# This example works with Application Board 2.0 and any sensor shuttle supports
# 16bit SPI register read

BOARD = cpy.CoinesBoard()


def verify_error(keyword=None, exit_flag=False):
    if BOARD.error_code != ErrorCodes.COINES_SUCCESS:
        print(f"{keyword} failure: {BOARD.error_code}")
        if exit_flag:
            BOARD.close_comm_interface()
            sys.exit()


# create single board instance over USB connection
def bst_init_brd_app30():
    """Init USB interface"""
    BOARD.open_comm_interface(cpy.CommInterface.USB)
    if BOARD.error_code != ErrorCodes.COINES_SUCCESS:
        print(f"Open Communication interface: {BOARD.error_code}")
        sys.exit()


if __name__ == "__main__":
    bst_init_brd_app30()

    BMA400_CS_PIN = cpy.MultiIOPin.SHUTTLE_PIN_7
    bus = cpy.SPIBus.BUS_SPI_0

    BOARD.set_shuttleboard_vdd_vddio_config(vdd_val=0, vddio_val=0)
    verify_error(keyword="set vdd, vddio", exit_flag=True)
    # 16bit SPI interface config
    BOARD.config_word_spi_bus(bus, BMA400_CS_PIN, cpy.SPISpeed.SPI_1_MHZ,
                              cpy.SPIMode.MODE0, cpy.SPITransferBits.SPI16BIT)
    verify_error(keyword="configuring spi bus", exit_flag=True)
    BOARD.set_pin_config(BMA400_CS_PIN, cpy.PinDirection.OUTPUT, cpy.PinValue.HIGH)
    verify_error(keyword="configuring Pin", exit_flag=True)

    BOARD.set_shuttleboard_vdd_vddio_config(vdd_val=3.3, vddio_val=3.3)
    verify_error(keyword="set vdd, vddio", exit_flag=True)
    time.sleep(0.2)

    # Reading up to 100 words(16 bit data = 200 bytes)
    for count in range(100):
        reg_data = BOARD.read_16bit_spi(bus, 0x00, count)
        verify_error(keyword="Device read", exit_flag=False)
        DATA = ' '.join(format(x, '04x') for x in reg_data)
        print("\nread data:\n" + DATA)

    BOARD.set_shuttleboard_vdd_vddio_config(vdd_val=0, vddio_val=0)
    BOARD.soft_reset()
    verify_error("soft reset")
    BOARD.close_comm_interface()
