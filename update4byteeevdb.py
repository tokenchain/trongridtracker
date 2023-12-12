#!/usr/bin/python
from core.solver.call4bytes import FourBytes, EVENTS

if __name__ == '__main__':
    f = FourBytes(EVENTS())
    f.scan()
