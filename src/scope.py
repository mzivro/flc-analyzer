"""Oscilloscope module"""

import tkinter as tk
import numpy as np
import pyvisa
import struct
import time


class Scope():
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.scope = None
        self.ip_address = None
        self.channel = None

    def lecroy_parse_wavedesc(self, wavedesc_bytes):
        if len(wavedesc_bytes) < 346:
            tk.messagebox.showerror("Error",
                f"Got incomplete WAVEDESC block ({len(wavedesc_bytes)} bytes) expected at least 346")
            return None

        try:
            comm_order_code = struct.unpack_from("<h", wavedesc_bytes, 32)[0]
            endian_prefix = "<" if comm_order_code == 1 else ">" # 1 = LO = Little Endian

            wavedesc_format = endian_prefix + (
                "16s"   # DESCRIPTOR_NAME
                "16s"   # TEMPLATE_NAME
                "h"     # COMM_TYPE (0=BYTE, 1=WORD)
                "h"     # COMM_ORDER (0=HI/BE, 1=LO/LE)
                "l"     # WAVE_DESCRIPTOR_LENGTH (346)
                "l"     # USER_TEXT_LENGTH
                "l"     # RES_DESC1
                "l"     # TRIGTIME_ARRAY_LENGTH
                "l"     # RISK_LEVELS_LENGTH
                "l"     # RESERVED1
                "l"     # WAVE_ARRAY_1_LENGTH (bytes count)
                "l"     # WAVE_ARRAY_2_LENGTH
                "l"     # RES_DESC2
                "l"     # RES_DESC3
                "16s"   # INSTRUMENT_NAME
                "l"     # INSTRUMENT_NUMBER (Serial)
                "16s"   # TRACE_LABEL (e.g., C1)
                "h"     # RESERVED4
                "h"     # RESERVED5
                "l"     # WAVE_ARRAY_COUNT (points count)
                "l"     # PNTS_PER_SCREEN
                "f"     # FIRST_VALID_PNT (float?)
                "f"     # LAST_VALID_PNT (float?)
                "l"     # FIRST_POINT
                "l"     # SPARSING_FACTOR
                "l"     # SEGMENT_INDEX
                "l"     # SUBARRAY_COUNT
                "l"     # SWEEPS_PER_ACQ
                "h"     # POINTS_PER_PAIR
                "h"     # PAIR_OFFSET
                "f"     # VERTICAL_GAIN (V/count)
                "f"     # VERTICAL_OFFSET (V)
                "f"     # MAX_VALUE
                "f"     # MIN_VALUE
                "h"     # NOMINAL_BITS
                "h"     # NOM_SUBARRAY_COUNT
                "f"     # HORIZ_INTERVAL (s/point)
                "d"     # HORIZ_OFFSET (s from triggering) - double precision
                "d"     # PIXEL_OFFSET - double precision
            )

            header_size = struct.calcsize(wavedesc_format)

            if header_size > len(wavedesc_bytes):
                tk.messagebox.showerror("Error",
                    f"Definied WAVEDESC format ({header_size} bytes) is longer than received data ({len(wavedesc_bytes)} bytes)")
                return None

            unpacked_data = struct.unpack_from(wavedesc_format, wavedesc_bytes, 0)

            # Mapowanie rozpakowanych wartości do słownika
            params = {
                "descriptor_name": unpacked_data[0].split(b"\x00", 1)[0].decode("ascii", errors="ignore"),
                "template_name": unpacked_data[1].split(b"\x00", 1)[0].decode("ascii", errors="ignore"),
                "comm_type": unpacked_data[2],
                "comm_order": unpacked_data[3],
                "wave_descriptor_length": unpacked_data[4],
                "user_text_length": unpacked_data[5],
                "trigtime_array_length": unpacked_data[7],
                "wave_array_1_length": unpacked_data[10],
                "instrument_name": unpacked_data[14].split(b"\x00", 1)[0].decode("ascii", errors="ignore"),
                "instrument_number": unpacked_data[15],
                "trace_label": unpacked_data[16].split(b"\x00", 1)[0].decode("ascii", errors="ignore"),
                "wave_array_count": unpacked_data[19],
                "pnts_per_screen": unpacked_data[20],
                "first_valid_pnt": unpacked_data[21],
                "last_valid_pnt": unpacked_data[22],
                "first_point": unpacked_data[23],
                "sparsing_factor": unpacked_data[24],
                "segment_index": unpacked_data[25],
                "subarray_count": unpacked_data[26],
                "sweeps_per_acq": unpacked_data[27],
                "points_per_pair": unpacked_data[28],
                "pair_offset": unpacked_data[29],
                "vertical_gain": unpacked_data[30],
                "vertical_offset": unpacked_data[31],
                "max_value": unpacked_data[32],
                "min_value": unpacked_data[33],
                "nominal_bits": unpacked_data[34],
                "nom_subarray_count": unpacked_data[35],
                "horiz_interval": unpacked_data[36],
                "horiz_offset": unpacked_data[37],
                "pixel_offset": unpacked_data[38],
                "endian_prefix": endian_prefix
            }

            if params["wave_array_count"] <= 0:
                tk.messagebox.showerror("Error",
                    f"Incorrect points count ({params["wave_array_count"]}) in WAVEDESC.")
                return None
            if params["vertical_gain"] == 0:
                tk.messagebox.showwarning("Warning",
                    f"Vertical gain is 0. Channel might be offline or error occured.")
            if params["horiz_interval"] <= 0:
                tk.messagebox.showerror("Error",
                    f"Incorrect horizontal interval ({params["horiz_interval"]}) in WAVEDESC.")
                return None

            return params
        except struct.error as e:
            tk.messagebox.showerror("Error",
                f"WAVEDESC unpacking failed: {e}")
            return None
        except Exception as e:
            tk.messagebox.showerror("Error",
                f"Unexpected error during WAVEDESC parsing: {e}")
            return None

    def lecroy_get_waveform(self):
        try:
            # DATA TRANSFER CONFIGURATION
            # set format data to binary, 16-bit (WORD)
            # DEF9 means using WAVEDESC block before data
            self.scope.write("COMM_FORMAT DEF9,WORD,BIN")

            # set bit order to Little Endian (LSB first) which is typical for LeCroy
            # LO = LSB first (Little Endian), HI = MSB first (Big Endian)
            # check device manual to confirm, but LO is frequent
            self.scope.write("COMM_ORDER LO")

            # === Data download ===

            self.scope.write(f"{self.channel}:WAVEFORM?")
            time.sleep(0.5)
            header = self.scope.read_bytes(12) # read "#" and count of bytes
            if header[10:11] != b"#":
                raise ValueError("Incorrect binary response header (lack of '#').")
            print(header)
            n_digits = int(header[11:12].decode("ascii"))
            num_bytes_str = self.scope.read_bytes(n_digits).decode("ascii")
            total_bytes_to_read = int(num_bytes_str)
            raw_data_bytes = self.scope.read_bytes(total_bytes_to_read)

            if len(raw_data_bytes) != total_bytes_to_read:
                tk.messagebox.showwarning("Warning", f"Expected {total_bytes_to_read} bytes, got {len(raw_data_bytes)}!")

            # WAVEDESC PARSING

            wavedesc_len = 346

            if len(raw_data_bytes) < wavedesc_len:
                raise ValueError(f"Received data is too small ({len(raw_data_bytes)} bytes) to contain full WAVEDESC ({wavedesc_len} bytes).")

            wavedesc_block = raw_data_bytes[:wavedesc_len]

            params = self.lecroy_parse_wavedesc(wavedesc_block)

            if params is None:
                raise ValueError("WAVEDESC parsing failed.")

            # EXTRACTION AND CONVERSION OF DATA

            num_points = params["wave_array_count"]
            data_bytes_expected = params["wave_array_1_length"]

            # data begins after WAVEDESC block
            waveform_raw_bytes = raw_data_bytes[wavedesc_len : wavedesc_len + data_bytes_expected]
            actual_data_bytes_read = len(waveform_raw_bytes)

            if actual_data_bytes_read != data_bytes_expected:
                tk.messagebox.showwarning("Warning",
                    f"Real data bytes count ({actual_data_bytes_read}) differs from expected ({data_bytes_expected}).")
                if params["comm_type"] == 1: # WORD (2 bajty na punkt)
                    num_points = actual_data_bytes_read // 2
                elif params["comm_type"] == 0: # BYTE (1 bajt na punkt)
                    num_points = actual_data_bytes_read
                else:
                    raise ValueError(f"Unknown data type (comm_type={params["comm_type"]}).")

            if params["comm_type"] == 1:  # WORD (int16)
                data_format = params["endian_prefix"] + str(num_points) + "h" # "h" = signed short (16-bit)
                bytes_per_point = 2
            elif params["comm_type"] == 0: # BYTE (int8)
                data_format = params["endian_prefix"] + str(num_points) + "b" # "b" = signed char (8-bit)
                bytes_per_point = 1
            else:
                raise ValueError(f"Unsupported data type in WAVEDESC (COMM_TYPE = {params["comm_type"]})")

            if actual_data_bytes_read < num_points * bytes_per_point:
                raise ValueError(f"Insufficient bytes count ({actual_data_bytes_read}) to unpack {num_points} points of type {"WORD" if bytes_per_point==2 else "BYTE"}.")

            adc_values = np.array(struct.unpack(data_format, waveform_raw_bytes[:num_points * bytes_per_point]))

            # scale data to physical values
            vertical_gain = params["vertical_gain"]
            vertical_offset = params["vertical_offset"]
            horiz_interval = params["horiz_interval"]
            horiz_offset = params["horiz_offset"]

            voltage_data = (adc_values * vertical_gain) - vertical_offset
            time_data = (np.arange(num_points) * horiz_interval) + horiz_offset

            return time_data, voltage_data
        except ValueError as e:
            tk.messagebox.showerror("Data processing error", f"{e}")
            return None, None
        except struct.error as e:
            error_text = f"""
            Binary data unpacking error: {e}

            Possible causes:
             - incorrect byte order (COMM_ORDER)
             - wrong data format (COMM_FORMAT)
             - incomplete data
            """
            tk.messagebox.showerror("Error", error_text)
            return None, None
        except Exception as e:
            tk.messagebox.showerror("Unexpected error during waveform extraction", f"{e}")
            return None, None

    def get_waveform(self, ip_address, channel):
        self.ip_address = ip_address
        self.channel = channel

        time = None
        voltage = None

        try:
            self.scope = self.rm.open_resource(f"TCPIP0::{self.ip_address}::INSTR")
            self.scope.timeout = 10000

            identity = self.scope.query("*IDN?")

            if "LECROY" in identity:
                time, voltage = self.lecroy_get_waveform()
            else:
                tk.messagebox.showerror("Error", f"This oscilloscope {identity} is not supported!")
        except pyvisa.errors.VisaIOError as e:
            error_text = f"""
            VISA I/O error: {e}

            Check if:
            1. Oscilloscope is online and connected to your computer?
            2. Oscilloscope ip address {self.ip_address} is correct?
            3. Ocilloscope have remote control mode enabled? (for example LXI, VXI-11)
            4. Firewall does not block VISA ports? (usually 111 or 5025)
            """
            tk.messagebox.showerror("VISA error", error_text)
        except Exception as e:
            tk.messagebox.showerror("Unexpected error", f"{e}")
        finally:
            if self.scope:
                self.scope.close()

            return time, voltage
