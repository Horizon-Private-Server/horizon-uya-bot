import logging
logger = logging.getLogger('thug.metric_manager')
logger.setLevel(logging.INFO)
from datetime import datetime, timedelta
from time import sleep
from collections import defaultdict

class MetricManager:
    def __init__(self):
        self._month = datetime.now().month
        self._year = datetime.now().year
        self._started = False
        self._udp_id = 1
        self._tcp_id = 1

        self._missing_packet_timeout = 500

        # player id -> last packet id
        self._last_packet_id = {
                'tcp': {
                    1: 0,
                    2: 0,
                    3: 0,
                    4: 0,
                    5: 0,
                    6: 0,
                    7: 0,
                },
                'udp': {
                    1: 0,
                    2: 0,
                    3: 0,
                    4: 0,
                    5: 0,
                    6: 0,
                    7: 0,
                },
        }

        self._missing_packet_tasks = {
                'tcp': {
                    1: {},
                    2: {},
                    3: {},
                    4: {},
                    5: {},
                    6: {},
                    7: {},
                },
                'udp': {
                    1: {},
                    2: {},
                    3: {},
                    4: {},
                    5: {},
                    6: {},
                    7: {},
                },
        }

    def start(self):
        logger.info("Metrics started!")
        self._started = True

    def get_udp_id(self):
        self._udp_id += 1
        # if self._udp_id == 20:
        #     self._udp_id = 22
        # elif self._udp_id == 30:
        #     return 21
        return self._udp_id - 1

    def get_tcp_id(self):
        self._tcp_id += 1
        return self._tcp_id - 1

    def update(self, mode:str, src_player, packet_id, hex_str):
        if not self._started:
            return

        if mode == 'tcp':
            ts = self.tcp_decode_hex_to_datetime(hex_str)
        elif mode == 'udp':
            ts = self.udp_decode_hex_to_datetime_8_fixed_year_month(hex_str)

        if self._last_packet_id[mode][src_player] == 0:
            self._last_packet_id[mode][src_player] = packet_id
        elif (self._last_packet_id[mode][src_player] + 1) == packet_id:
            # Correct packet order
            self._last_packet_id[mode][src_player] = packet_id
        elif packet_id < self._last_packet_id[mode][src_player]:
            logger.warning(f"{mode} {src_player} {packet_id} Out of order packet!")
            # TODO: remove from tasks if applicable
        else:
            # Incorrect order
            # Get the range of all ids between new packet and current packet
            last_packet_id = self._last_packet_id[mode][src_player]

            all_missing = list(range(last_packet_id+1, packet_id))
            logger.warning(f"{mode} {src_player} {packet_id} Missing packets: {all_missing}")
            # TODO: add tasks for missing packets

            self._last_packet_id[mode][src_player] = packet_id

        dt_received = self.ts_to_dt(ts)
        dt_now = datetime.now()

        dt_diff = dt_now - dt_received

        total_ms_difference = int(dt_diff.total_seconds() * 1000)

        logger.warning(f"{mode} {src_player} {packet_id} TOTAL MS DIFF {total_ms_difference}")


    def ts_to_dt(self, ts):
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S,%f")

    def get_ts(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

########################## TCP

    def get_tcp(self):
        return self.tcp_encode_timestamp_hex(self.get_ts())

    def tcp_encode_timestamp_hex(self, current_time:str):
        # Parse the datetime string into a datetime object
        dt_obj = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S,%f")

        # Encode each part into a hex string
        year_hex = f"{dt_obj.year:04x}"
        month_hex = f"{dt_obj.month:02x}"
        day_hex = f"{dt_obj.day:02x}"
        hour_hex = f"{dt_obj.hour:02x}"
        minute_hex = f"{dt_obj.minute:02x}"
        second_hex = f"{dt_obj.second:02x}"
        millis_hex = f"{dt_obj.microsecond // 1000:04x}"  # We take only milliseconds

        # Concatenate all parts into a single hex string (20 hex characters total)
        hex_string = year_hex + month_hex + day_hex + hour_hex + minute_hex + second_hex + millis_hex

        return hex_string.upper() + '00'

    def tcp_decode_hex_to_datetime(self, hex_str):
        # Decode each part back to its respective component
        year = int(hex_str[0:4], 16)
        month = int(hex_str[4:6], 16)
        day = int(hex_str[6:8], 16)
        hour = int(hex_str[8:10], 16)
        minute = int(hex_str[10:12], 16)
        second = int(hex_str[12:14], 16)
        millis = int(hex_str[14:18], 16)

        # Construct a datetime object
        decoded_dt = datetime(year, month, day, hour, minute, second, millis * 1000)

        # Convert back to the string format
        decoded_dt_str = decoded_dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        return decoded_dt_str

########################## UDP

    def get_udp(self):
        return self.udp_encode_datetime_to_hex_8_fixed_year_month(self.get_ts())

    def udp_encode_datetime_to_hex_8_fixed_year_month(self, current_time:str):
        # Parse the datetime string, assuming the year and month are fixed
        dt_obj = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S,%f")

        # Extract day, hour, minute, second, and milliseconds
        day = dt_obj.day            # 5 bits
        hour = dt_obj.hour          # 5 bits
        minute = dt_obj.minute      # 6 bits
        second = dt_obj.second      # 6 bits
        millis = dt_obj.microsecond // 1000  # Convert microseconds to milliseconds (10 bits)

        # Pack the values into 32 bits
        packed = (day << 27) | (hour << 22) | (minute << 16) | (second << 10) | millis

        # Convert the packed value to an 8-character hex string
        hex_string = f"{packed:08x}"
        
        return hex_string.upper()

    def udp_decode_hex_to_datetime_8_fixed_year_month(self, hex_str):
        # Convert the hex string back to a packed integer
        packed = int(hex_str, 16)

        # Unpack the values
        day = (packed >> 27) & 0x1F    # 5 bits
        hour = (packed >> 22) & 0x1F   # 5 bits
        minute = (packed >> 16) & 0x3F # 6 bits
        second = (packed >> 10) & 0x3F # 6 bits
        millis = packed & 0x3FF        # 10 bits

        # Construct the datetime object
        decoded_dt = datetime(self._year, self._month, day, hour, minute, second, millis * 1000)

        # Convert to string
        decoded_dt_str = decoded_dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        
        return decoded_dt_str



if __name__ == '__main__':
    m = MetricManager()
    for i in range(10000):
        ## TCP TESTING
        start = m.get_ts()
        encoded = m.tcp_encode_timestamp_hex(start)
        decoded = m.tcp_decode_hex_to_datetime(encoded)
        sleep(.05)
        print("TCP", start, encoded, decoded)
        assert start == decoded
        assert m.ts_to_dt(start) == m.ts_to_dt(decoded)

        ### UDP TESTING
        start = m.get_ts()
        encoded = m.udp_encode_datetime_to_hex_8_fixed_year_month(start)
        decoded = m.udp_decode_hex_to_datetime_8_fixed_year_month(encoded)
        sleep(.05)
        print("UDP", start, encoded, decoded)
        assert start == decoded
        assert m.ts_to_dt(start) == m.ts_to_dt(decoded)