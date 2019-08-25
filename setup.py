from setuptools import setup
import sdist_upip

from ruuvitag import __version__


setup(
    name='micropython-ruuvitag',
    version=__version__.decode("utf-8"),
    description='RuuviTag BLE Sensor Beacon scanner.',
    long_description=open('README.rst').read(),
    url='https://github.com/rroemhild/micropython-ruuvitag/',
    author='Rafael Römhild',
    author_email='rafael@roemhild.de',
    maintainer='Rafael Römhild',
    maintainer_email='rafael@roemhild.de',
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['ruuvitag'],
)
