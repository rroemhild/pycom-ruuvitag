import utime

from ruuvitag.scanner import RuuviTagScanner


def scan(rts):
    tags = rts.find_ruuvitags()

    print("Found {} Ruuvitags".format(len(tags)))

    for t in tags:
        print(
            "MAC: {}, RSSI: {}, Format: {}, Temp: {}, Humid: {}".format(
                t.mac, t.rssi, t.format, t.temperature, t.humidity
            )
        )


def main():
    delay = 30
    rts = RuuviTagScanner()

    try:
        while True:
            print("Scanning...")
            scan(rts)
            print("Sleep for {} seconds.".format(delay))
            utime.sleep(delay)
    except KeyboardInterrupt:
        if rts.bluetooth.isscanning():
            rts.bluetooth.stop_scan()

        rts.bluetooth.deinit()


if __name__ == "__main__":
    main()
