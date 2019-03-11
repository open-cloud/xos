# XOS

XOS is a framework for operationalizing a collection of disaggregated services.
It is packaged as a project in the Open CORD initiative, with source code
managed through <https://gerrit.opencord.org>. It is also mirrored at
<https://github.com/opencord>.

You can download and use XOS either as part of CORD (see the
[CORD Guide](https://guide.opencord.org/) for details)
or as a standalone component (see the
[XOS Guide](https://guide.xosproject.org/) for details).

Also visit the
[XOS Wiki Page](https://wiki.opencord.org/display/CORD/XOS+and+the+CORD+Controller)
for additional information.

## Testing the XOS Core

Run `make test` to run all tests on the XOS codebase. This is what happens
during the `verify_xos_unit-test` job in Jenkins.

Running these tests requires:

- A Python 2.7, and one or more of Python 3.5, 3.6, or 3.7 development environment
  - Requires a C build system and the python header files (under ubuntu 16.04, `apt
    install python2-dev python3-dev build-essential`) to build packages with C
    extensions.
- [virtualenv](https://virtualenv.pypa.io)
- [tox](https://tox.readthedocs.io) version 3.2 or later

This will run 3 sets of test targets, which can also be run individually:

- `lib-test`: runs `tox` on each of the library modules stored in `lib`.
  These are tested against both Python 2 and 3 by running both `nose2` and
  `flake8`.

  If you are making changes only to a specific library, it is recommended that
  you run `tox` directly inside that modules directory, which should run much
  more quickly than testing all the libraries.

- `xos-test`: runs `nose2` to test the `xos` directory. This code is not yet
  Python 3 or flake8 clean.

- `migration-test`: Runs the `xos-migrate` tool on the XOS core modules. This
  verifies that the Django migrations have been properly created.  If you've
  changed `xosgenx` or the `core.xproto` file you may need to generate new
  migrations. See `docs/dev/xosmigrate.md` for more information.

Additionally, a virtualenv will be created in `venv-xos` - you can `source
./venv-xos/bin/activate` if you'd like to run tools like `xos-migrate` manually.

### Issues you may encounter when developing XOS

*Testing errors that complain about missing compliers or header files:
`src/twisted/test/raiser.c:4:20: fatal error: Python.h: No such file or
directory`*

You probably need to install a C build system and the Python development headers.

*After making changes to the requirements.txt or other files, the changes don't
seem to be register*

You might need to clean up any files left behind by previous development work.
`make clean` in the root Makefile should clean up most files. Additionally,
`git clean -ixd` will let you interactively remove all ignored files and
directories from your source tree.
