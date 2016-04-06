# xos-api-docs

To execute the test:

- run `npm install`
- run `pip install dredd_hooks`
- open `dredd.yml` and change `endpoint: 'http://xos.dev:9999'` to your experiment url
- open `hooks.py` and change `restoreSubscriber` to ssh into your experiment

# TODO

Define helper to setup the DB in a consistent shape for tests.

