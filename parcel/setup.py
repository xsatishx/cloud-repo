from setuptools import setup
from subprocess import check_call, call
import logging
from setuptools.command.develop import develop
from setuptools.command.install import install
from sys import platform


def parcel_build(command_subclass):
    original = command_subclass.run

    def parcel_run(self):
        try:
            call(['make', 'clean'])
            check_call(['make'])
        except Exception as e:
            logging.error(
                "Unable to build UDT library: {}".format(e))
        if isinstance(self, install):
            install.do_egg_install(self)
        else:
            original(self)

    command_subclass.run = parcel_run
    return command_subclass


@parcel_build
class ParcelDevelop(develop):
    pass


@parcel_build
class ParcelInstall(install):
    pass


APP = ['bin/parcel']
OPTIONS = {
    'argv_emulation': True,
    'emulate_shell_environment': True,
}


extra_args = {}
if platform == 'darwin':
    extra_args.update(dict(
        app=APP,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    ))


setup(
    name='parcel',
    version='0.1.13',
    packages=["parcel"],
    cmdclass={
        'install': ParcelInstall,
        'develop': ParcelDevelop,
    },
    install_requires=[
        'requests==2.5.1',
        'progressbar==2.3',
        'Flask==0.10.1',
        'intervaltree==2.0.4',
        'termcolor==1.1.0',
        'cmd2==0.6.8',
    ],
    package_data={
        "parcel": [
            "src/lparcel.so",
        ]
    },
    scripts=[
        'bin/parcel',
        'bin/parcel-server',
        'bin/parcel-tcp2udt',
        'bin/parcel-udt2tcp',
    ],
    **extra_args
)
