#!/usr/bin/env bash
enp/bin/python -m pip freeze | grep -vE '^(pyobjc-|pyobjc).*==' | awk '{print $1}' > requirements.txt
