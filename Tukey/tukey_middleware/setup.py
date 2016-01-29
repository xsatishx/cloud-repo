#  Copyright 2013 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

#from distutils.core import setup
from setuptools import setup
import subprocess

name='tukey_middleware'

sub_packages = ['modules', 'api', 'auth', 'cloud_driver',
    # tests
    'tests', 'tests.services']


sub_modules = ['ids', 'instance_metadata', 'metadata']
modules = ['modules.%s' % s for s in sub_modules]

setup(
    name=name,
    version='0.4.2.1',
    packages=[name] + ['%s.%s' % (name, s) for s in sub_packages + modules],
    license='Apache License 2.0"',
    dependency_links=[
        'https://github.com/LabAdvComp/novacluster/tarball/master#egg=novacluster'],
    install_requires=[
        'novacluster',
        'flask',
        'python-glanceclient',
        'python-cinderclient',
        'python-magic',
        'python-memcached',
        'dnspython',
        'prettytable',
        'apache-libcloud==0.14.0-beta3',
        'xmldict',
        'SQLAlchemy',
        'psycopg2',
        'couchdb',
        'fuse-python',
        'requests',
        'python-novaclient',
        'python-swiftclient',
        'psutil',
        'python-gnupg',
        'M2Crypto',
    ],
    long_description=open('README.rst').read(),
    scripts=['bin/osdcfs', 'bin/osdc-upload-metadata', 'bin/osdc-upload-file',
            'bin/osdc-register-file'],
)

#VIRTUAL_ENV
#%s/lib/python2.7/site-packages/tukey_middleware/local_settings.py
#subprocess.Popen(", shell=True)
