from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='saaspy',
    version='0.1',
    author='Steven D. Christe',
    author_email='steven.d.christe@nasa.gov',
    packages=['saaspy'],
    url='',
    license='See LICENSE.txt',
    description='',
    long_description=open('README.md').read(),
)
