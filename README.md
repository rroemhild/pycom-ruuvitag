# MicroPython RuuviTag Scanner

Harvest data from [RuuviTag BLE Sensor Beacon](http://ruuvitag.com/) with MicroPython Bluetooth enabled micro controller.

micropython-ruuvitag supports [Data Format 2, 3 and 4](https://github.com/ruuvi/ruuvi-sensor-protocols).

## Usage

RuuviTagScanner scans for RuuviTags and decode the data format. The result is a list with named tuples.

### Get data from sensors

Scan 10 seconds for RuuviTag sensors and print the result.

```python
from ruuvitag import RuuviTagScanner

rts = RuuviTagScanner()

for ruuvitag in rts.find_ruuvitags(timeout=10):
    print(ruuvitag)
```

### Whitelist devices

You can collect data from only the devices you want by define a whitelist with mac addresses. Other Devices then will be ignored.

```python
whitelist = (b'aa:bb:cc:dd:ee:21', b'aa:bb:cc:dd:ee:42',)
rts = RuuviTagScanner(whitelist)
```

### Blacklist persistence

If the data from a Bluetooth device can not be decoded, the device get on a blacklist as long the MicroPython device is not resetted. For a persistent device blacklist the list should be saved and reloaded.

```python
>>> from ruuvitag import RuuviTagScanner
>>> rts = RuuviTagScanner()
>>> # add back blacklisted devices
>>> rts.blacklist = [b'aa:bb:cc:dd:ee:21', b'aa:bb:cc:dd:ee:42']
>>> # run a new scan
>>> rts.find_ruuvitags(timeout=10)
>>> # get blacklisted devices
>>> rts.blacklist
```

### Named tuple format

```python
RuuviTag = namedtuple('RuuviTag', (
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
))
```
