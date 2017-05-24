import plyxproto.model as m
import pdb
import plyxproto.parser as plyxproto
import traceback
import sys
import jinja2
import os
from xos2jinja import XOS2Jinja
from proto2xproto import Proto2XProto

import lib
import yaml

loader = jinja2.PackageLoader(__name__, 'templates')
env = jinja2.Environment(loader=loader)

class XOSGenerator:
    def __init__(self, args):
        self.args = args
	self.input = None

    def file_exists(self):
        def file_exists2(name):
            try:
                path = self.args.attic+'/'+name
            except TypeError:
                path = name
            return (os.path.exists(path))
        return file_exists2

    def include_file(self):
        def include_file2(name):
            try:
                path = self.args.attic+'/'+name
            except TypeError:
                path = name
            return open(path).read()
        return include_file2

        # FIXME: Support templates in the future
        #return jinja2.Markup(loader.get_source(env, name)[0])

    def format_list(self):
	def format_list2(input_list, format_string, arguments=[]):
    	    return [format_string % tuple(arguments + [s]) for s in input_list]
	return format_list2


    def generate(self):
        try:
            parser = plyxproto.ProtobufAnalyzer()
            input = self.input
            ast = parser.parse_string(input,debug=0)

            if (self.args.rev):
                v = Proto2XProto()
                ast.accept(v)
            
            v = XOS2Jinja()
            ast.accept(v)
            
            try:
                template_name = self.args.template_dir + '/' + self.args.target
            except AttributeError:
                template_name = os.path.abspath(self.args.target)

            os_template_loader = jinja2.FileSystemLoader( searchpath=[os.path.split(template_name)[0]])
            os_template_env = jinja2.Environment(loader=os_template_loader)
            os_template_env.globals['include_file'] = self.include_file() # Generates a function
            os_template_env.globals['file_exists'] = self.file_exists() # Generates a function
            os_template_env.filters['yaml'] = yaml.dump
            os_template_env.globals['zip'] = zip
            os_template_env.filters['format_list'] = self.format_list() # Generates a function

            for f in dir(lib):
                if f.startswith('xproto'):
                    os_template_env.globals[f] = getattr(lib, f)

            template = os_template_env.get_template(os.path.split(template_name)[1])
            context = {}

            try:
                for s in self.args.kv.split(','):
                    k,val=s.split(':')
                    context[k]=val
            except:
                pass

            rendered = template.render({"proto": {'message_table':v.models, 'messages':v.messages, 'message_names':[m['name'] for m in v.messages]},"context":context,"options":v.options})

            lines = rendered.splitlines()

            current_buffer = []
            for l in lines:
                if (l.startswith('+++')):
                    prefix = ''
                    prefixes = self.args.output.rsplit('/',1)
                    if (len(prefixes)>1):
                        path = prefix+'/'+l[4:]
                        direc = prefix
                        if (direc):
                            os.system('mkdir -p %s'%direc)
                    else:
                        path = l[4:]
                    
                    fil = open(path,'w')
                    buf = '\n'.join(current_buffer)

                    obuf = buf

                    """
                    for d in options.dict:
                        df = open(d).read()
                        d = json.loads(df)

                        pattern = re.compile(r'\b(' + '|'.join(d.keys()) + r')\b')
                        obuf = pattern.sub(lambda x: d[x.group()], buf)
                    """

                    fil.write(obuf)
                    fil.close()

                    try:
                        quiet = self.args.quiet
                    except:
                        quiet = False
                    if (not quiet):
                        print 'Written to file %s'%path

                    current_buffer = []
                else:
                    current_buffer.append(l)

            if (current_buffer):
                print '\n'.join(current_buffer)


        except Exception as e:
            print "    Error occurred! file[%s]" % (self.args.inputs), e
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            raise e
    
def main():
    generator = XOSGenerator(args)
    generator.generate()

if __name__=='__main__':
    main()
