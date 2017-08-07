
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/python

import argparse
from generator import *

parse = argparse.ArgumentParser(description='XOS Generative Toolchain')
parse.add_argument('--rev', dest='rev', action='store_true',default=False, help='Convert proto to xproto')
parse.add_argument('--target', dest='target', action='store',default=None, help='Output format, corresponding to <output>.yaml file', required=True)
parse.add_argument('--output', dest='output', action='store',default=None, help='Destination dir')
parse.add_argument('--attic', dest='attic', action='store',default=None, help='The location at which static files are stored')
parse.add_argument('--kvpairs', dest='kv', action='store',default=None, help='Key value pairs to make available to the target')
parse.add_argument('--write-to-file', dest='write_to_file', choices = ['single', 'model', 'target'], action='store',default=None, help='Single output file (single) or output file per model (model) or let target decide (target)')

group = parse.add_mutually_exclusive_group()
group.add_argument('--dest-file', dest='dest_file', action='store',default=None, help='Output file name (if write-to-file is set to single)')
group.add_argument('--dest-extension', dest='dest_extension', action='store',default=None, help='Output file extension (if write-to-file is set to single)')

parse.add_argument('files', metavar='<input file>', nargs='+', action='store', help='xproto files to compile')

class XosGen:

    @staticmethod
    def init(args=None):

        if not args:
            args = parse.parse_args()

        args.quiet = False

        # convert output to absolute path
        if args.output is not None and not os.path.isabs(args.output):
            args.output = os.path.abspath(os.getcwd() + '/' + args.output)
        if not '/' in args.target:
            # if the target is not a path, it refer to a library included one
            args.target = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/targets/" + args.target)
        if not os.path.isabs(args.target):
            args.target = os.path.abspath(os.getcwd() + '/' + args.target)

        # check if there's a line that starts with +++ in the target
        # if so, then the output file names are left to the target to decide
        # also, if dest-file or dest-extension are supplied, then an error is generated.
        plusplusplus = reduce(lambda acc, line: True if line.startswith('+++') else acc, open(args.target).read().splitlines(), False)

        if plusplusplus and args.write_to_file != 'target':
            parse.error('%s chooses the names of the files that it generates, you must set --write-to-file to "target"' % args.target)


        if args.write_to_file != 'single' and (args.dest_file):
            parse.error('--dest-file requires --write-to-file to be set to "single"')

        if args.write_to_file != 'model' and (args.dest_extension):
            parse.error('--dest-extension requires --write-to-file to be set to "model"')

        inputs = []

        for fname in args.files:
            if not os.path.isabs(fname):
                inputs.append(os.path.abspath(os.getcwd() + '/' + fname))
            else:
                inputs.append(fname)
        args.files = inputs

        generated = XOSGenerator.generate(args)

        if not args.output and not args.write_to_file:
            print generated