# Managing Configurations

XOS comes with several pre-configured environments. The main available configurations are:

- Frontend Only
- CORD
Every configuration comes with different settings and different features, from GUI elements to Services.

__NOTE: files should not be added by hand to this folder. They will break the configuration system.__

## Basic configuration

A common configuration file is saved in `xos/configurations/common/xos_common_config`. This file stores all the common configurations for XOS.

This is the base config:
``
[plc]
name=plc
deployment=plc

[db]
name=xos
user=postgres
password=password
host=localhost
port=5432

[api]
host=localhost
port=8000
ssl_key=None
ssl_cert=None
ca_ssl_cert=None
ratelimit_enabled=0
omf_enabled=0
mail_support_address=support@localhost
nova_enabled=True
logfile=/var/log/xos.log

[nova]
admin_user=admin@domain.com
admin_password=admin
admin_tenant=admin
url=http://localhost:5000/v2.0/
default_image=None
default_flavor=m1.small
default_security_group=default
ca_ssl_cert=/etc/ssl/certs/ca-certificates.crt

[observer]
pretend=False
backoff_disabled=False
images_directory=/opt/xos/images
dependency_graph=/opt/xos/model-deps
logfile=/var/log/xos_backend.log

[gui]
disable_minidashboard=True
branding_name=Open Cloud
#branding_css= #no branding css is provided by default
branding_icon=/static/logo.png

``

## Extending configuration

### How it works

In some environments changes to the configuration are needed. To achieve this, XOS reads configurations from a `xos/xos_configuration`.

All the configuration files in this folder are parsed with [ConfigParser](https://docs.python.org/2/library/configparser.html).

### Extending a configuration

_An example is available in the CORD config_

These are the basic step to extend a configuration. 
_The following uses `myConf` as a placeholder for the current configuration._

**Local Config**

- In your configuration create a new config file named: `xos_<myConf>_config`
Sample local config:
``
[gui]
branding_name=A BRAND NAME
branding_icon=/static/my_logo.png
``

_The file above will change the displayed brand name and the logo in the UI_

**Makefile Changes**
- Clean the configuration folder: `rm ../../xos_configuration/*`
- - Add the common config: `cp ../common/xos_common_config ../../xos_configuration/`
- - Add the local config: `cp ./xos_<myConf>_config ../../xos_configuration/`
_IMPORTANT: this instructions have to be executed before `docker build`_



