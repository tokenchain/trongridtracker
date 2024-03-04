#!/usr/bin/python


from lib.solver.call4bytes import FourBytes, SIGNATURE
if __name__ == '__main__':
    f = FourBytes(SIGNATURE())
    f.scan()
