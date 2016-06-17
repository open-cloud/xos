# XOS UI End to End Test

This tests are implemented using `selenium`.

To execute them, you should install it with `pip install selenium` and you should have `phantomjs` available as a command. You can install it with `npm install phantomjs -g`.

# Execute the test
If you want to execute the tests locally, simply navigate to this folder and execute: `python xos-e2e-test.py`

You can optionally use Firefox as target browser with `python xos-e2e-test.py firefox`

You can eventually add also a target url with `python xos-e2e-test.py firefox 'http://xos.dev:9999'`

# Execute the test from inside the docker container
- `cd xos/configurations/test-standalone`
- `make containers`
- `make`
- `make test-ui`