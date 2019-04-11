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

import os
import jinja2
import plyxproto.parser as plyxproto
import yaml
from colorama import Fore
import sys

from . import jinja2_extensions
from .proto2xproto import Proto2XProto
from .xos2jinja import XOS2Jinja
from .validator import XProtoValidator

loader = jinja2.PackageLoader(__name__, "templates")
env = jinja2.Environment(loader=loader)


class XOSProcessorArgs:
    """ Helper class for use cases that want to call XOSProcessor directly, rather than executing xosgenx from the
        command line.
    """

    default_rev = False
    default_output = None
    default_attic = None
    default_kvpairs = None
    default_write_to_file = None
    default_dest_file = None
    default_dest_extension = None
    default_target = None
    default_checkers = None
    default_verbosity = (
        0
    )  # Higher numbers = more verbosity, lower numbers = less verbosity
    default_include_models = (
        []
    )  # If neither include_models nor include_apps is specified, then all models will
    default_include_apps = []  # be included.
    default_strict_validation = False
    default_lint = False

    def __init__(self, **kwargs):
        # set defaults
        self.rev = XOSProcessorArgs.default_rev
        self.output = XOSProcessorArgs.default_output
        self.attic = XOSProcessorArgs.default_attic
        self.kvpairs = XOSProcessorArgs.default_kvpairs
        self.verbosity = XOSProcessorArgs.default_verbosity
        self.write_to_file = XOSProcessorArgs.default_write_to_file
        self.default_dest_file = XOSProcessorArgs.default_dest_file
        self.default_dest_extension = XOSProcessorArgs.default_dest_extension
        self.default_target = XOSProcessorArgs.default_target
        self.default_checkers = XOSProcessorArgs.default_target
        self.include_models = XOSProcessorArgs.default_include_models
        self.include_apps = XOSProcessorArgs.default_include_apps
        self.strict_validation = XOSProcessorArgs.default_strict_validation
        self.lint = XOSProcessorArgs.default_lint

        # override defaults with kwargs
        for (k, v) in kwargs.items():
            setattr(self, k, v)


class XOSProcessor:
    @staticmethod
    def _read_input_from_files(files):
        """ Read the files and return the combined text read.

            Also returns a list of (line_number, filename) tuples that tell which
            starting line corresponds to each file.
        """
        line_map = []
        input = ""
        for fname in files:
            with open(fname) as infile:
                line_map.append((len(input.split("\n")), fname))
                input += infile.read()
        return (input, line_map)

    @staticmethod
    def _attach_parser(ast, args):
        if hasattr(args, "rev") and args.rev:
            v = Proto2XProto()
            ast.accept(v)

        v = XOS2Jinja(args)
        ast.accept(v)
        return v

    @staticmethod
    def _get_template(target):
        if not os.path.isabs(target):
            return os.path.abspath(
                os.path.dirname(os.path.realpath(__file__)) + "/targets/" + target
            )
        return target

    @staticmethod
    def _file_exists(attic):
        # NOTE this method can be used in the jinja template
        def file_exists2(name):
            if attic is not None:
                path = attic + "/" + name
            else:
                path = name
            return os.path.exists(path)

        return file_exists2

    @staticmethod
    def _include_file(attic):
        # NOTE this method can be used in the jinja template
        def include_file2(name):
            if attic is not None:
                path = attic + "/" + name
            else:
                path = name
            return open(path).read()

        return include_file2

    @staticmethod
    def _load_jinja2_extensions(os_template_env, attic):

        os_template_env.globals["include_file"] = XOSProcessor._include_file(
            attic
        )  # Generates a function
        os_template_env.globals["file_exists"] = XOSProcessor._file_exists(
            attic
        )  # Generates a function

        os_template_env.filters["yaml"] = yaml.dump
        for f in dir(jinja2_extensions):
            if f.startswith("xproto"):
                os_template_env.globals[f] = getattr(jinja2_extensions, f)
        return os_template_env

    @staticmethod
    def _add_context(args):
        if not hasattr(args, "kv") or not args.kv:
            return
        try:
            context = {}
            for s in args.kv.split(","):
                k, val = s.split(":")
                context[k] = val
            return context
        except Exception as e:
            print(e)

    @staticmethod
    def _write_single_file(rendered, dir, dest_file, quiet):

        file_name = "%s/%s" % (dir, dest_file)
        file = open(file_name, "w")
        file.write(rendered)
        file.close()
        if not quiet:
            print("Saved: %s" % file_name)

    @staticmethod
    def _write_split_target(rendered, dir, quiet):

        lines = rendered.splitlines()
        current_buffer = []
        for l in lines:
            if l.startswith("+++"):

                if dir:
                    path = dir + "/" + l[4:].lower()

                fil = open(path, "w")
                buf = "\n".join(current_buffer)

                obuf = buf

                fil.write(obuf)
                fil.close()

                if not quiet:
                    print("Save file to: %s" % path)

                current_buffer = []
            else:
                current_buffer.append(l)

    @staticmethod
    def _find_message_by_model_name(messages, model):
        return next((x for x in messages if x["name"] == model), None)

    @staticmethod
    def _find_last_nonempty_line(text, pointer):
        ne_pointer = pointer
        found = False
        while ne_pointer != 0 and not found:
            ne_pointer = text[: (ne_pointer - 1)].rfind("\n")
            if ne_pointer < 0:
                ne_pointer = 0
            if text[ne_pointer - 1] != "\n":
                found = True

        return ne_pointer

    @staticmethod
    def process(args, operator=None):
        # Setting defaults
        if not hasattr(args, "attic"):
            args.attic = None
        if not hasattr(args, "write_to_file"):
            args.write_to_file = None
        if not hasattr(args, "dest_file"):
            args.dest_file = None
        if not hasattr(args, "dest_extension"):
            args.dest_extension = None
        if not hasattr(args, "output"):
            args.output = None
        if not hasattr(args, "quiet"):
            args.quiet = True

        # Validating
        if args.write_to_file == "single" and args.dest_file is None:
            raise Exception(
                "[XosGenX] write_to_file option is specified as 'single' but no dest_file is provided"
            )
        if args.write_to_file == "model" and (args.dest_extension is None):
            raise Exception(
                "[XosGenX] write_to_file option is specified as 'model' but no dest_extension is provided"
            )

        if args.output is not None and not os.path.isabs(args.output):
            raise Exception("[XosGenX] The output dir (%s) must be an absolute path!" % args.output)
        if args.output is not None and not os.path.isdir(args.output):
            raise Exception("[XosGenX] The output dir (%s) must be a directory!" % args.output)

        if hasattr(args, "files"):
            (inputs, line_map) = XOSProcessor._read_input_from_files(args.files)
        elif hasattr(args, "inputs"):
            inputs = args.inputs
            line_map = []
        else:
            raise Exception("[XosGenX] No inputs provided!")

        context = XOSProcessor._add_context(args)

        parser = plyxproto.ProtobufAnalyzer()
        try:
            ast = parser.parse_string(inputs, debug=0)
        except plyxproto.ParsingError as e:
            line, start, end = e.error_range

            ptr = XOSProcessor._find_last_nonempty_line(inputs, start)

            if start == 0:
                beginning = ""
            else:
                beginning = inputs[ptr: start - 1]

            line_end_char = inputs[start + end:].find("\n")
            line_end = inputs[line_end_char]

            if e.message:
                error = e.message
            else:
                error = "xproto parsing error"

            print(error + "\n" + Fore.YELLOW + "Line %d:" % line + Fore.WHITE)
            print(
                beginning
                + Fore.YELLOW
                + inputs[start - 1: start + end]
                + Fore.WHITE
                + line_end
            )
            exit(1)

        v = XOSProcessor._attach_parser(ast, args)

        if args.include_models or args.include_apps:
            for message in v.messages:
                message["is_included"] = False
                if message["name"] in args.include_models:
                    message["is_included"] = True
                else:
                    app_label = (
                        message.get("options", {})
                        .get("app_label")
                        .strip('"')
                    )
                    if app_label in args.include_apps:
                        message["is_included"] = True
        else:
            for message in v.messages:
                message["is_included"] = True

        validator = XProtoValidator(v.models, line_map)
        validator.validate()
        if validator.errors:
            if args.strict_validation or (args.verbosity >= 0):
                validator.print_errors()
            fatal_errors = [x for x in validator.errors if x["severity"] == "ERROR"]
            if fatal_errors and args.strict_validation:
                sys.exit(-1)

        if args.lint:
            return ""

        if not operator:
            operator = args.target
            template_path = XOSProcessor._get_template(operator)
        else:
            template_path = operator

        [template_folder, template_name] = os.path.split(template_path)
        os_template_loader = jinja2.FileSystemLoader(searchpath=[template_folder])
        os_template_env = jinja2.Environment(loader=os_template_loader)
        os_template_env = XOSProcessor._load_jinja2_extensions(
            os_template_env, args.attic
        )
        template = os_template_env.get_template(template_name)

        if args.output is not None and args.write_to_file == "model":
            # Handle the case where each model is written to a separate python file.
            rendered = {}

            for i, model in enumerate(v.models):
                model_dict = v.models[model]
                messages = [XOSProcessor._find_message_by_model_name(v.messages, model)]

                rendered[model] = template.render(
                    {
                        "proto": {
                            "message_table": {model: model_dict},
                            "messages": messages,
                            "policies": v.policies,
                            "message_names": [m["name"] for m in v.messages],
                        },
                        "context": context,
                        "options": v.options,
                    }
                )
                if not rendered[model]:
                    print("Not saving model %s as it is empty" % model, file=sys.stderr)
                else:
                    legacy = jinja2_extensions.base.xproto_list_evaluates_true(
                        [model_dict.get("options", {}).get("custom_python", None),
                         model_dict.get("options", {}).get("legacy", None),
                         v.options.get("custom_python", None),
                         v.options.get("legacy", None)])

                    if legacy:
                        file_name = "%s/%s_decl.%s" % (args.output, model.lower(), args.dest_extension)
                    else:
                        file_name = "%s/%s.%s" % (args.output, model.lower(), args.dest_extension)

                    file = open(file_name, "w")
                    file.write(rendered[model])
                    file.close()
                    if not args.quiet:
                        print("Saved: %s" % file_name, file=sys.stderr)
        else:
            # Handle the case where all models are written to the same python file.

            rendered = template.render(
                {
                    "proto": {
                        "message_table": v.models,
                        "messages": v.messages,
                        "policies": v.policies,
                        "message_names": [m["name"] for m in v.messages],
                    },
                    "context": context,
                    "options": v.options,
                }
            )
            if args.output is not None and args.write_to_file == "target":
                XOSProcessor._write_split_target(rendered, args.output, args.quiet)
            elif args.output is not None and args.write_to_file == "single":
                XOSProcessor._write_single_file(
                    rendered, args.output, args.dest_file, args.quiet
                )

        return rendered
