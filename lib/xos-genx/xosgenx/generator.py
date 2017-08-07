
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


import plyxproto.parser as plyxproto
import jinja2
import os
from xos2jinja import XOS2Jinja
from proto2xproto import Proto2XProto
import jinja2_extensions
import yaml

loader = jinja2.PackageLoader(__name__, 'templates')
env = jinja2.Environment(loader=loader)

class XOSGenerator:

    @staticmethod
    def _read_input_from_files(files):
        input = ''
        for fname in files:
            with open(fname) as infile:
                input += infile.read()
        return input

    @staticmethod
    def _attach_parser(ast, args):
        if hasattr(args, 'rev') and args.rev:
            v = Proto2XProto()
            ast.accept(v)

        v = XOS2Jinja()
        ast.accept(v)
        return v

    @staticmethod
    def _get_template(target):
        if not os.path.isabs(target):
            return os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/targets/' + target)
        return target

    @staticmethod
    def _file_exists(attic):
        # NOTE this method can be used in the jinja template
        def file_exists2(name):
            if attic is not None:
                path = attic + '/' + name
            else:
                path = name
            return (os.path.exists(path))

        return file_exists2

    @staticmethod
    def _include_file(attic):
        # NOTE this method can be used in the jinja template
        def include_file2(name):
            if attic is not None:
                path = attic + '/' + name
            else:
                path = name
            return open(path).read()
        return include_file2

    @staticmethod
    def _load_jinja2_extensions(os_template_env, attic):

        os_template_env.globals['include_file'] = XOSGenerator._include_file(attic)  # Generates a function
        os_template_env.globals['file_exists'] = XOSGenerator._file_exists(attic)  # Generates a function

        os_template_env.filters['yaml'] = yaml.dump
        for f in dir(jinja2_extensions):
            if f.startswith('xproto'):
                os_template_env.globals[f] = getattr(jinja2_extensions, f)
        return os_template_env

    @staticmethod
    def _add_context(args):
        if not hasattr(args, 'kv') or not args.kv:
            return
        try:
            context = {}
            for s in args.kv.split(','):
                k, val = s.split(':')
                context[k] = val
            return context
        except Exception, e:
            print e.message

    @staticmethod
    def _write_single_file(rendered, dir, dest_file, quiet):

        file_name = "%s/%s" % (dir, dest_file)
        file = open(file_name, 'w')
        file.write(rendered)
        file.close()
        if quiet == False:
            print "Saved: %s" % file_name

    @staticmethod
    def _write_file_per_model(rendered, dir, extension, quiet):
        for m in rendered:

            file_name = "%s/%s.%s" % (dir, m.lower(), extension)
            if not rendered[m]:
                if quiet == False:
                    print "Not saving %s as it is empty" % file_name
            else:
                file = open(file_name, 'w')
                file.write(rendered[m])
                file.close()
                if quiet == False:
                    print "Saved: %s" % file_name

    @staticmethod
    def _write_split_target(rendered, dir, quiet):

        lines = rendered.splitlines()
        current_buffer = []
        for l in lines:
            if (l.startswith('+++')):

                if dir:
                    path = dir + '/' + l[4:].lower()

                fil = open(path, 'w')
                buf = '\n'.join(current_buffer)

                obuf = buf

                fil.write(obuf)
                fil.close()

                if quiet == False:
                    print "Save file to: %s" % path

                current_buffer = []
            else:
                current_buffer.append(l)

    @staticmethod
    def _find_message_by_model_name(messages, model):
        return next((x for x in messages if x['name'] == model), None)

    @staticmethod
    def generate(args):

        # Setting defaults
        if not hasattr(args, 'attic'):
            args.attic = None
        if not hasattr(args, 'write_to_file'):
            args.write_to_file = None
        if not hasattr(args, 'dest_file'):
            args.dest_file = None
        if not hasattr(args, 'dest_extension'):
            args.dest_extension = None
        if not hasattr(args, 'output'):
            args.output = None
        if not hasattr(args, 'quiet'):
            args.quiet = True

        # Validating
        if args.write_to_file == 'single' and args.dest_file is None:
            raise Exception("[XosGenX] write_to_file option is specified as 'single' but no dest_file is provided")
        if args.write_to_file == 'model' and args.dest_extension is None:
            raise Exception("[XosGenX] write_to_file option is specified as 'model' but no dest_extension is provided")

        if args.output is not None and not os.path.isabs(args.output):
            raise Exception("[XosGenX] The output dir must be an absolute path!")
        if args.output is not None and not os.path.isdir(args.output):
            raise Exception("[XosGenX] The output dir must be a directory!")

        if hasattr(args, 'files'):
            inputs = XOSGenerator._read_input_from_files(args.files)
        elif hasattr(args, 'inputs'):
            inputs = args.inputs
        else:
            raise Exception("[XosGenX] No inputs provided!")

        template_path = XOSGenerator._get_template(args.target)
        [template_folder, template_name] = os.path.split(template_path)
        os_template_loader = jinja2.FileSystemLoader(searchpath=[template_folder])
        os_template_env = jinja2.Environment(loader=os_template_loader)
        os_template_env = XOSGenerator._load_jinja2_extensions(os_template_env, args.attic)
        template = os_template_env.get_template(template_name)
        context = XOSGenerator._add_context(args)

        parser = plyxproto.ProtobufAnalyzer()
        ast = parser.parse_string(inputs, debug=0)
        v = XOSGenerator._attach_parser(ast, args)

        if args.output is not None and args.write_to_file == "model":
            rendered = {}
            for i, model in enumerate(v.models):
                models = {}
                models[model] = v.models[model]
                messages = [XOSGenerator._find_message_by_model_name(v.messages, model)]

                rendered[model] = template.render(
                    {"proto":
                        {
                            'message_table': models,
                            'messages': messages,
                            'policies': v.policies,
                            'message_names': [m['name'] for m in messages]
                        },
                        "context": context,
                        "options": v.options
                    }
                )
            XOSGenerator._write_file_per_model(rendered, args.output, args.dest_extension, args.quiet)
        else:
            rendered = template.render(
                {"proto":
                    {
                        'message_table': v.models,
                        'messages': v.messages,
                        'policies': v.policies,
                        'message_names': [m['name'] for m in v.messages]
                    },
                    "context": context,
                    "options": v.options
                }
            )
            if args.output is not None and args.write_to_file == "target":
                XOSGenerator._write_split_target(rendered, args.output, args.quiet)
            elif args.output is not None and args.write_to_file == "single":
                XOSGenerator._write_single_file(rendered, args.output, args.dest_file, args.quiet)

        return rendered
