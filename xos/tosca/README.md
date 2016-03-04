## TOSCA Interface Definition

This directory implements a TOSCA interface for XOS,
which can be extended to include specifications for
service models added to XOS. The directory is organized
as follows:

 * custom_types -- Defines schema for XOS-specific models.
   * `.m4` files are source.
   * `.yaml` files are generated.
 * definitions -- Defines schema for TOSCA's base models.
 * resources -- Translates TOSCA specification to Django API.
 * sample -- Example TOSCA models.
