from ruuvitag.format import RuuviTagRAW
from ubinascii import hexlify

from ruuvitag.core import RuuviTag


class RuuviTagTracker(RuuviTag):
    """Ruuvi Tag Tracker

    Track RuuviTags and call a callback on each new recieved data.

    If device data can not be decoded it's propably not a RuuviTag and
    the device goes onto the blacklist. Blacklistet devices will be
    ignored as long this device is not resetted.
    """

    def __init__(self, whitelist=None, antenna=None):
        super().__init__(whitelist, antenna)

    def track_ruuvitags(self, callback):
        self.bluetooth.start_scan(-1)

        get_adv = self.bluetooth.get_adv
        isscanning = self.bluetooth.isscanning
        whitelist = self._whitelist

        while isscanning():
            adv = get_adv()
            if adv:
                mac = hexlify(adv.mac, ":")

                if whitelist is not None:
                    if mac not in whitelist:
                        continue
                elif mac in self._blacklist:
                    continue

                tag = self.get_tag(mac, adv)
                if isinstance(tag, RuuviTagRAW):
                    callback(tag)
