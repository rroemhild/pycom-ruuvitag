import ubinascii

from ruuvitag.core import RuuviTagBase


class RuuviTagScanner(RuuviTagBase):
    """Ruuvi Tag Scanner

    Scan for RuuviTags until the timout is reached.

    If device data can not be decoded it's propably not a RuuviTag and
    the device goes onto the blacklist. Blacklisted tags will be
    ignored as long the device is not resetted.
    """
    def __init__(self, whitelist=None):
        super().__init__(whitelist)

    def find_ruuvitags(self, timeout=10):
        scanned_tags = {}
        ruuvi_tags = []

        # enable bluetooth and start scanning
        self.bluetooth.init()
        self.bluetooth.start_scan(timeout)

        while self.bluetooth.isscanning():
            adv = self.bluetooth.get_adv()
            if adv:
                mac = ubinascii.hexlify(adv.mac, ':')

                if mac in scanned_tags or mac in self._blacklist:
                    continue
                elif self._whitelist is not None:
                    if mac not in self._whitelist:
                        continue

                # add tag to scanned list
                scanned_tags[mac] = adv

        # disable bluetooth
        self.bluetooth.deinit()

        for mac in scanned_tags:
            tag = self.get_tag(mac, scanned_tags[mac])
            ruuvi_tags.append(tag)

        return ruuvi_tags
