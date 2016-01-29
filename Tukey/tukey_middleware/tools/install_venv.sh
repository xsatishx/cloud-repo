#!/bin/bash
virtualenv .venv
# need because something bad possibly in pbr
tools/with_venv.sh pip install -r tools/pip-requires
tools/with_venv.sh python setup.py install
