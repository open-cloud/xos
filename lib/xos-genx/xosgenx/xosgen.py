#!/usr/bin/env python

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

from __future__ import absolute_import, print_function

import argparse
import os
from functools import reduce

from six.moves import range

from .generator import XOSProcessor, XOSProcessorArgs
from .version import __version__

parse = argparse.ArgumentParser(description="XOS Generative Toolchain")
parse.add_argument(
    "--rev",
    dest="rev",
    action="store_true",
    default=XOSProcessorArgs.default_rev,
    help="Convert proto to xproto",
)
parse.add_argument(
    "--output",
    dest="output",
    action="store",
    default=XOSProcessorArgs.default_output,
    help="Destination dir",
)
parse.add_argument(
    "--attic",
    dest="attic",
    action="store",
    default=XOSProcessorArgs.default_attic,
    help="The location at which static files are stored",
)
parse.add_argument(
    "--kvpairs",
    dest="kv",
    action="store",
    default=XOSProcessorArgs.default_kvpairs,
    help="Key value pairs to make available to the target",
)
parse.add_argument(
    "--write-to-file",
    dest="write_to_file",
    choices=["single", "model", "target"],
    action="store",
    default=XOSProcessorArgs.default_write_to_file,
    help="Single output file (single) or output file per model (model) or let target decide (target)",
)
parse.add_argument("--version", action="version", version=__version__)
parse.add_argument(
    "-v",
    "--verbosity",
    action="count",
    default=XOSProcessorArgs.default_verbosity,
    help="increase output verbosity",
)
parse.add_argument(
    "--include-models",
    dest="include_models",
    action="append",
    default=XOSProcessorArgs.default_include_models,
    help="list of models to include",
)
parse.add_argument(
    "--include-apps",
    dest="include_apps",
    action="append",
    default=XOSProcessorArgs.default_include_apps,
    help="list of models to include",
)

group = parse.add_mutually_exclusive_group()
group.add_argument(
    "--dest-file",
    dest="dest_file",
    action="store",
    default=XOSProcessorArgs.default_dest_file,
    help="Output file name (if write-to-file is set to single)",
)
group.add_argument(
    "--dest-extension",
    dest="dest_extension",
    action="store",
    default=XOSProcessorArgs.default_dest_extension,
    help="Output file extension (if write-to-file is set to single)",
)

group = parse.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--target",
    dest="target",
    action="store",
    default=XOSProcessorArgs.default_target,
    help="Output format, corresponding to <output>.yaml file",
)
group.add_argument(
    "--checkers",
    dest="checkers",
    action="store",
    default=XOSProcessorArgs.default_checkers,
    help="Comma-separated list of static checkers",
)
group.add_argument(
    "--lint",
    dest="lint",
    action="store_true",
    default=XOSProcessorArgs.default_lint,
    help="Parse the xproto but don't execute any xtargets",
)


parse.add_argument(
    "files",
    metavar="<input file>",
    nargs="+",
    action="store",
    help="xproto files to compile",
)

parse.add_argument(
    "--strict-validation",
    dest="strict_validation",
    action="store_true",
    default=XOSProcessorArgs.default_strict_validation,
    help="Exit if validation fails",
)

CHECK = 1
GEN = 2
LINT = 3


class XosGen:
    @staticmethod
    def init(args=None):
        if not args:
            args = parse.parse_args()

        args.quiet = False

        if args.target:
            op = GEN
            subdir = "/targets/"
            operators = [args.target]
        elif args.checkers:
            op = CHECK
            subdir = "/checkers/"
            operators = args.checkers
        elif args.lint:
            op = LINT
            subdir = None
            operators = []
        else:
            parse.error("At least one of --target, --checkers, or --lint is required")

        for i in range(len(operators)):
            if "/" not in operators[i]:
                # if the target is not a path, it refer to a library included one
                operators[i] = os.path.abspath(
                    os.path.dirname(os.path.realpath(__file__)) + subdir + operators[i]
                )

            if not os.path.isabs(operators[i]):
                operators[i] = os.path.abspath(os.getcwd() + "/" + operators[i])

        if op == GEN:
            # convert output to absolute path
            if args.output is not None and not os.path.isabs(args.output):
                args.output = os.path.abspath(os.getcwd() + "/" + args.output)

            operator = operators[0]

            # check if there's a line that starts with +++ in the target
            # if so, then the output file names are left to the target to decide
            # also, if dest-file or dest-extension are supplied, then an error is generated.
            plusplusplus = reduce(
                lambda acc, line: True if line.startswith("+++") else acc,
                open(operator).read().splitlines(),
                False,
            )

            if plusplusplus and args.write_to_file != "target":
                parse.error(
                    '%s chooses the names of the files that it generates, you must set --write-to-file to "target"'
                    % operator
                )

            if args.write_to_file != "single" and (args.dest_file):
                parse.error(
                    '--dest-file requires --write-to-file to be set to "single"'
                )

            if args.write_to_file != "model" and (args.dest_extension):
                parse.error(
                    '--dest-extension requires --write-to-file to be set to "model"'
                )

        elif op == CHECK:
            if args.write_to_file or args.dest_extension:
                parse.error("Checkers cannot write to files")
        elif op == LINT:
            # no outputs, so nothing to check
            pass

        inputs = []

        for fname in args.files:
            if not os.path.isabs(fname):
                inputs.append(os.path.abspath(os.getcwd() + "/" + fname))
            else:
                inputs.append(fname)

        args.files = inputs

        if op == GEN:
            generated = XOSProcessor.process(args, operators[0])
            if not args.output and not args.write_to_file:
                print(generated)
        elif op == CHECK:
            for o in operators:
                verdict_str = XOSProcessor.process(args, o)
                vlst = verdict_str.split("\n")

                try:
                    verdict = next(v for v in vlst if v.strip())
                    status_code, status_string = verdict.split(" ", 1)
                    status_code = int(status_code)
                except BaseException:
                    print("Checker %s returned mangled output" % o)
                    exit(1)

                if status_code != 200:
                    print("%s: %s - %s" % (o, status_code, status_string))
                    exit(1)
                else:
                    print("%s: OK" % o)
        elif op == LINT:
            XOSProcessor.process(args, None)
