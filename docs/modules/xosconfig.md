# Xos Config

This module is responsible to read, validate and distribute the configuration for all
the XOS based components.

_The code for this module can be found in lib/xos-config_

The `xosconfig` module use a combination of parameters provided via a `.yaml` file and a service discovery mechanism.

## How to use this module

This module needs to be initialized once (and only once) when you application start, you can do it with:
```python
from xosconfig import Config
Config.init()
```

By default the `xosconfig` module will look for a configuration file in `/opt/xos/config.yaml`, if for any reason you need to pass a different config file it can be done with:
```python
from xosconfig import Config
Config.init("/path/to/my/config.yaml")
```

### Configuration defaults
Note that defaults are defined for some of the configuration items. Defaults are defined in `lib/xos-config/xosconfig/default.py`.

### Reading data from the configuration file

To access static information defined in the `config.yaml` file you can use this api:
```python
from xosconfig import Config
res = Config.get('database')
```
this call will return something like:
```python
{
    'username': 'test',
    'password': 'safe'
}
```
Since the configuration support nested dictionary is possible to query directly nested values using a `dot` notation, for example:
```python
from xosconfig import Config
res = Config.get('database.username')
```
will return:
```python
"test"
```
**The configuration schema is defined in `/lib/xos-config/config-schema.yaml`**

### Reading service information

XOS is composed by a plethora of services, to discover them and their address we are using
a tool called [registrator](https://github.com/gliderlabs/registrator).
 
#### Retrieve a list of services:
```python
from xosconfig import Config
Config.get_service_list()
```
this call will return an array of available services, by default:
```python
[
  "xos-ws",
  "xos-ui-deprecated",
  "xos-rest",
  "xos-gui",
  "xos-db",
  "consul-rest",
  "consul",
]
```
>You can get the same information on the `head node` using:
>```bash
> curl consul:8500/v1/catalog/services
>```

#### Retrieve information for a single service:
```python
from xosconfig import Config
Config.get_service_info('xos-db')
```
that will return:
```python
{
    'name': 'xos-db',
    'url': '172.18.0.4',
    'port': 5432
}
```
>You can get the same information on the `head node` using:
>```bash
> curl consul:8500/v1/catalog/service/xos-db
>```

#### Retrieve endpoint for a single service:
```python
from xosconfig import Config
Config.get_service_endpoint('xos-db')
```
that will return:
```python
"http://172.18.0.4:5432"
```