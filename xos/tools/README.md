## Overview of XOS tools

### modelgen

Modelgen reads the XOS models and applies those models to a template to generate output. 

Examples:
  * ./modelgen -a core api.template.py > ../../xos/xosapi.py            
  * ./modelgen -a services.hpc -b Service -b User hpc-api.template.py > ../../xos/hpcapi.py
