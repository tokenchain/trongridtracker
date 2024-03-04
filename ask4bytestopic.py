#!/usr/bin/python
import os
from lib.solver.call4bytes import FourBytes, EVENTS
if __name__ == '__main__':
    # Clearing the Screen
    os.system('clear')
    text = input("Check event topics, enter the method name:\n")
    f = FourBytes(EVENTS())
    f.search(text)
