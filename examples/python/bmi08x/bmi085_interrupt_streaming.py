#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This example works with Application Board 3.0 with BMI085 shuttle board
# pylint: disable=no-member, too-few-public-methods, protected-access, broad-except
"""
This is a simple example of BMI085 Interrupt streaming using coinespy
"""
from enum import Enum
import coinespy as cpy
import bmi08x_common as bmi08x
from bmi08x_common import BMI08X as BMI08X_CLS
import helper_functions as hfunc


class BMI085(BMI08X_CLS):
    """ Child class of BMI08X_CLS with methods for interrupt streaming """
    def __init__(self, **kwargs):
        BMI08X_CLS.__init__(self, kwargs["bus"], kwargs["interface"])
        self.accel_stream_settings = dict(
            I2C_ADDR_PRIMARY=0x18,
            NO_OF_BLOCKS = 2,
            REG_X_LSB= [0x12, 0x00],
            NO_OF_DATA_BYTES= [6, 1],
            CHANNEL_ID=1,
            CS_PIN=cpy.MultiIOPin.SHUTTLE_PIN_8.value,
            INT_PIN=cpy.MultiIOPin.SHUTTLE_PIN_21.value,
            INT_TIME_STAMP=1,
            HW_PIN_STATE = 1,
            # SPI_TYPE = 0,
            # CLEAR_ON_WRITE = 0,
            # INTLINE_COUNT =0
        )
        self.gyro_stream_settings = dict(
            I2C_ADDR_PRIMARY=0x68,
            NO_OF_BLOCKS = 2,
            REG_X_LSB= [0x02,0x00],
            NO_OF_DATA_BYTES = [6, 1],
            CHANNEL_ID=2,
            CS_PIN=cpy.MultiIOPin.SHUTTLE_PIN_14.value,
            INT_PIN=cpy.MultiIOPin.SHUTTLE_PIN_22.value,
            INT_TIME_STAMP=1,
            HW_PIN_STATE = 0,
            # SPI_TYPE = 0,
            # CLEAR_ON_WRITE = 0,
            # INTLINE_COUNT =0
        )
        # ACCEL Range set to 16G
        self.accel_full_range = 16
        #  GYRO Range set to 250 dps
        self.gyro_full_range = 250
        self.accel_stream_config, self.accel_data_blocks = self.set_stream_settings(
            self.accel_stream_settings, bmi08x.SensorType.ACCEL)
        self.gyro_stream_config, self.gyro_data_blocks = self.set_stream_settings(
            self.gyro_stream_settings, bmi08x.SensorType.GYRO)
        self.number_of_samples = 10
        self.accel_int_config = self.set_accel_interrupt_cfg()
        self.gyro_int_config = self.set_gyro_interrupt_cfg()

    def set_stream_settings(self, sensor: dict, sensor_type: bmi08x.SensorType):
        """ API to configure Stream and Data blocks """
        stream_config = cpy.StreamingConfig()
        data_blocks = cpy.StreamingBlocks()
        if self.interface == cpy.SensorInterface.I2C:
            stream_config.Intf = cpy.SensorInterface.I2C.value
            stream_config.I2CBus = cpy.I2CBus.BUS_I2C_0.value
            stream_config.DevAddr = sensor["I2C_ADDR_PRIMARY"]

        elif self.interface == cpy.SensorInterface.SPI:
            stream_config.Intf = cpy.SensorInterface.SPI.value
            stream_config.SPIBus = cpy.SPIBus.BUS_SPI_0.value
            stream_config.CSPin = sensor["CS_PIN"]

        if sensor_type == bmi08x.SensorType.ACCEL and self.interface == cpy.SensorInterface.SPI:
            # extra dummy byte for SPI
            dummy_byte_offset = 1
        else:
            dummy_byte_offset = 0
        
        data_blocks.NoOfBlocks = sensor["NO_OF_BLOCKS"]
        for i in range(0, data_blocks.NoOfBlocks):
            data_blocks.RegStartAddr[i] = sensor["REG_X_LSB"][i]
            data_blocks.NoOfDataBytes[i] = sensor["NO_OF_DATA_BYTES"][i] + dummy_byte_offset

        stream_config.IntTimeStamp = sensor["INT_TIME_STAMP"]
        stream_config.IntPin = sensor["INT_PIN"]
    
        stream_config.HwPinState = sensor["HW_PIN_STATE"]
        # stream_config.SPIType = sensor["SPI_TYPE"]
        # stream_config.ClearOnWrite = sensor["CLEAR_ON_WRITE"]
        # if stream_config.ClearOnWrite:
        #     stream_config.ClearOnWriteConfig.DummyByte = 0
        #     stream_config.ClearOnWriteConfig.StartAddress = 0
        #     stream_config.ClearOnWriteConfig.NumBytesToClear = 0
        
        # stream_config.IntlineCount = sensor["INTLINE_COUNT"]
        # for i in range(0, stream_config.IntlineCount):
        #     stream_config.IntlineInfo[i] = sensor["INTLINE_INFO"][i]

        return (stream_config, data_blocks)

    def send_stream_settings(self, sensor: dict, sensor_type: Enum):
        """ API to send streaming settings to board based on Sensor type"""
        if sensor_type == bmi08x.SensorType.ACCEL:
            ret = self.board.config_streaming(
                sensor["CHANNEL_ID"], self.accel_stream_config, self.accel_data_blocks)
        else:
            ret = self.board.config_streaming(
                sensor["CHANNEL_ID"], self.gyro_stream_config, self.gyro_data_blocks)
        return ret

    def print_accel_gyro_data(self, sensor: dict, sensor_type, sensor_data):
        chip_id = 0
        """ To Display Accel and Gyro data after unit conversion"""
        if sensor_data:
            stream_buffer, valid_sample_count = sensor_data
            data = stream_buffer
            if data:
                print(f'\n{"ACCEL" if sensor_type == bmi08x.SensorType.ACCEL else "GYRO"} DATA \n')
                buffer_index = 0
                for idx in range(0, valid_sample_count):
                    if (idx + 5) < len(data):
                        # First 4 bytes contain packet count info
                        packet_count = 0
                        shift_value = 24
                        for j in range(4):
                            packet_count |= data[buffer_index] << shift_value
                            buffer_index += 1
                            shift_value -= 8

                        if self.interface == cpy.SensorInterface.SPI and sensor_type == bmi08x.SensorType.ACCEL:
                            # dummy byte
                            buffer_index += 1

                        # Next 6 bytes contain sensor info
                        x_data = hfunc.twos_comp(
                            (data[1 + buffer_index] << 8) | data[0 + buffer_index], 16)
                        y_data = hfunc.twos_comp(
                            (data[3 + buffer_index] << 8) | data[2 + buffer_index], 16)
                        z_data = hfunc.twos_comp(
                            (data[5 + buffer_index] << 8) | data[4 + buffer_index], 16)
                        buffer_index += 6

                        if sensor_type == bmi08x.SensorType.ACCEL:
                            unit_converted_x_data = bmi08x.lsb_to_mps2(
                                x_data, self.accel_full_range, 16)
                            unit_converted_y_data = bmi08x.lsb_to_mps2(
                                y_data, self.accel_full_range, 16)
                            unit_converted_z_data = bmi08x.lsb_to_mps2(
                                z_data, self.accel_full_range, 16)

                        elif sensor_type == bmi08x.SensorType.GYRO:
                            unit_converted_x_data = bmi08x.lsb_to_dps(x_data, self.gyro_full_range, 16)
                            unit_converted_y_data = bmi08x.lsb_to_dps(y_data, self.gyro_full_range, 16)
                            unit_converted_z_data = bmi08x.lsb_to_dps(z_data, self.gyro_full_range, 16)

                        #Next 1 byte chip_id
                        chip_id = data[buffer_index]
                        buffer_index += 1

                        # Next 6 bytes contain Time stamp
                        if sensor["INT_TIME_STAMP"] == 1:
                            time_stamp = 0
                            shift_value = 40
                            for j in range(6):
                                time_stamp |= data[buffer_index] << shift_value
                                buffer_index += 1
                                shift_value -= 8

                        if sensor_type == bmi08x.SensorType.ACCEL:
                            print(f"Accel[{packet_count}] Acc_ms2_X : {unit_converted_x_data:+.3f}"
                                  f"\tAcc_ms2_Y : {unit_converted_y_data:+.3f}"
                                  f"\tAcc_ms2_Z : {unit_converted_z_data:+.3f}  Chip_id : {chip_id} T(us): {time_stamp}")
                        elif sensor_type == bmi08x.SensorType.GYRO:
                            print(f"Gyro[{packet_count}] Gyr_DPS_X : {unit_converted_x_data:+3.2f}"
                                  f"\tGyr_DPS_Y : {unit_converted_y_data:+3.2f}"
                                  f"\tGyr_DPS_Z : {unit_converted_z_data:+3.2f} Chip_id : {chip_id} T(us): {time_stamp}")               

    def set_accel_interrupt_cfg(self):
        """ Set accel interrupt configurations """
        accel_int_config = dict()

        # Set accel interrupt pin configuration
        int_types = bmi08x.Bmi08xAccelIntTypes
        int_channels = bmi08x.Bmi08xAccelIntChannel
        accel_int_config['int_channel'] = int_channels.BMI08X_INT_CHANNEL_1
        accel_int_config['int_type'] = int_types.BMI08X_ACCEL_INT_DATA_RDY
        accel_int_config['int_pin_cfg'] = dict()
        accel_int_config['int_pin_cfg']['output_mode'] = bmi08x.BMI08X_INT_MODE_PUSH_PULL
        accel_int_config['int_pin_cfg']['lvl'] = bmi08x.BMI08X_INT_ACTIVE_HIGH

        return accel_int_config

    def set_gyro_interrupt_cfg(self):
        """ Set gyro interrupt configurations """
        gyro_int_config = dict()

        # Set gyro interrupt pin
        int_types = bmi08x.Bmi08xGyroIntTypes
        int_channels = bmi08x.Bmi08xGyroIntChannel
        gyro_int_config['int_channel'] = int_channels.BMI08X_INT_CHANNEL_3
        gyro_int_config['int_type'] = int_types.BMI08X_GYRO_INT_DATA_RDY
        gyro_int_config['int_pin_cfg'] = dict()
        gyro_int_config['int_pin_cfg']['output_mode'] = bmi08x.BMI08X_INT_MODE_PUSH_PULL
        gyro_int_config['int_pin_cfg']['lvl'] = bmi08x.BMI08X_INT_ACTIVE_HIGH
        return gyro_int_config

    def enable_disable_bmi08x_interrupt(self, enable_interrupt: bool):
        """API to enable interrupt if enable_interrupt is True and disable otherwise

        Args:
            enable_interrupt (bool):
        """
        self.accel_int_config['int_pin_cfg']['enable_int_pin'] = bmi08x.BMI08X_ENABLE if enable_interrupt else bmi08x.BMI08X_DISABLE
        # Enable accel data ready interrupt channel
        self.api_error_code = bmi08x.bmi08a_set_int_config(self, self.accel_int_config)
        self.verify_api_error("Accel Interrupt Config")

        self.gyro_int_config['int_pin_cfg']['enable_int_pin'] = bmi08x.BMI08X_ENABLE if enable_interrupt else bmi08x.BMI08X_DISABLE
        # Enable gyro data ready interrupt channel
        self.api_error_code = bmi08x.bmi08g_set_int_config(self, self.gyro_int_config)
        self.verify_api_error("Gyro Interrupt Config")


    def interrupt_streaming(self):
        """ API to execute interrupt streaming sequence"""
        accel_read_status = cpy.ErrorCodes.COINES_E_COMM_IO_ERROR
        gyro_read_status = cpy.ErrorCodes.COINES_E_COMM_IO_ERROR
        # Send streaming settings
        self.board.error_code = self.send_stream_settings(self.accel_stream_settings, bmi08x.SensorType.ACCEL)
        self.verify_error("Accel Stream settings")
        self.board.error_code = self.send_stream_settings(self.gyro_stream_settings, bmi08x.SensorType.GYRO)
        self.verify_error("Gyro Stream settings")

        # Enables 48-bit system timer
        self.board.error_code = self.board.trigger_timer(
            cpy.TimerConfig.TIMER_START.value, cpy.TimerStampConfig.TIMESTAMP_ENABLE.value)
        self.verify_error("Start timer")

        # Wait for 10 ms
        self.board.delay_milli_sec(10)

        # Enable data ready interrupts
        self.enable_disable_bmi08x_interrupt(enable_interrupt=True)

        # Start interrupt streaming
        self.board.error_code = self.board.start_stop_streaming(
            cpy.StreamingMode.STREAMING_MODE_INTERRUPT.value, cpy.StreamingState.STREAMING_START.value)
        self.verify_error("Start Interrupt streaming")

        # Read sensor data via interrupt streaming
        (self.board.error_code, accel_stream_buffer, accel_valid_sample_count) = self.board.read_stream_sensor_data(
            self.accel_stream_settings["CHANNEL_ID"], self.number_of_samples)
        accel_read_status = self.board.error_code
        self.verify_error("Read Accel stream data")

        if self.board.error_code == cpy.ErrorCodes.COINES_SUCCESS:
            (self.board.error_code, gyro_stream_buffer, gyro_valid_sample_count) = self.board.read_stream_sensor_data(
                self.gyro_stream_settings["CHANNEL_ID"], self.number_of_samples)
            gyro_read_status = self.board.error_code
        self.verify_error("Read Gyro stream data")

        # Stop interrupt streaming
        self.board.error_code = self.board.start_stop_streaming(
            cpy.StreamingMode.STREAMING_MODE_INTERRUPT.value, cpy.StreamingState.STREAMING_STOP.value)
        self.verify_error("Stop Interrupt streaming")

        # Stop Timer
        self.board.error_code = self.board.trigger_timer(
            cpy.TimerConfig.TIMER_STOP.value, cpy.TimerStampConfig.TIMESTAMP_DISABLE.value)
        self.verify_error("Stop timer")

        # print the streamed accel & gyro data
        if accel_read_status == cpy.ErrorCodes.COINES_SUCCESS:
            accel_data = [accel_stream_buffer,
                        accel_valid_sample_count]
        
            self.print_accel_gyro_data(
                self.accel_stream_settings, bmi08x.SensorType.ACCEL, accel_data)
            
        if gyro_read_status == cpy.ErrorCodes.COINES_SUCCESS:
            gyro_data = [gyro_stream_buffer, gyro_valid_sample_count]
            self.print_accel_gyro_data(
                self.gyro_stream_settings, bmi08x.SensorType.GYRO, gyro_data)

        # flush the buffer
        self.board.flush_interface()

        # Wait for 100 ms
        self.board.delay_milli_sec(100)

        # Disable data ready interrupts
        self.enable_disable_bmi08x_interrupt(enable_interrupt=False)


if __name__ == "__main__":
    bmi085 = BMI085(bus=cpy.I2CBus.BUS_I2C_0,
                    interface=cpy.SensorInterface.I2C)
    # bmi085 = BMI085(bus=cpy.SPIBus.BUS_SPI_0,interface=cpy.SensorInterface.SPI)
    bmi085.init_board()

    # Change sensor config settings as shown below
    # bmi085.accel_stream_config.I2CBus = cpy.I2CBus.BUS_I2C_0.value
    # bmi085.number_of_samples = 30
    # # Change sensor interrupt config settings as shown below
    # bmi085.accel_int_config['int_channel'] = bmi08x.Bmi08xAccelIntChannel.BMI08X_INT_CHANNEL_1

    # Set Accel power, ODR and range settings
    bmi085.set_accel_power_mode()
    acc_range = bmi085.set_accel_meas_conf()

    # Set Gyro power, ODR and range settings
    bmi085.set_gyro_power_mode()
    gyr_range = bmi085.set_gyro_meas_conf()
    print(f"Accel range: {acc_range} Gyro range: {gyr_range}")

    if bmi085.accel_cfg['POWER_MODE'] == bmi08x.BMI08X_ACCEL_PM_SUSPEND and \
       (bmi085.gyro_cfg['POWER_MODE'] == bmi08x.BMI08X_GYRO_PM_SUSPEND or \
        bmi085.gyro_cfg['POWER_MODE'] == bmi08x.BMI08X_GYRO_PM_DEEP_SUSPEND):
        print("Warning: Accel and gyro sensors are in suspend mode. Use them in active/normal mode !!")

    try:
        bmi085.interrupt_streaming()
    except Exception as e:
        print(f"Exception:{e}")
        bmi085.close_comm()
    bmi085.close_comm()
