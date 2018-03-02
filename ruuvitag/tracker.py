""" RuuviTagTracker

Track RuuviTags and call the callback everytime we recieve data.
"""

import ubinascii

from ruuvitag import RuuviTagBase, RuuviTagRAW, RuuviTagURL


class RuuviTagTracker(RuuviTagBase):
    """
    Track RuuviTags and call a callback on each new recieved data.

    If device data can not be decoded it's propably not a RuuviTag and
    the device goes onto the blacklist. Blacklistet devices will be
    ignored as long this device is not resetted.
    """
    def __init__(self, whitelist=None):
        super().__init__(whitelist)

    def track_ruuvitags(self, callback):
        self.bluetooth.init()
        self.bluetooth.start_scan(-1)

        while self.bluetooth.isscanning():
            adv = self.bluetooth.get_adv()
            if adv:
                mac = ubinascii.hexlify(adv.mac, ':')

                if self._whitelist is not None:
                    if mac not in self._whitelist:
                        continue
                elif mac in self._blacklist:
                    continue

                data = self.get_data(adv)

                if data is None:
                    self._blacklist.append(mac)
                    continue

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

                callback(tag(mac.decode('utf-8'), adv.rssi, *data))
