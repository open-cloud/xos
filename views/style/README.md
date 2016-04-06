# XOS Styles

This folder holds style definition for XOS and a collection of tools usefull to work with them.

## Setup

The best way to work with XOS styling and appearance is to have the `frontend` configuration running locally on your machine. In this way most of the GUI files are shared (see below). To use the provided tools as they are XOS should be available at `http://xos.dev:9999`.

Before start working on the UI you should also install the dependencies, so enter `xos/views/style/` and execute `npm install` (NodeJs is required).

## Developing

When your environment is ready you could start it with `npm start`, this command will:
  - Whatch styles in `xos/views/style/sass` and compile them on change
  - Reload the broser on file changes (for more details see `xos/views/style/bs-config.js`)

## Shared files:
Shared files are defined in `xos/configurations/frontend/docker-compose.yml`, for the `frontend` configuration they are:
```
  - ../common/xos_common_config:/opt/xos/xos_configuration/xos_common_config
  - ../../core/xoslib:/opt/xos/core/xoslib
  - ../../core/static:/opt/xos/core/static
  - ../../core/dashboard:/opt/xos/core/dashboard
  - ../../core/templatetags:/opt/xos/core/templatetags
  - ../../templates/admin:/opt/xos/templates/admin
  - ../../configurations:/opt/xos/configurations
  - ../../xos:/opt/xos/xos
```
