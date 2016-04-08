# API Test Configuration

This configuration is intended to be used to test the API,
to use it:

- `make containers` //rebuild the container with current code
- `make xos` //start the container with fixtures data
- `make prepare` //install test dependencies

Then anytime is needed `make test` (`xos/api` folder is shared with the container)