import ustruct
import ubinascii

from network import Bluetooth
from ucollections import namedtuple


__version__ = b'0.5.0'


RuuviTagURL = namedtuple('RuuviTagURL', (
    'mac',
    'rssi',
    'format',
    'humidity',
    'temperature',
    'pressure',
    'id',
))


RuuviTagRAW = namedtuple('RuuviTagRAW', (
    'mac',
    'rssi',
    'format',
    'humidity',
    'temperature',
    'pressure',
    'acceleration_x',
    'acceleration_y',
    'acceleration_z',
    'battery_voltage',
    'power_info',
    'movement_counter',
    'measurement_sequence',
))


class RuuviTagBase:
    def __init__(self, whitelist=None):
        self._whitelist = whitelist
        self._blacklist = []
        self.bluetooth = Bluetooth()
        self.bluetooth.deinit()

    def __repr__(self):
        return '{}(whitelist={!r}, blacklist={!r})'.format(
            type(self).__name__, self._whitelist, self._blacklist)

    @property
    def blacklist(self):
        return self._blacklist

    @blacklist.setter
    def blacklist(self, value):
        self._blacklist = value

    def get_tag(self, mac, adv):
        data = self.get_data(adv)

        if data is None:
            self._blacklist.append(mac)
            return None

        data = self.decode_data(*data)

        # Select namedtuple for URL or RAW format
        if data[0] in [2, 4]:
            tag = RuuviTagURL
        else:
            tag = RuuviTagRAW
            if data[0] == 3:
                # Fill missing measurements from RAW 1
                # format with None
                data = data + (None, ) * 3

        return tag(mac.decode('utf-8'), adv.rssi, *data)

    def get_data(self, adv):
        data = self.get_data_format_2and4(adv)

        if data is not None:
            return (2, data)

        data = self.get_data_format_raw(adv)

        if data is not None:
            return data

    @staticmethod
    def get_data_format_2and4(adv):
        """
        Test if device data is in data format 2 or 4.

        Returns measurement data or None it not in format 2 or 4.
        """
        data = adv.data.decode('utf-8')
        try:
            index = data.find('ruu.vi/#')
            if index > -1:
                return data[(index + 8):]
            else:
                index = data.find('r/')
                if index > -1:
                    return data[(index + 2):]
                return None
        except Exception:
            return None

    def get_data_format_raw(self, adv):
        """Test if device data is in data raw format 3 or 5.

        Returns decoded measurements from the manufacturer data
        or None it not in format 3 or 5.

        The bluetooth device is necessary to get the manufacturer data.
        """
        raw_data_formats = [3, 5]

        try:
            data = self.bluetooth.resolve_adv_data(
                adv.data, Bluetooth.ADV_MANUFACTURER_DATA
            )
        except TypeError:
            return None

        # Only RuuviTags
        if data[:2] != b'\x99\x04':
            return None

        # Only data format 3 and 5 (raw)
        if data[2] not in raw_data_formats:
            return None

        return (data[2], data)

    def decode_data(self, data_format, data):
        if data_format in (2, 4):
            return self.decode_data_format_2and4(data)
        elif data_format == 3:
            return self.decode_data_format_3(data)
        elif data_format == 5:
            return self.decode_data_format_5(data)

    @staticmethod
    def decode_data_format_2and4(data):
        """RuuviTag URL decoder"""
        data = data.encode()
        if len(data) > 8:
            # identifier = data[8:]
            data = data[:8]
        decoded = ubinascii.a2b_base64(data)

        data_format = decoded[0]
        humidity = decoded[1] / 2
        temperature = (decoded[2] & 127) + decoded[3] / 100
        pressure = ((decoded[4] << 8) + decoded[5]) + 50000

        return (data_format, humidity, temperature, pressure)

    @staticmethod
    def decode_data_format_3(data):
        """RuuviTag RAW 1 decoder"""
        humidity = data[3] / 2

        temperature = data[4] + data[5] / 100
        if temperature > 128:
            temperature -= 128
            temperature = round(0 - temperature, 2)

        pressure = ustruct.unpack('!H', data[6:8])[0] + 50000

        acceleration_x = ustruct.unpack('!h', data[8:10])[0]
        acceleration_y = ustruct.unpack('!h', data[10:12])[0]
        acceleration_z = ustruct.unpack('!h', data[12:14])[0]

        battery_voltage = ustruct.unpack('!H', data[14:16])[0]

        return (3, humidity, temperature, pressure, acceleration_x,
                acceleration_y, acceleration_z, battery_voltage)

    @staticmethod
    def decode_data_format_5(data):
        """RuuviTag RAW 2 decoder"""
        temperature = ustruct.unpack('!h', data[3:5])[0] * 0.005

        humidity = ustruct.unpack('!H', data[5:7])[0] * 0.0025

        pressure = ustruct.unpack('!H', data[7:9])[0] + 50000

        acceleration_x = ustruct.unpack('!h', data[9:11])[0]
        acceleration_y = ustruct.unpack('!h', data[11:13])[0]
        acceleration_z = ustruct.unpack('!h', data[13:15])[0]

        power_bin = bin(ustruct.unpack('!H', data[15:17])[0])[2:]
        battery_voltage = int(power_bin[:11], 2) + 1600
        tx_power = int(power_bin[11:], 2) * 2 - 40

        movement_counter = data[18]

        measurement_sequence = ustruct.unpack('!H', data[18:20])[0]

        return (5, humidity, temperature, pressure, acceleration_x,
                acceleration_y, acceleration_z, battery_voltage, tx_power,
                movement_counter, measurement_sequence)
