#!/usr/bin/python
from lib.solver.call4bytes import FourBytes, EVENTS

if __name__ == '__main__':
    f = FourBytes(EVENTS())
    f.scan()
