#!/usr/bin/python
import os

from core.solver.call4bytes import FourBytes, SIGNATURE

if __name__ == '__main__':
    # Clearing the Screen
    os.system('clear')
    text = input("Check signature, enter the method name:\n")
    f = FourBytes(SIGNATURE())
    f.search(text)
