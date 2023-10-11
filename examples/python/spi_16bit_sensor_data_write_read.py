#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=no-member

import sys
import time
import coinespy as cpy
from coinespy import ErrorCodes

# This example works with Application Board 2.0 and any sensor shuttle supports
# 16bit SPI register read and write

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

    REG_ADDR = 0x0020
    WRITE_DATA = [0x1011]
    for count in range(5):
        # Writing data
        ret = BOARD.write_16bit_spi(bus, REG_ADDR, WRITE_DATA)
        verify_error(keyword="Device write", exit_flag=False)
        print("\nregister address: ", hex(REG_ADDR))
        print("write data:", hex(WRITE_DATA[0]))

        # Read back the data
        REG_DATA = BOARD.read_16bit_spi(bus, REG_ADDR, len(WRITE_DATA))
        verify_error(keyword="Device read", exit_flag=False)
        DATA = ' '.join(format(x, '04x') for x in REG_DATA)
        print("read data: 0x" + DATA)
        WRITE_DATA[0] = WRITE_DATA[0] + 1

    BOARD.set_shuttleboard_vdd_vddio_config(vdd_val=0, vddio_val=0)
    verify_error(keyword="set vdd, vddio", exit_flag=True)
    BOARD.soft_reset()
    verify_error("soft reset")
    BOARD.close_comm_interface()
