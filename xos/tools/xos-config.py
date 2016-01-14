#!/usr/bin/env python
import sys

# add the parent directory to sys.path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from xos.config import Config

def help():
    print "syntax: %s get name [default]" % sys.argv[0]

def main():
    c = Config()

    if len(sys.argv)<=1:
        help()
        return

    if sys.argv[1] == "get":
        if len(sys.argv)==4:
            print getattr(c, sys.argv[2], sys.argv[3])
        elif len(sys.argv)==3:
            print getattr(c, sys.argv[2])
        else:
            help()
    else:
        help()

main()
