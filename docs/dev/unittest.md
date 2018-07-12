# Unit Testing

XOS supports automated unit tests using the `nose2` unit testing framework.

## Setting up a unit testing environment

To run unit tests, an environment needs to be setup with the appropriate python
libraries used by the unit testing framework and also the XOS libraries that
are being tested. There is a development/test convenience script,
`setup_venv.sh`, that sets up a python virtualenv and installs all the required
packages to run local CLI tools.

Assuming you've checked out the whole source repository with `repo` into `~/cord`:

```bash
cd ~/cord/orchestration/xos
./scripts/setup_venv.sh
source venv-xos/bin/activate
```

At this point all the XOS libraries are installed as python modules, so you can use any
cli tool such as `xosgenx` or `xossh`, as well as the unit testing tools.

## Running unit tests

To run unit tests, go to the root of the `xos` repository and run the following
to run the tests and print a coverage report:

```shell
nose2 --verbose --with-coverage --coverage-report term
```

You can also run unit tests in a service repository by going into the `xos`
subdirectory and running the same command.

## Writing new unit tests

New test filename should start with the string `test`. For example,
`test_mymodule.py`. If named properly, then `nose2` will automatically pick
them up.

## Ignoring unwanted unit tests

Some tests are still being migrated to the unit testing framework and/or
require features that may not be present in the virtual-env. Placing the
[__test__
attribute](https://nose2.readthedocs.io/en/latest/plugins/dundertests.html) set to `False`:

```python
__test__ = False
```

in a class will exclude it from being evaluated by the test framework.
