from setuptools import setup
import sdist_upip


setup(
    name='micropython-ruuvitag',
    version='0.3.0',
    description='RuuviTag BLE Sensor Beacon scanner.',
    long_description='More documentation is available at https://github.com/rroemhild/micropython-ruuvitag',
    url='https://github.com/rroemhild/micropython-ruuvitag',
    author='Rafael Römhild',
    author_email='rafael@roemhild.de',
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['ruuvitag'],
)
