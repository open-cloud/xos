#!/usr/bin/python

import sys
import netifaces

def main (argv):
    addr = argv[0]
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if 2 in addrs and addrs[2][0]['addr'] == addr:
            sys.stdout.write(iface)

if __name__ == "__main__":
    main(sys.argv[1:])
