============================
MicroPython RuuviTag Scanner
============================

Harvest data from `RuuviTag BLE Sensor Beacon <http://ruuvitag.com/>`_ with MicroPython Bluetooth enabled micro controller like the `pycom <https://pycom.io/>`_ devices.

micropython-ruuvitag supports `Data Format 2, 3, 4 and 5 <https://github.com/ruuvi/ruuvi-sensor-protocols>`_.

This package comes with a scanner and a tracker. The scanner scans for RuuviTags in a pre defined time and return the result. The tracker continuously scans for RuuviTags and call a callback for each tag found.

Version: ``0.4.2``

Installation
------------

The easiest way to install the package is via ``upip``:

>>> import upip
>>> upip.install('micropython-ruuvitag')

For manual installation copy the ``ruuvitag`` directory with all files to your device ``lib`` directory.


Scanner
-------

``RuuviTagScanner`` scans for RuuviTags and decode the data format. The result is a list with named tuples.

Scan 10 seconds for RuuviTag sensors and print the result:

.. code-block:: python

    from ruuvitag.scanner import RuuviTagScanner

    rts = RuuviTagScanner()

    for ruuvitag in rts.find_ruuvitags(timeout=10):
        print(ruuvitag)


Tracker
-------

``RuuviTagTracker`` scans for RuuviTags, decode the data format and call a callback with a named tuple if recieved data from tag.

.. code-block:: python

    from ruuvitag.tracker import RuuviTagTracker

    def cb(ruuvitag):
        print(ruuvitag)

    rtt = RuuviTagTracker()
    rtt.track_ruuvitags(cb)


Whitelist devices
-----------------

You can collect data from only the devices you want by define a whitelist with mac addresses. Other Devices then will be ignored. Whitelists can be used with RuuviTagScanner and RuuviTagTracker.

.. code-block:: python

    whitelist = (b'aa:bb:cc:dd:ee:21', b'aa:bb:cc:dd:ee:42',)
    rts = RuuviTagScanner(whitelist)


Blacklist persistence
---------------------

If the data from a Bluetooth device can not be decoded, the device get on a blacklist as long the MicroPython device is not resetted. For a persistent device blacklist the list should be saved and reloaded.

>>> from ruuvitag import RuuviTagScanner
>>> rts = RuuviTagScanner()
>>> # add back blacklisted devices
>>> rts.blacklist = [b'aa:bb:cc:dd:ee:21', b'aa:bb:cc:dd:ee:42']
>>> # run a new scan
>>> rts.find_ruuvitags(timeout=10)
>>> # get blacklisted devices
>>> rts.blacklist


Named tuple formats
-------------------

Format 2 and 4 (Eddystone-URL)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    RuuviTagURL = namedtuple('RuuviTagURL', (
        'mac',
        'rssi',
        'format',
        'humidity',
        'temperature',
        'pressure',
        'id',
    ))

Format 3 and 5 (RAW)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    RuuviTagRAW = namedtuple('RuuviTagRAW', (
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
        'power_info',
        'movement_counter',
        'measurement_sequence',
    ))