#!/usr/bin/env python
from types import StringTypes
from lxml import etree
from StringIO import StringIO

# helper functions to help build xpaths
class XpathFilter:
    @staticmethod

    def filter_value(key, value):
        xpath = ""
        if isinstance(value, str):
            if '*' in value:
                value = value.replace('*', '')
                xpath = 'contains(%s, "%s")' % (key, value)
            else:
                xpath = '%s="%s"' % (key, value)
        return xpath

    @staticmethod
    def xpath(filter={}):
        xpath = ""
        if filter:
            filter_list = []
            for (key, value) in filter.items():
                if key == 'text':
                    key = 'text()'
                else:
                    key = '@'+key
                if isinstance(value, str):
                    filter_list.append(XpathFilter.filter_value(key, value))
                elif isinstance(value, list):
                    stmt = ' or '.join([XpathFilter.filter_value(key, str(val)) for val in value])
                    filter_list.append(stmt)
            if filter_list:
                xpath = ' and '.join(filter_list)
                xpath = '[' + xpath + ']'
        return xpath

# a wrapper class around lxml.etree._Element
# the reason why we need this one is because of the limitations
# we've found in xpath to address documents with multiple namespaces defined
# in a nutshell, we deal with xml documents that have
# a default namespace defined (xmlns="http://default.com/") and specific prefixes defined
# (xmlns:foo="http://foo.com")
# according to the documentation instead of writing
# element.xpath ( "//node/foo:subnode" )
# we'd then need to write xpaths like
# element.xpath ( "//{http://default.com/}node/{http://foo.com}subnode" )
# which is a real pain..
# So just so we can keep some reasonable programming style we need to manage the
# namespace map that goes with the _Element (its internal .nsmap being unmutable)
class XmlElement:
    def __init__(self, element, namespaces):
        self.element = element
        self.namespaces = namespaces

    # redefine as few methods as possible
    def xpath(self, xpath, namespaces=None):
        if not namespaces:
            namespaces = self.namespaces
        elems = self.element.xpath(xpath, namespaces=namespaces)
        return [XmlElement(elem, namespaces) for elem in elems]

    def add_element(self, tagname, **kwds):
        element = etree.SubElement(self.element, tagname, **kwds)
        return XmlElement(element, self.namespaces)

    def append(self, elem):
        if isinstance(elem, XmlElement):
            self.element.append(elem.element)
        else:
            self.element.append(elem)

    def getparent(self):
        return XmlElement(self.element.getparent(), self.namespaces)

    def get_instance(self, instance_class=None, fields=[]):
        """
        Returns an instance (dict) of this xml element. The instance
        holds a reference to this xml element.
        """
        if not instance_class:
            instance_class = Object
        if not fields and hasattr(instance_class, 'fields'):
            fields = instance_class.fields

        if not fields:
            instance = instance_class(self.attrib, self)
        else:
            instance = instance_class({}, self)
            for field in fields:
                if field in self.attrib:
                   instance[field] = self.attrib[field]
        return instance

    def add_instance(self, name, instance, fields=[]):
        """
        Adds the specifed instance(s) as a child element of this xml
        element.
        """
        if not fields and hasattr(instance, 'keys'):
            fields = instance.keys()
        elem = self.add_element(name)
        for field in fields:
            if field in instance and instance[field]:
                elem.set(field, unicode(instance[field]))
        return elem

    def remove_elements(self, name):
        """
        Removes all occurences of an element from the tree. Start at
        specified root_node if specified, otherwise start at tree's root.
        """

        if not name.startswith('//'):
            name = '//' + name 
        elements = self.element.xpath('%s ' % name, namespaces=self.namespaces)
        for element in elements:
            parent = element.getparent()
            parent.remove(element)

    def delete(self):
        parent = self.getparent()
        parent.remove(self)

    def remove(self, element):
        if isinstance(element, XmlElement):
            self.element.remove(element.element)
        else:
            self.element.remove(element)

    def set_text(self, text):
        self.element.text = text

    # Element does not have unset ?!?
    def unset(self, key):
        del self.element.attrib[key]

    def toxml(self):
        return etree.tostring(self.element, encoding='UTF-8', pretty_print=True)

    def __str__(self):
        return self.toxml()

    # are redirected on self.element
    def __getattr__ (self, name):
        if not hasattr(self.element, name):
            raise AttributeError, name
        return getattr(self.element, name)

class Xml:

    def __init__(self, xml=None, namespaces=None):
        self.root = None
        self.namespaces = namespaces
        self.default_namespace = None
        self.schema = None
        if isinstance(xml, basestring):
            self.parse_xml(xml)
        if isinstance(xml, XmlElement):
            self.root = xml
            self.namespaces = xml.namespaces
        elif isinstance(xml, etree._ElementTree) or isinstance(xml, etree._Element):
            self.parse_xml(etree.tostring(xml))

    def parse_xml(self, xml):
        """
        parse rspec into etree
        """
        parser = etree.XMLParser(remove_blank_text=True)
        try:
            tree = etree.parse(xml, parser)
        except IOError:
            # 'rspec' file doesnt exist. 'rspec' is proably an xml string
            try:
                tree = etree.parse(StringIO(xml), parser)
            except Exception, e:
                raise Exception, str(e)
        root = tree.getroot()
        self.namespaces = dict(root.nsmap)
        # set namespaces map
        if 'default' not in self.namespaces and None in self.namespaces:
            # If the 'None' exist, then it's pointing to the default namespace. This makes
            # it hard for us to write xpath queries for the default naemspace because lxml
            # wont understand a None prefix. We will just associate the default namespeace
            # with a key named 'default'.
            self.namespaces['default'] = self.namespaces.pop(None)

        else:
            self.namespaces['default'] = 'default'

        self.root = XmlElement(root, self.namespaces)
        # set schema
        for key in self.root.attrib.keys():
            if key.endswith('schemaLocation'):
                # schemaLocation should be at the end of the list.
                # Use list comprehension to filter out empty strings
                schema_parts  = [x for x in self.root.attrib[key].split(' ') if x]
                self.schema = schema_parts[1]
                namespace, schema  = schema_parts[0], schema_parts[1]
                break

    def parse_dict(self, d, root_tag_name='xml', element = None):
        if element is None:
            if self.root is None:
                self.parse_xml('<%s/>' % root_tag_name)
            element = self.root.element

        if 'text' in d:
            text = d.pop('text')
            element.text = text

        # handle repeating fields
        for (key, value) in d.items():
            if isinstance(value, list):
                value = d.pop(key)
                for val in value:
                    if isinstance(val, dict):
                        child_element = etree.SubElement(element, key)
                        self.parse_dict(val, key, child_element)
                    elif isinstance(val, basestring):
                        child_element = etree.SubElement(element, key).text = val

            elif isinstance(value, int):
                d[key] = unicode(d[key])
            elif value is None:
                d.pop(key)

        # element.attrib.update will explode if DateTimes are in the
        # dcitionary.
        d=d.copy()
        # looks like iteritems won't stand side-effects
        for k in d.keys():
            if not isinstance(d[k],StringTypes):
                del d[k]

        element.attrib.update(d)

    def validate(self, schema):
        """
        Validate against rng schema
        """
        relaxng_doc = etree.parse(schema)
        relaxng = etree.RelaxNG(relaxng_doc)
        if not relaxng(self.root):
            error = relaxng.error_log.last_error
            message = "%s (line %s)" % (error.message, error.line)
            raise Exception, message
        return True

    def xpath(self, xpath, namespaces=None):
        if not namespaces:
            namespaces = self.namespaces
        return self.root.xpath(xpath, namespaces=namespaces)

    def set(self, key, value):
        return self.root.set(key, value)

    def remove_attribute(self, name, element=None):
        if not element:
            element = self.root
        element.remove_attribute(name)

    def add_element(self, *args, **kwds):
        """
        Wrapper around etree.SubElement(). Adds an element to
        specified parent node. Adds element to root node is parent is
        not specified.
        """
        return self.root.add_element(*args, **kwds)

    def remove_elements(self, name, element = None):
        """
        Removes all occurences of an element from the tree. Start at
        specified root_node if specified, otherwise start at tree's root.
        """
        if not element:
            element = self.root

        element.remove_elements(name)

    def add_instance(self, *args, **kwds):
        return self.root.add_instance(*args, **kwds)

    def get_instance(self, *args, **kwds):
        return self.root.get_instnace(*args, **kwds)

    def get_element_attributes(self, elem=None, depth=0):
        if elem == None:
            elem = self.root
        if not hasattr(elem, 'attrib'):
            # this is probably not an element node with attribute. could be just and an
            # attribute, return it
            return elem
        attrs = dict(elem.attrib)
        attrs['text'] = str(elem.text).strip()
        attrs['parent'] = elem.getparent()
        if isinstance(depth, int) and depth > 0:
            for child_elem in list(elem):
                key = str(child_elem.tag)
                if key not in attrs:
                    attrs[key] = [self.get_element_attributes(child_elem, depth-1)]
                else:
                    attrs[key].append(self.get_element_attributes(child_elem, depth-1))
        else:
            attrs['child_nodes'] = list(elem)
        return attrs

    def append(self, elem):
        return self.root.append(elem)

    def iterchildren(self):
        return self.root.iterchildren()

    def merge(self, in_xml):
        pass

    def __str__(self):
        return self.toxml()

    def toxml(self):
        return etree.tostring(self.root.element, encoding='UTF-8', pretty_print=True)

    # XXX smbaker, for record.load_from_string
    def todict(self, elem=None):
        if elem is None:
            elem = self.root
        d = {}
        d.update(elem.attrib)
        d['text'] = elem.text
        for child in elem.iterchildren():
            if child.tag not in d:
                d[child.tag] = []
            d[child.tag].append(self.todict(child))

        if len(d)==1 and ("text" in d):
            d = d["text"]

        return d

    def save(self, filename):
        f = open(filename, 'w')
        f.write(self.toxml())
        f.close()

    
