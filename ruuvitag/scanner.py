""" RuuviTagScanner

Scan amout of time for RuuviTags and return a list with tags
"""

import ubinascii

from ruuvitag import RuuviTagBase, RuuviTagRAW, RuuviTagURL


class RuuviTagScanner(RuuviTagBase):
    """
    Scan for RuuviTags until the timout is reached.

    Each RuuviTag will only be scanned ones each scan.

    If device data can not be decoded it's propably not a RuuviTag and
    the device goes onto the blacklist. Blacklistet tags will be
    ignored as long this device is not resetted.
    """
    def __init__(self, whitelist=None):
        super().__init__(whitelist)

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

                if self._whitelist is not None:
                    if mac not in self._whitelist or mac in scanned_tags:
                        continue
                elif mac in self._blacklist or mac in scanned_tags:
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

                ruuvi_tags.append(
                    tag(mac.decode('utf-8'), adv.rssi, *data)
                )

                scanned_tags.append(mac)

        # disable bluetooth
        self.bluetooth.deinit()

        return ruuvi_tags
