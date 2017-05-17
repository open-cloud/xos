#!/usr/bin/python

import pdb
import argparse
import traceback
import sys
import os
from generator import *

parse = argparse.ArgumentParser(description='XOS code generator')
parse.add_argument('--rev', dest='rev', action='store_true',default=False, help='Convert proto to xproto')
parse.add_argument('--target', dest='target', action='store',default=None, help='Output format, corresponding to <output>.yaml file', required=True)
parse.add_argument('--output', dest='output', action='store',default=None, help='Destination path')
parse.add_argument('--attic', dest='attic', action='store',default=None, help='The location at which static files are stored')
parse.add_argument('--kvpairs', dest='kv', action='store',default=None, help='Key value pairs to make available to the target')
parse.add_argument('inputs', metavar='<input file>', nargs='+', action='store', help='xproto files to compile')

args = parse.parse_args()

def main():
    input = ''
    for fname in args.inputs:
	with open(fname) as infile:
	    input+=infile.read()

    generator = XOSGenerator(args)
    generator.input = input
    generator.generate()

if __name__=='__main__':
    main()
