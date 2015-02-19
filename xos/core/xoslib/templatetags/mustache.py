from django import template
from django.conf import settings
import pystache
import os

register = template.Library()

class View(pystache.View):
    template_path = settings.TEMPLATE_DIRS[0]

    def __init__(self, template_dir, template_name, context):
        self.template_path = template_dir
        self.template_name = template_name
        return super(View, self).__init__(context=context)

class MustacheNode(template.Node):
    def __init__(self, template_name, attr=None):
        for template_dir in settings.TEMPLATE_DIRS:
            if os.path.exists(os.path.join(template_dir, template_name) + ".mustache"):
                break
        else:
            raise IOError("failed to find %s in %s" % (template_name, str(settings.TEMPLATE_DIRS)))

        self.template_path = template_dir
        self.template = template_name
        self.attr = attr

    def render(self, context):
        mcontext = context[self.attr] if self.attr else {}
        view = View(self.template_path, self.template, context=mcontext)
        return view.render()

def do_mustache(parser, token):
    """
    Loads a mustache template and render it inline
    
    Example::
    
    {% mustache "foo/bar" data %}
    
    """
    bits = token.split_contents()
    if len(bits) not in  [2,3]:
        raise template.TemplateSyntaxError("%r tag takes two arguments: the location of the template file, and the template context" % bits[0])
    path = bits[1]
    path = path[1:-1]
    attrs = bits[2:]
    return MustacheNode(path, *attrs)


register.tag("mustache", do_mustache)
