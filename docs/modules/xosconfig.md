# XOS Configuration

The `xosconfig` module is used to read, validate and distribute configuration
information for all XOS-related components.

The code for this module can be found in `lib/xos-config`.

The `xosconfig` module uses a combination of parameters provided via a `.yaml`
file and a service discovery mechanism.

## How to Use This Module

This module needs to be initialized once (and only once) when XOS starts. You
can do it with:

```python
from xosconfig import Config
Config.init()
```

By default, `xosconfig` looks for a configuration file in
`/opt/xos/config.yaml`. Passing a different config file can be done with:

```python
from xosconfig import Config
Config.init("/path/to/my/config.yaml")
```

### Configuration Defaults

Defaults are defined for some of the configuration items in
`lib/xos-config/xosconfig/default.py`.

### Reading Data from the Configuration File

To access static information defined in the `config.yaml` file, use the
following API:

```python
from xosconfig import Config
res = Config.get('database')
```

This call returns something like:

```python
{
    'username': 'test',
    'password': 'safe'
}
```

Since the configuration supports a nested dictionary, it is possible to query
directly nested values using `dot` notation. For example:

```python
from xosconfig import Config
res = Config.get('database.username')
```

returns:

```python
"test"
```

**The configuration schema is defined in `/lib/xos-config/config-schema.yaml`**
