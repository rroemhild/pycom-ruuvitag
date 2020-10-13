from ubinascii import hexlify

from ruuvitag.core import RuuviTag


class RuuviTagScanner(RuuviTag):
    """Ruuvi Tag Scanner

    Scan for RuuviTags until the timout is reached.

    If device data can not be decoded it's propably not a RuuviTag and
    the device goes onto the blacklist. Blacklisted tags will be
    ignored as long the device is not resetted.
    """

    def __init__(self, whitelist=None, antenna=None):
        super().__init__(whitelist, antenna)

    def find_ruuvitags(self, timeout=10):
        scanned_tags = {}
        ruuvi_tags = []

        self.bluetooth.start_scan(timeout)

        get_adv = self.bluetooth.get_adv
        isscanning = self.bluetooth.isscanning
        whitelist = self._whitelist

        while isscanning():
            adv = get_adv()
            if adv:
                mac = hexlify(adv.mac, ":")

                if mac in scanned_tags or mac in self._blacklist:
                    continue
                elif whitelist is not None:
                    if mac not in whitelist:
                        continue

                # add tag to scanned list
                scanned_tags[mac] = adv

        for mac in scanned_tags:
            tag = self.get_tag(mac, scanned_tags[mac])
            ruuvi_tags.append(tag)

        return ruuvi_tags
