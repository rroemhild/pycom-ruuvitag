# MicroPython RuuviTag Scanner

Harvest data from [RuuviTag BLE Sensor Beacon](http://ruuvitag.com/) with MicroPython Bluetooth enabled microcontroller.

micropython-ruuvitag supports [Data Format 2, 3 and 4](https://github.com/ruuvi/ruuvi-sensor-protocols).

## Usage

RuuviTagScanner scans for RuuviTags and tries to decode the measuerments from the data format. The result is a list with named tuples.

### Get data from sensors

Scan for sensors and print the result.

```python
from ruuvitag import RuuviTagScanner

rts = RuuviTagScanner()

for ruuvitag in rts.find_ruuvitags(timeout=10):
    print(ruuvitag)
```

### Whitelist devices

You can collect data from only the devices you want by define a whitelist with mac addresses. Other Devices will be ignored.

```python
whitelist = (b'aa:bb:cc:dd:ee:21', b'aa:bb:cc:dd:ee:42',)
rts = RuuviTagScanner(whitelist)
```

### Named tuple format

```python
RuuviTag = namedtuple('RuuviTag', (
    'mac',
    'humidity',
    'temperature',
    'pressure',
))
```
