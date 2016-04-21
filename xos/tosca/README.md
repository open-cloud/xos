## TOSCA Interface Definition

This directory implements a TOSCA interface for XOS,
which can be extended to include specifications for
service models added to XOS. The directory is organized
as follows:

 * custom_types -- Defines schema for XOS-specific models.
   * `.m4` source files
   * `.yaml` generated files
 * definitions -- Defines schema for TOSCA's base models.
 * resources -- Translates TOSCA to Django API.
 * sample -- Example TOSCA specifications.
