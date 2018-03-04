import ubinascii

from network import Bluetooth
from ucollections import namedtuple


__version__ = b'0.4.0'


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
        raw_data_formats = [b'03', b'05']

        try:
            mfg_data = self.bluetooth.resolve_adv_data(
                adv.data, Bluetooth.ADV_MANUFACTURER_DATA
            )
            data = ubinascii.hexlify(mfg_data)
        except TypeError:
            return None

        # Only RuuviTags
        if data[:4] != b'9904':
            return None

        # Only data format 3 and 5 (raw)
        if data[4:6] not in raw_data_formats:
            return None

        return (int(data[4:6], 16), data)

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
        humidity = int(data[6:8], 16) / 2

        temperature_str = data[8:12]
        temperature = int(temperature_str[:2], 16)
        temperature += int(temperature_str[2:4], 16) / 100
        if temperature > 128:
            temperature -= 128
            temperature = 0 - temperature

        pressure = int(data[12:16], 16) + 50000

        acceleration_x = int(data[16:20], 16)
        if acceleration_x > 32767:
            acceleration_x -= 65536

        acceleration_y = int(data[20:24], 16)
        if acceleration_y > 32767:
            acceleration_y -= 65536

        acceleration_z = int(data[24:28], 16)
        if acceleration_z > 32767:
            acceleration_z -= 65536

        battery_voltage = int(data[28:32], 16)

        return (3, humidity, temperature, pressure, acceleration_x,
                acceleration_y, acceleration_z, battery_voltage)

    @staticmethod
    def decode_data_format_5(data):
        """RuuviTag RAW 2 decoder"""
        temperature = int(data[6:10], 16)
        if temperature > 32767:
            temperature -= 65536
        temperature = temperature * 0.005

        humidity = int(data[10:14], 16) / 400

        pressure = int(data[14:18], 16) + 50000

        acceleration_x = int(data[18:22], 16)
        if acceleration_x > 32767:
            acceleration_x -= 65536

        acceleration_y = int(data[22:26], 16)
        if acceleration_y > 32767:
            acceleration_y -= 65536

        acceleration_z = int(data[26:30], 16)
        if acceleration_z > 32767:
            acceleration_z -= 65536

        power_int = int(data[30:34], 16)
        battery_voltage = int(bin(power_int)[2:13], 2) + 1600
        tx_power = int(bin(power_int)[13:18], 2) * 2 - 40

        movement_counter = int(data[34:36], 16)

        measurement_sequence = int(data[36:38], 16)

        return (5, humidity, temperature, pressure, acceleration_x,
                acceleration_y, acceleration_z, battery_voltage, tx_power,
                movement_counter, measurement_sequence)
