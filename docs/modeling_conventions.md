#Modeling Conventions

CORD adopts the following terminology and data modeling conventions
(some of which is carried over from an earlier Django-based implementation).

## Terminology

A *Model*  consists of a set of *Fields*. Each
Field has a *Type* and each Type has a set of *Attributes*. Some of these
Attributes are core (common across all Types) and some are
Type-specific. *Relationships* between Models are expressed by Fields
with one of a set of distinguished relationship-oriented Types (e.g,
*OneToOneField*). Finally, an *Object* is an instance (instantiation) of a
Model, where each Object has a unique primary key (or more precisely,
a primary index into the table that implements the Model). By
convention, that index/key is auto-generated for any Model that has
not identified a separate unique primary key. The default primary key
is always `id` for system level tables, and `pk` for model tables.

## Naming Conventions

Model names should use CamelCase without underscore. Model names should always
be singular, never plural. For example: `Slice`, `Network`, `Site`.

Sometimes a model is used to relate two other models, and
should be named after the two models that it relates. For example, a model that
relates the `Controller` and `User` models should be called `ControllerUser`.

Field names use lower case with underscores separating names. Examples of
valid field names are: name, `disk_format`, `controller_format`.

## Field Types

There are various built-in Fields that may be specified in a model specification.

| FieldType          | Why to Use It?     |
|--------------------|--------------------|
| BooleanField       | Displays as a checkbox in GUI; limits input to valid possibilities. If None is a valid option, please use *NullBooleanField* which uses default widget of choice: None, Yes, No.|
| CharField          | Allows for String representation, additional required attributes are "max_length". This should be used for small to large size strings. For mulitiple sentences, use TextField.|
| DateTimeField      | Special field that maps to python DateTime. May set optional attributes of *auto_now* (update field each time it is saved), *auto_add_now* (update field when created only) |
| EmailField         | Automatically checks for well formed Emails based on RFC3696/5321. Note that for full compliance we need to set the length to 254; default is 75. [**This is a bug in our model.**] |
| FloatField         | Used to represent a real number; default widget is TextInput.|
| IntegerField       | Used to represent Integer values; default widget is TextInput. [**We should review whether the IntegerFields should be changed to be PositiveIntegers, or PositiveSmalls accordingly.**]|
| GenericIPAddressField | Able to validate IPv4 and IPv6 flavors of addresses; default widget is TextInput.|
| URLField           | Verifies well formed URL, max_length is defaulted to 200.  GUI convenience is that the value of the field is displayed as a clickable link above the input widget.|
| SlugField          | Used to represent a short label for something containing only letters, numbers, underscores or hyphens. This should be used for the name of Tags so that there is a better chance of promoting the Tag to be an actual field attribute once the model has been solidified.|

## Core Field Attributes

The following Field-level optional attributes are currently in use.

| Attribute          | Effect             |
|--------------------|--------------------|
| verbose_name="..." | Provides a label to be used in the GUI display for this field. Differs from the field name itself, which is used to create the database table.|
| verbose_name_plural="..." | Way to override the verbose name for this field.|
| help_text="..." | Provides some context-based help for the field; will show up in the GUI display.|
| default=... | Allows a predefined default value to be specified.|
| choices=CHOICE_LIST | An interable (list or tuple). Allows the field to be filled in from an enumerated choice. For example, *ROLE_CHOICES = (('admin', 'Admin'), ('pi', 'Principle Investigator'), ('user','User'))*|
| unique=True |	Requires that the field be unique across all entries.|
| blank=True | Allows the field to be present but empty.|
| null=True | Allows the field to have a value of null if the field is blank.|
| editable=False | If you would like to make this a readOnly field to the user.|
| gui_hidden=True | Hide a particular field from the GUI. This can be specified for an entire model.|

The following Field-level optional attributes should not be used (or use judiciously).

| Attribute          | Why                |
|--------------------|--------------------|
| primary_key        | Some of the plugins we use, particularly in the REST area, do not do well with CharField's as the primary key. In general, it is best to use the system primary key instead, and put a *db_index=True, unique=True* on the CharField you would have used.|
| db_column, db_tablespace | Convention is to use the Field name as the db column, and use verbose_name if you want to change the display. For tablespace, all models should be defined within the application they are specified in. Overwriting the tablespace will make it more challenging for the next developer to find and fix any issues that might arise.|

The following Field-level optional attributes are not currently used but may
be used at some point.

| Attribute          | Effect             |
|--------------------|--------------------|
| db_index=True      | Allows for quicker queries if you are going to order by, or filter by, the specified field.|
| error_messages={...} | Pass in a dictionary of error keys, and the message you want to display if the error occurs.  For example: null, blank, invalid, invalid_choice, and unique. Other error messages may be present per FieldType.|
| validators=[...]      | Allows a list of validators to be run before committing the value of this field to the model. |

## Expressing Relationships

There are a few different types of Relationship-based fields.

| FieldType          | When to Use it     |
|--------------------|--------------------|
| ForeignKeyField    | Used to represent a 1-to-Many relationship. For example: Instance's may have 1 and only 1 Node; Node's may have 0 or more Instances. Can also be used to represent recursive relationships for the same object types by providing "self" as the relationship (first position) parameter.|
| ManyToManyField    | Used to represent an N-to-N relationship. For example: Deployments may have 0 or more Sites; Sites may have 0 or more Deployments.|
| OneToOneField      | Not currently in use, but would be useful for applications that wanted to augment a core class with their own additional settings. This has the same affect as a ForeignKey with unique=True.  The difference is that the reverse side of the relationship will always be 1 object (not a list).|
| GenericForeignKey | Not currently in use, but can be used to specify a non specific relation to "another object." Meaning object A relates to any other object. This relationship requires a reverse attribute in the "other" object to see the relationship -- but would primarily be accessed through the GenericForeignKey owner Model.
The nuances of these relationships is brought about by the additional optional attributes that can be ascribed to each Field.

>Note that we should likely convert our Tags to use GenericForeignKey
>so that all objects can be extensible during development, but then
>converted/promoted to attributes once the model has stabilized.

## Optional Attribute Side Effects

| Attribute          | Key Type           | Why                |
|--------------------|--------------------|--------------------|
| limit_choices_to   | ForeignKeyField, ManyToManyField | Not currently in use. Good to limit the possible selection choices for a remote relationship by some constraint.  Constraints may either be expressed by a dictionary of lookups, or by a Q object. |
| relate_name        | ForeignKeyField, ManyToManyField | The name to use for the relation back to this one.  This is extremely useful both to provide additional context in the way the objects are related but also when you have the same objects and object types related in different contexts to the same instance.|
| on_delete          | ForeignKeyField | Default behavior is to behave like "ON DELETE CASCADE." This may be turned of so long as the *null=True, blank=True* options are also set. For example, *user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)*|
| symmetrical        | ManyToManyField | Only used when ManyToManyField definition is against "self." For example, *class Person: friends = models.ManyToManyField("self")* would mean that if Person Alice is friended to Person Brian, then Brian is also Friends with Alice.|
| through            | ManyToManyField | Automatically creates a mapping table for ManyToMany relationships. By using this field, you can specify the exact mapping table you would like to use, therefore allowing you to augment/extend that table with additional data. |
| parent_link        | OneToOneField | Used only for multiple inheritance (specifically from a concrete class) to avoid additional/extra OneToOneFields being created via subclassing. |

## Avoid List

Avoid using the following optional attributes as they can have adverse
effects on data integrity and REST relationships:

| Attribute          | Effect             |
|--------------------|--------------------|
| to_field           | Would allow the relationship to exist against a field other than the primary key in the remote object.|
| db_constraint      | Controls whether or not a constraint should be created in the database for the foreignKey relationship. It defaults to True. If you set it to False you could cause database pointers to non-existent data. We should avoid this.|

## Model-Specific MetaData

| Model Setting      | When to use it     |
|--------------------|--------------------|
| abstract           | Used to specify that the defined model is not intended/able to be instantiated directly. For example, XOSBase, which is used to ensure that created, updated, and enacted fields will be provided for all XOS participating objects.|
| app_label          | Necessary if models are defined in modules other than models.py  In our core application we split out the model definitions into their own modules for clarity -- each of the models not derived from the XOSBase needs to explicitly state the "core" as the application this object is associated to. For example, XOSBase and User.|
| order_with_respect_to | |
| ordering | Defines the default column to order lists of the object type by. For example, Users => email.|
| description | Provide an explation of the model. It's rendered in the GUI to help the operator.|
| gui_hidden=True | Hide a particular model from the GUI. This can be specified for a single field.|



