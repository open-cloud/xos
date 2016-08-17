# M-CORD UI

## Requirements

To run this UI is required to have installd:
- NodeJs > v4
- Bower

## Mock Server

A server that mock the response, used for development, is available and can be started with `npm run server`

## Application setup

This development environment require to be executed from inside the `xos` repo. The correct location for this folder is `/views/ngXosViews`. 
An `environment` configuration should also be present under `/views/env` and should contain a `default.js` file (to connect to XOS) and a `local.js` file (to connect to the mock server).

The content of the `local.js` should be (to work with the provided server):
```
module.exports = {
  host: 'http://localhost:4000/'
};
```

While the `default.js` file should look like (please updated your values, refer to https://www.youtube.com/watch?v=iEp9F7JYPO8 for more information):
```
module.exports = {
  host: 'http://127.0.0.1:9999/', // XOS Url
  xoscsrftoken: 'jJRuH4YNK69qYV4Jks3dPCNrYDKFMtyL', // XOS token
  xossessionid: 'jbsvkfjlcqtroxhxgz53oyvnd3348a03' // XOS session id
};
```

## Start the application

### To use the mock server

From the root of this application (`/views/ngXosViews/ecordTopology`):
- execute: `NODE_ENV=local npm start`
- In another shell `npm run server`

### To connect to your running XOS instance

From the root of this application (`/views/ngXosViews/ecordTopology`) execute `npm start` (make sure that token and sessionId in the `default.js` config file are correct).

## Build the App

Once everything is working you can execute `npm run build` that will copy the files in the correct location and then you can load the dashboard in the UI (refer again to the tutorial).
