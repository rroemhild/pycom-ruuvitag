from network import Bluetooth

from ruuvitag.format import RuuviTagURL, RuuviTagRAW
from ruuvitag.decoder import (
    decode_data_format_2and4,
    decode_data_format_3,
    decode_data_format_5,
)


class RuuviTag:
    def __init__(self, whitelist=None, antenna=None):
        self._whitelist = whitelist
        self._blacklist = []
        self.bluetooth = Bluetooth()
        self.bluetooth.init(antenna=antenna)

    def __repr__(self):
        return "{}(whitelist={!r}, blacklist={!r})".format(
            type(self).__name__, self._whitelist, self._blacklist
        )

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
                data = data + (None,) * 3

        return tag(mac.decode("utf-8"), adv.rssi, *data)

    def get_data(self, adv):
        # raw1 and raw2 format
        data = self.get_data_format_raw(adv)
        if data is not None:
            return data

        # deprecated url format
        data = self.get_data_format_2and4(adv)
        if data is not None:
            return (2, data)

    @staticmethod
    def get_data_format_2and4(adv):
        """
        Test if device data is in data format 2 or 4.

        Returns measurement data or None if not in format 2 or 4.
        """
        try:
            data = adv.data.decode("utf-8")
            index = data.find("ruu.vi/#")
            if index > -1:
                return data[(index + 8):]
            else:
                index = data.find("r/")
                if index > -1:
                    return data[(index + 2):]
                return None
        except Exception:
            return None

    def get_data_format_raw(self, adv):
        """Test if device data is in raw format 3 (RAWv1) or 5 (RAWv2).

        Returns decoded measurements from the manufacturer data
        or None if not in format RAWv1, RAWv2 or no data can be extracetd
        from the device.

        The Bluetooth device is necessary to get the manufacturer data.
        """
        raw_data_formats = [3, 5]

        try:
            data = self.bluetooth.resolve_adv_data(
                adv.data, Bluetooth.ADV_MANUFACTURER_DATA
            )
        except TypeError:
            return None

        if data is None:
            return None

        # Only RuuviTags
        if data[:2] != b"\x99\x04":
            return None

        # Only data format 3 and 5 (raw)
        if data[2] not in raw_data_formats:
            return None

        return (data[2], data)

    def decode_data(self, data_format, data):
        if data_format in (2, 4):
            return decode_data_format_2and4(data)
        elif data_format == 3:
            return decode_data_format_3(data)
        elif data_format == 5:
            return decode_data_format_5(data)
