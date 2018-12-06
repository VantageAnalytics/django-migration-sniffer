import os
from setuptools import setup, find_packages


VERSION = __import__('migration_sniffer').__version__


def read(*path):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *path)).read()


setup(
    name='migration sniffer',
    version=VERSION,
    description=('django migration sniffer warns users about migrations with '
                 'dangerous operations such as dropping columns and tables.'),
    license='BSD',
    author='Vantage',
    author_email='brandon@vantageanalytics.com',
    maintainer='Vantage',
    maintainer_email='brandon@vantageanalytics.com',
    url='http://github.com/dvincelli/django-migration-sniffer/',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
