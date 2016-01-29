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

name='ssh_key_service'

setup(
    name=name,
    version='0.4.2.1',
    packages=[name],
    license='Apache License 2.0"',
    install_requires=[
        'flask',
        'python-gnupg',
        'M2Crypto',
    ],
    #long_description=open('README.rst').read(),
)

#VIRTUAL_ENV
#%s/lib/python2.7/site-packages/tukey_middleware/local_settings.py
#subprocess.Popen(", shell=True)
