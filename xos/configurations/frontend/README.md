# XOS UI Development

This configuration launches an XOS container on Cloudlab that runs the XOS develserver. The container is left running
in the backgorund.

The observer is not started, and there is no openstack backend connected for XOS. 

This configuration is intended for developing the XOS GUI. 

## Getting Started

- Navigate to '/xos/configurations/frontend' folder
- Run `make` command

You'll be able to visit XOS at `0.0.0.0:9000` and the `xos/core/xoslib` folder is shared with the container. This means that any update to that folder is automatically reported in the container.

### Docker Helpers

Stop the container: `make stop`

Restart (without rebuilding): `make start`

Open a container shell: `make enter`

View logs: `make showlogs`

## Test

To run the FE tests, navigate to: `xos/core/xoslib`, and run 'npm test'.

This will install the required `npm` dependencies and run the test.

Tests are runned in a headless browser (_PhantomJs_) by _Karma_ and the assertions are made with _Jasmine_. This is a pretty common standard for FE testing so you should feel at home.

You can find the tests in the `spec/` folder, each source file has a corresponding `.test` file in it.

## JS Styleguide

This project is following [Google JavaScript Style Guide](https://google.github.io/styleguide/javascriptguide.xml). To contribute please install [Eslint](http://eslint.org/) in your editor and run `npm run eslint` before commit.

> _NOTE_
> Many of the already present file were not Style compliant. Linting for them has been disabled as it was to time consuming fix all of them. If **you are going to work** on that files, please **start fixing style issues**, and then **remove the `/* eslint-disable */`** comment

