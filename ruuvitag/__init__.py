import ubinascii

from network import Bluetooth
from ucollections import namedtuple


__version__ = b'0.1.0'


RuuviTag = namedtuple('RuuviTag', (
    'mac',
    'humidity',
    'temperature',
    'pressure',
))


class RuuviTagScanner:
    def __init__(self, whitelist=None):
        self.whitelist = whitelist
        self.blacklist = []
        self.bluetooth = Bluetooth()
        self.bluetooth.deinit()

    def find_ruuvitags(self, timeout=10):
        scanned_tags = []
        ruuvi_tags = []

        # enable bluetooth and start scanning
        self.bluetooth.init()
        self.bluetooth.start_scan(timeout)

        while self.bluetooth.isscanning():
            adv = self.bluetooth.get_adv()
            if adv:
                mac = ubinascii.hexlify(adv.mac, ':')

                if self.whitelist is not None:
                    if mac not in self.whitelist or mac in scanned_tags:
                        continue
                elif mac in self.blacklist or mac in scanned_tags:
                    continue

                data = self.get_data(adv)

                if data is None:
                    self.blacklist.append(mac)
                    continue

                data = self.decode_data(*data)

                ruuvi_tags.append(RuuviTag(mac.decode('utf-8'), *data))
                scanned_tags.append(mac)

        # disable bluetooth
        self.bluetooth.deinit()

        return ruuvi_tags

    def get_data(self, adv):
        data = self.get_data_format_2and4(adv)

        if data is not None:
            return (2, data)

        data = self.get_data_format_3(adv)

        if data is not None:
            return (3, data)

    def get_data_format_2and4(self, adv):
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

    def get_data_format_3(self, adv):
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

        # Only data format 3 (raw)
        if data[4:6] != b'03':
            return None

        return data

    def decode_data(self, data_format, data):
        if data_format == 2:
            return self.decode_data_format_2(data)
        elif data_format == 3:
            return self.decode_data_format_3(data)

    @staticmethod
    def decode_data_format_2(data):
        """ RuuviTag URL decoder """
        data = data.encode()
        if len(data) > 8:
            # identifier = data[8:]
            data = data[:8]
        decoded = ubinascii.a2b_base64(data)

        humidity = decoded[1] / 2
        temperature = (decoded[2] & 127) + decoded[3] / 100
        pressure = ((decoded[4] << 8) + decoded[5]) + 50000

        return (humidity, temperature, pressure)

    @staticmethod
    def decode_data_format_3(data):
        humidity = int(data[6:8], 16) / 2

        temperature_str = data[8:12]
        temperature = int(temperature_str[:2], 16)
        temperature += int(temperature_str[2:4], 16) / 100
        if temperature > 128:
            temperature -= 128
            temperature = 0 - temperature

        pressure = int(data[12:16], 16) + 50000

        return (humidity, temperature, pressure)
