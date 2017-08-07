
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


/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 10/20/16.
 */

(function () {
  'use strict';
  angular.module('xos.globalXos')
  .service('Controllers', function($resource){
    return $resource('/api/core/controllers/:id', {id: '@id'});
  })
  .service('GXOS', function($q, $resource, _, LXOS){
    this.attachXosToItem = (items, target = LXOS) => {
      return _.map(items, (lxos, i) => {
        let currentXos = target[i];
        return _.map(lxos, (item) => {
          item.xos = currentXos;
          return item;
        });
      })
    };

    this.buildQueryEndpoint = (baseUrl, target = LXOS) => {
      return () => {
        const d = $q.defer();

        // store generated $resource for each L-XOS
        let r = [];

        let p = [];
        _.forEach(target, (xos, i) => {
          let resource = $resource(`${xos.auth_url}${baseUrl}`, {id: '@id'}, {
            query: {
              isArray: true,
              headers: {
                Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
              }
            }
          });
          r.push(resource);
          p.push(r[i].query().$promise);
        });

        $q.all(p)
        .then(res => {
          res = this.attachXosToItem(res, target);
          d.resolve(_.flatten(res));
        })
        .catch(d.reject);

        return {$promise: d.promise};
      };
    };

    // TODO evaluate
    this.buildLocalResource = (baseUrl, xos) => {
      const headers = {
        Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
      };
      const resource = $resource(`${xos.auth_url}${baseUrl}`, {id: '@id'}, {
        query: {
          isArray: true,
          headers: headers
        }
      });
      return resource;
    }
  })
  .service('LocalAuth', function ($q, $http, _, LXOS) {
    const baseUrl = `api/utility/login/`;
    this.login = () => {
      const d = $q.defer();

      let p = [];
      _.forEach(LXOS, (xos, i) => {
        let loginRequest = $http.post(`${xos.auth_url}${baseUrl}`, {username: xos.admin_user, password: xos.admin_password});
        p.push(loginRequest);
      });

      $q.all(p)
      .then(auths => {
        _.forEach(auths, (auth, i) => {
          LXOS[i].xoscsrftoken = auth.data.xoscsrftoken;
          LXOS[i].xossessionid = auth.data.xossessionid;
          LXOS[i].user = JSON.parse(auth.data.user);
        });
        d.resolve();
      })
      .catch(e => {
        d.reject(e);
      });

      return d.promise;
    };

    this.getUserByName = (xos, username) => {
      const d = $q.defer();
      console.log(username);
      $http.get(`${xos.auth_url}api/core/users/`, {
        params: {
          username: username
        },
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
      .then((res) => {
        d.resolve(res.data[0]);
      })
      .catch(e => {
        d.reject(e);
      });

      return d.promise;
    }
  })
  .service('LocalSlices', function($q, $http, GXOS){
    const baseUrl = `api/utility/slicesplus/`;

    // TODO build a global resource
    this.queryFromAll = (targets) => {
      return GXOS.buildQueryEndpoint(baseUrl, targets)();
    };

    this.getLocalByName = (xos, sliceName) => {
      const d = $q.defer();

      $http.get(`${xos.auth_url}${baseUrl}`, {
        // params: params,
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
      .then((res) => {
        const slice = _.filter(res.data, (s) => {
          return s.name.indexOf(sliceName) > -1;
        });
        d.resolve(slice[0]);
      })
      .catch(e => {
        d.reject(e);
      });

      return d.promise;
    };
  })
  .service('LocalUsers', function(GXOS){
    const baseUrl = `api/core/users/`;

    // TODO build a global resource
    this.queryFromAll = GXOS.buildQueryEndpoint(baseUrl);
  })
  .service('LocalInstances', function($q, $http, GXOS, LocalDeployments, LocalImages, LocalFlavor, LocalNode){
    const baseUrl = `api/core/instances/`;

    // NOTE Evaluate to dinamically create a resource targeted to a L-XOS

    this.queryFromAll = (targets) => {
      return GXOS.buildQueryEndpoint(baseUrl, targets)();
    };
    this.createOnLocal = (instance) => {
      const d = $q.defer();
      const xos = instance.xos;
      delete instance.xos;
      $http.post(`${xos.auth_url}${baseUrl}`, instance, {
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
      .then((inst) => {
        d.resolve(inst);
      })
      .catch(e => {
        d.reject(e);
      });

      return d.promise;
    };

    this.getFromLocal = (xos, params) => {
      const d = $q.defer();
      $http.get(`${xos.auth_url}${baseUrl}`, {
        params: params,
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
        .then((inst) => {
          d.resolve(inst.data);
        })
        .catch(e => {
          d.reject(e);
        });

      return d.promise;
    };

    this.deleteFromLocal = (instance) => {
      console.log('deleteFromLocal');
      const d = $q.defer();
      $http.delete(`${instance.xos.auth_url}${baseUrl}${instance.id}/`, {
        headers: {
          Authorization: `Basic ${btoa(instance.xos.admin_user + ':' + instance.xos.admin_password)}`
        }
      })
        .then((inst) => {
          d.resolve(inst.data);
        })
        .catch(e => {
          d.reject(e);
        });

      return d.promise;
    };

    this.getLocalInfo = (xos) => {
      const d = $q.defer();
      $q.all([
        LocalDeployments.queryFromLocal(xos),
        LocalImages.queryFromLocal(xos),
        LocalFlavor.queryFromLocal(xos),
        LocalNode.queryFromLocal(xos)
      ])
        .then((res) => {
          res = _.map(res, collection => {
            return _.map(collection, item => {
              return {id: item.id, label: item.name}
            });
          });
          d.resolve(res);
        })
        .catch(d.reject);
      return d.promise;
    };

  })
  .service('LocalDeployments', function($q, $http){

    const baseUrl = `api/core/deployments/`;

    this.queryFromLocal = (xos) => {
      const d = $q.defer();

      $http.get(`${xos.auth_url}${baseUrl}`, {
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
      .then((res) => {
        d.resolve(res.data);
      })
      .catch(e => {
        d.reject(e);
      });

      return d.promise;
    }
  })
  .service('LocalImages', function($q, $http){

    const baseUrl = `api/core/images/`;

    this.queryFromLocal = (xos) => {
      const d = $q.defer();

      $http.get(`${xos.auth_url}${baseUrl}`, {
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
      .then((res) => {
        d.resolve(res.data);
      })
      .catch(e => {
        d.reject(e);
      });

      return d.promise;
    }
  })
  .service('LocalFlavor', function($q, $http){

    const baseUrl = `api/core/flavors/`;

    this.queryFromLocal = (xos) => {
      const d = $q.defer();

      $http.get(`${xos.auth_url}${baseUrl}`, {
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
        .then((res) => {
          d.resolve(res.data);
        })
        .catch(e => {
          d.reject(e);
        });

      return d.promise;
    }
  })
  .service('LocalNode', function($q, $http){

    const baseUrl = `api/core/nodes/`;

    this.queryFromLocal = (xos) => {
      const d = $q.defer();

      $http.get(`${xos.auth_url}${baseUrl}`, {
        headers: {
          Authorization: `Basic ${btoa(xos.admin_user + ':' + xos.admin_password)}`
        }
      })
        .then((res) => {
          d.resolve(res.data);
        })
        .catch(e => {
          d.reject(e);
        });

      return d.promise;
    }
  });
})();

