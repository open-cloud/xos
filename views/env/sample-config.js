
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


// This is a default configuration for your development environment.
// You can duplicate this configuration for any of your Backend Environments.
// Different configurations are loaded setting a NODE_ENV variable that contain the config file name.
// `NODE_ENV=local npm start`

// You can retrieve token and sessionId from your browser cookies.

module.exports = {
  host: 'http://localhost:9999/', // XOS Url
  xoscsrftoken: 'ogrMpnJgOGq43OxGd8jIKIx2aY1vl1Ci', // XOS token
  xossessionid: 'l49h474keq0vsk6car6l1quz0oeyvohh' // XOS session id
};
