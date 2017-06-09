# xproto

xproto is a variant of Google Protobufs that incorporates XOS’ data modeling features. Its goal is to encode XOS data models and facilitate the generation of code that depends on those data models.

In general, the goal of XOS data modeling is to abstract technology-independent information out of service implementations. An example of this is the database layer of XOS, which is implemented purely in xproto, and converted into Django data models at build time, but could also target a different technology, such as NoSQL.

In this chapter, we explain how to write xproto specs and how to use the xproto toolset to generate code. It is assumed that you are in a working CORD development environment. Please consult [this document](https://github.com/opencord/platform-install#creating-a-development-environment-on-you-machine) for instructions on how to bring one up. You do not need to bring up a full pod to use xproto, the frontend environment described in the linked document is sufficient.


## Generating code from an existing xproto file

> NOTE: To work with `xproto` please setup the python virtual environment as describred [here](local_env.md)

Drop an xproto file in your working directory. You can copy and paste the following content into a file named `slice.xproto`.

```protobuf
message Slice (PlCoreBase){
     required string name = 1 [max_length = 80, content_type = "stripped", blank = False, help_text = "The Name of the Slice", null = False, db_index = False];
     required bool enabled = 2 [help_text = "Status for this Slice", default = True, null = False, db_index = False, blank = True];
     required bool omf_friendly = 3 [default = False, null = False, db_index = False, blank = True];
     required string description = 4 [help_text = "High level description of the slice and expected activities", max_length = 1024, null = False, db_index = False, blank = True];
     required string slice_url = 5 [db_index = False, max_length = 512, null = False, content_type = "url", blank = True];
     required manytoone site->Site:slices = 6 [help_text = "The Site this Slice belongs to", null = False, db_index = True, blank = False];
     required int32 max_instances = 7 [default = 10, null = False, db_index = False, blank = False];
     optional manytoone service->Service:slices = 8 [db_index = True, null = True, blank = True];
     optional string network = 9 [blank = True, max_length = 256, null = True, db_index = False, choices = "((None, 'Default'), ('host', 'Host'), ('bridged', 'Bridged'), ('noauto', 'No Automatic Networks'))"];
     optional string exposed_ports = 10 [db_index = False, max_length = 256, null = True, blank = True];
     optional manytoone serviceClass->ServiceClass:slices = 11 [db_index = True, null = True, blank = True];
     optional manytoone creator->User:slices = 12 [db_index = True, null = True, blank = True];
     optional manytoone default_flavor->Flavor:slices = 13 [db_index = True, null = True, blank = True];
     optional manytoone default_image->Image:slices = 14 [db_index = True, null = True, blank = True];
     optional manytoone default_node->Node:slices = 15 [db_index = True, null = True, blank = True];
     optional string mount_data_sets = 16 [default = "GenBank", max_length = 256, content_type = "stripped", blank = True, null = True, db_index = False];
     required string default_isolation = 17 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
     required manytomany tags->Tag = 18 [db_index = False, null = False, blank = True];
}
```
To generate a Django model starting from this file you can use:
`xosgenx --target="django.xtarget" --output=. --write-to-file="model" --dest-extension="py" slice.xproto`
This should generate a file called `slice.py` in your current directory. 
If there were multiple files, then it would generate python Django models for each of them.

The tool that processes xproto files and generates code is called `xosgenx`. You can print its syntax by running `xosgenx --help`.

```
usage: xosgenx [-h] [--rev] --target TARGET [--output OUTPUT] [--attic ATTIC]
               [--kvpairs KV] [--write-to-file {single,model,target}]
               [--dest-file DEST_FILE | --dest-extension DEST_EXTENSION]
               <input file> [<input file> ...]

XOS Generative Toolchain

positional arguments:
  <input file>          xproto files to compile

optional arguments:
  -h, --help            show this help message and exit
  --rev                 Convert proto to xproto
  --target TARGET       Output format, corresponding to <output>.yaml file
  --output OUTPUT       Destination dir
  --attic ATTIC         The location at which static files are stored
  --kvpairs KV          Key value pairs to make available to the target
  --write-to-file {single,model,target}
                        Single output file (single) or output file per model
                        (model) or let target decide (target)
  --dest-file DEST_FILE
                        Output file name (if write-to-file is set to single)
  --dest-extension DEST_EXTENSION
                        Output file extension (if write-to-file is set to
                        single)
```


## Writing an xproto file 

xproto is based on Google Protobufs. This means that any protobuf file also qualifies as xproto. We currently use the Protobuf v2 syntax. For example, the file below specifies a model that describes container images:

```protobuf
message Image {
     required string name = 1 [db_index = False, max_length = 256, null = False, content_type = "stripped", blank = False];
     required string kind = 2 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'))", max_length = 30, blank = False, null = False, db_index = False];
     required string disk_format = 3 [db_index = False, max_length = 256, null = False, content_type = "stripped", blank = False];
     required string container_format = 4 [db_index = False, max_length = 256, null = False, content_type = "stripped", blank = False];
     optional string path = 5 [max_length = 256, content_type = "stripped", blank = True, help_text = "Path to image on local disk", null = True, db_index = False];
     optional string tag = 6 [max_length = 256, content_type = "stripped", blank = True, help_text = "For Docker Images, tag of image", null = True, db_index = False];
}
```

xproto contains several extensions, encoded as Protobuf options, which the xproto toolchain recognizes at the top level. That is, these options are not declared explicitly in Protobuf syntax.


## xproto extensions to Google Protobufs

**Inheritance**

- xproto
  ```protobuf
  message EC2Instance (Instance, EC2Object) {
        // EC2Instance inherits the fields of  Instance
  }
  ```

- protobuf
  ```protobuf
  message EC2Instance  {
        option bases = "Instance,EC2Object"
  }
  ```

Inheritance instructs the xproto processor that a model inherits the fields of a set of base models. Note that these base model fields are not copied into the derived model automatically. However, the fields can be accessed in an xproto target.

**Links**

- xproto
  ```protobuf
  message Instance {
        required manytoone slice:Slice->instances = 1;
  }
  ```

- protobuf
  ```protobuf
  message Instance {
        required int32 slice = 1 [model="Slice", link="manytoone", src_port="slice", dst_port="instances"];
  }
  ```

Links are references to one model from another. A link specifies the type of the reference (manytoone, manytomany, onetomany, or onetoone), name of the field that contains the reference (_slice_ in the above example), its type (Slice), the name of the field in the peer model that points back to the current model, and a “through” field, specifying a model declared separately as an xproto message, that stores properties of the link.

The example below illustrates a manytomany link from Image to Deployment, which goes through the model “ImageDeployments”

- xproto

  ```protobuf
  required manytomany deployments->Deployment/ImageDeployments:images = 7 [help_text = "Select which images should be instantiated on this deployment", null = False, db_index = False, blank = True];
  ```


- Protobuf

  ```protobuf
  required int32 deployments = 7 [help_text = "Select which images should be instantiated on this deployment", null = False, db_index = False, blank = True, model="Deployment", through="ImageDeployments", dst_port="images", link="manytomany"];
  ```


**Model options**

```protobuf
option name = "Name of service"
option verbose_name = "Verbose name of service";
option app_name = "Name of app containing service";
```

The above options declare information about models. They can be declared for models individually, or at the top level in the xproto definition, in which case they are inherited by all of the models in that definition.

**Field options**

The field options supported by the xproto processor are listed below.

```protobuf
option null = True/False
```

The null option specifies whether a field has to be set or not.

```protobuf
option help_text = “Descriptive text goes here”;
```

Help text describes a field.

```protobuf
option default = “Default value of field”;
```

The default value of the field.

```protobuf
option max_length = 128;
```

The maximum length of a field whose type is string.

```protobuf
option blank = False;
```

Whether a field can be empty.

```protobuf
option choices = "(('vm', 'Virtual Machine'), ('container', 'Container'))"
```

The set of valid values for a field. Each inner tuple specifies equivalence classes. E.g. vm is equivalent to Virtual Machine.

```protobuf
option db_index = True
```

Whether the field is an index field. Used by database targets.


## The xproto toolchain: an overview 

The figure below illustrates the processing of an xproto file. The xosgen tool converts the xproto file into an intermediate representation and passes it to a target, which in turn generates the output code. The target has access to a library of auxiliary functions implemented in Python. The target itself is written as a jinja2 template.

![xproto toolchain](./toolchain.png)

## The IR 

The IR is a representation of a parsed xproto file in the form of nested Python dictionaries. Here is a description of its structure.

```protobuf
"proto": {
    "messages": [
         {"name": "foo", fields: [{...}], links: [{...}], rlinks: [{...}], options: [{...}]}
    ]
},
"context": {
    "command line option 1": "value - see the --kv option of xosgen"
},
"options": {
    "top level option 1": "value of option 1"
}
```


## Writing a target 

A target is a template written in jinja2 that takes the IR described in the previous section as input and generates some code, such as Python, Protobufs, unit tests etc. We will take up a few examples. The example below generates a GraphViz dot file from a set of xproto representations:

```python
digraph {
{% for m in proto.messages %}
  {%- for l in m.links %}
  {{ m.name }} -> {{ l.peer }};
  {%- endfor %}
{% endfor %}
}```

This target loops through all of the messages in a proto definition and through the links in each message. For each link, it formats and outputs an edge in a graph in Graphviz’ dot notation.

```
{{ proto }}
```

This target simply prints the IR for an xproto definition.

```python
{% for m in proto.messages -%}
{% for r in m.rlinks %}
    def enumerate_{{ xos_singularize(r) }}_ids:
        return map(lambda x:x['id'], {{ xos_pluralize(r) }})
{% endfor %}
{% endfor -%}
```

The target above outputs a Python function that enumerates the ids of the objects from which the current object is linked.

## Library functions

xproto targets can use a set of library functions implemented in Python. These can be found in the file lib.py in the genx/tool directory. These functions are listed below

- `xproto_unquote(string)` Unquotes a string. For example, `"This is a help string"` is converted into `This is a help string.`    
- `xproto_singularize(field)` Converts an english plural into its singular. It is extracted from the `singular` option for a field if such an option is specified, otherwise, it performs the conversion automatically using the library `pattern.en`.
- `xproto_pluralize(field)` The reverse of xproto_singularize.

