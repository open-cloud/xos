/*jshint -W069 */
/*global angular:false */
angular.module('xos.xoslib', [])
    .factory('xoslib', ['$q', '$http', '$rootScope', function($q, $http, $rootScope) {
        'use strict';

        /**
         * 
         * @class xoslib
         * @param {(string|object)} [domainOrOptions] - The project domain or options object. If object, see the object's optional properties.
         * @param {string} [domainOrOptions.domain] - The project domain
         * @param {string} [domainOrOptions.cache] - An angularjs cache implementation
         * @param {object} [domainOrOptions.token] - auth token - object with value property and optional headerOrQueryName and isQuery properties
         * @param {string} [cache] - An angularjs cache implementation
         */
        var xoslib = (function() {
            function xoslib(options, cache) {
                var domain = (typeof options === 'object') ? options.domain : options;
                this.domain = typeof(domain) === 'string' ? domain : 'http://localhost:9999';
                cache = cache || ((typeof options === 'object') ? options.cache : cache);
                this.cache = cache;
            }

            xoslib.prototype.$on = function($scope, path, handler) {
                var url = domain + path;
                $scope.$on(url, function() {
                    handler();
                });
                return this;
            };

            xoslib.prototype.$broadcast = function(path) {
                var url = domain + path;
                //cache.remove(url);
                $rootScope.$broadcast(url);
                return this;
            };

            xoslib.transformRequest = function(obj) {
                var str = [];
                for (var p in obj) {
                    var val = obj[p];
                    if (angular.isArray(val)) {
                        val.forEach(function(val) {
                            str.push(encodeURIComponent(p) + "=" + encodeURIComponent(val));
                        });
                    } else {
                        str.push(encodeURIComponent(p) + "=" + encodeURIComponent(val));
                    }
                }
                return str.join("&");
            };

            /**
             * 
             * @method
             * @name xoslib#Monitoring_Channel_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Monitoring_Channel_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/monitoringchannel/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Monitoring_Channel_Detail_PUT
             * @param {string} pk - 
             * @param {string} provider_service - 
             * 
             */
            xoslib.prototype.Monitoring_Channel_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/monitoringchannel/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['provider_service'] !== undefined) {
                    form['provider_service'] = parameters['provider_service'];
                }

                if (parameters['provider_service'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: provider_service'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Monitoring_Channel_Detail_PATCH
             * @param {string} pk - 
             * @param {string} provider_service - 
             * 
             */
            xoslib.prototype.Monitoring_Channel_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/monitoringchannel/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['provider_service'] !== undefined) {
                    form['provider_service'] = parameters['provider_service'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PATCH',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Monitoring_Channel_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Monitoring_Channel_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/monitoringchannel/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Monitoring_Channel_List_GET
             * 
             */
            xoslib.prototype.Monitoring_Channel_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/monitoringchannel/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Monitoring_Channel_List_POST
             * @param {string} provider_service - 
             * 
             */
            xoslib.prototype.Monitoring_Channel_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/monitoringchannel/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['provider_service'] !== undefined) {
                    form['provider_service'] = parameters['provider_service'];
                }

                if (parameters['provider_service'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: provider_service'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Hpc_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Hpc_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/hpcview/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Hpc_List_GET
             * 
             */
            xoslib.prototype.Hpc_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/hpcview/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Tenant_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Tenant_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/tenantview/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Tenant_List_GET
             * 
             */
            xoslib.prototype.Tenant_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/tenantview/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Port_Forwarding_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Port_Forwarding_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/portforwarding/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Port_Forwarding_List_GET
             * 
             */
            xoslib.prototype.Port_Forwarding_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/portforwarding/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Ssh_Key_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Ssh_Key_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/sshkeys/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Ssh_Key_List_GET
             * 
             */
            xoslib.prototype.Ssh_Key_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/sshkeys/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Debug_get_vbng_dump
             * 
             */
            xoslib.prototype.Cord_Debug_get_vbng_dump = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/cord_debug/vbng_dump/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/cordsubscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_Detail_PUT
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/cordsubscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_Detail_PATCH
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/cordsubscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PATCH',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/cordsubscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_List_GET
             * 
             */
            xoslib.prototype.Cord_Subscriber_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/cordsubscriber/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_List_POST
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/cordsubscriber/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_list
             * 
             */
            xoslib.prototype.Cord_Subscriber_list = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_update
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_update = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_partial_update
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_partial_update = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PATCH',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_update
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_update = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_destroy
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_destroy = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_retrieve
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_retrieve = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_vcpe_synced
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_vcpe_synced = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/vcpe_synced/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_url_filter
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_url_filter = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/url_filter/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_set_url_filter
             * @param {string} pk - 
             * @param {string} level - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_set_url_filter = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/url_filter/{level}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{level}', parameters['level']);

                if (parameters['level'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: level'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_services
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_services = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/services/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_service
             * @param {string} pk - 
             * @param {string} service - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_service = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/services/{service}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{service}', parameters['service']);

                if (parameters['service'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: service'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_enable_service
             * @param {string} pk - 
             * @param {string} service - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_enable_service = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/services/{service}/true/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{service}', parameters['service']);

                if (parameters['service'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: service'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_disable_service
             * @param {string} pk - 
             * @param {string} service - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_disable_service = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/services/{service}/false/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{service}', parameters['service']);

                if (parameters['service'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: service'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_create_user
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_create_user = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_users
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_users = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_clear_users
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_clear_users = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/clearusers/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_clear_users
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_clear_users = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/clearusers/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_clear_users
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_clear_users = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/clearusers/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_create_user
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_create_user = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/newuser/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_create_user
             * @param {string} pk - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_create_user = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/newuser/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_delete_user
             * @param {string} pk - 
             * @param {string} uid - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_delete_user = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/{uid}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{uid}', parameters['uid']);

                if (parameters['uid'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: uid'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_user_level
             * @param {string} pk - 
             * @param {string} uid - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_user_level = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/{uid}/url_filter/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{uid}', parameters['uid']);

                if (parameters['uid'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: uid'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_set_user_level
             * @param {string} pk - 
             * @param {string} uid - 
             * @param {string} level - 
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_set_user_level = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/users/{uid}/url_filter/{level}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                path = path.replace('{uid}', parameters['uid']);

                if (parameters['uid'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: uid'));
                    return deferred.promise;
                }

                path = path.replace('{level}', parameters['level']);

                if (parameters['level'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: level'));
                    return deferred.promise;
                }

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_bbsdump
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_bbsdump = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subscriber/{pk}/bbsdump/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_initdemo
             * @param {boolean} firewall_enable - 
             * @param {string} firewall_rules - 
             * @param {boolean} url_filter_enable - 
             * @param {string} url_filter_rules - 
             * @param {string} url_filter_level - 
             * @param {boolean} vcpe_synced - 
             * @param {boolean} cdn_enable - 
             * @param {string} routeable_subnet - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_initdemo = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/initdemo/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['firewall_enable'] !== undefined) {
                    form['firewall_enable'] = parameters['firewall_enable'];
                }

                if (parameters['firewall_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_enable'));
                    return deferred.promise;
                }

                if (parameters['firewall_rules'] !== undefined) {
                    form['firewall_rules'] = parameters['firewall_rules'];
                }

                if (parameters['firewall_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: firewall_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_enable'] !== undefined) {
                    form['url_filter_enable'] = parameters['url_filter_enable'];
                }

                if (parameters['url_filter_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_enable'));
                    return deferred.promise;
                }

                if (parameters['url_filter_rules'] !== undefined) {
                    form['url_filter_rules'] = parameters['url_filter_rules'];
                }

                if (parameters['url_filter_rules'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url_filter_rules'));
                    return deferred.promise;
                }

                if (parameters['url_filter_level'] !== undefined) {
                    form['url_filter_level'] = parameters['url_filter_level'];
                }

                if (parameters['vcpe_synced'] !== undefined) {
                    form['vcpe_synced'] = parameters['vcpe_synced'];
                }

                if (parameters['vcpe_synced'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vcpe_synced'));
                    return deferred.promise;
                }

                if (parameters['cdn_enable'] !== undefined) {
                    form['cdn_enable'] = parameters['cdn_enable'];
                }

                if (parameters['cdn_enable'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: cdn_enable'));
                    return deferred.promise;
                }

                if (parameters['routeable_subnet'] !== undefined) {
                    form['routeable_subnet'] = parameters['routeable_subnet'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_initdemo
             * 
             */
            xoslib.prototype.Cord_Subscriber_initdemo = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/initdemo/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_ssiddetail
             * @param {string} ssid - 
             * 
             */
            xoslib.prototype.Cord_Subscriber_ssiddetail = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subidlookup/{ssid}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{ssid}', parameters['ssid']);

                if (parameters['ssid'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: ssid'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_ssidlist
             * 
             */
            xoslib.prototype.Cord_Subscriber_ssidlist = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/subidlookup/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_Subscriber_get_vbng_mapping
             * 
             */
            xoslib.prototype.Cord_Subscriber_get_vbng_mapping = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/rs/vbng_mapping/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_User_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_User_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/corduser/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_User_Detail_PUT
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_User_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/corduser/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_User_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Cord_User_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/corduser/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_User_List_GET
             * 
             */
            xoslib.prototype.Cord_User_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/corduser/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Cord_User_List_POST
             * 
             */
            xoslib.prototype.Cord_User_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/corduser/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Volt_Tenant_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Volt_Tenant_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/volttenant/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Volt_Tenant_Detail_PUT
             * @param {string} pk - 
             * @param {string} provider_service - 
             * @param {string} service_specific_id - 
             * @param {string} vlan_id - 
             * 
             */
            xoslib.prototype.Volt_Tenant_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/volttenant/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['provider_service'] !== undefined) {
                    form['provider_service'] = parameters['provider_service'];
                }

                if (parameters['provider_service'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: provider_service'));
                    return deferred.promise;
                }

                if (parameters['service_specific_id'] !== undefined) {
                    form['service_specific_id'] = parameters['service_specific_id'];
                }

                if (parameters['service_specific_id'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: service_specific_id'));
                    return deferred.promise;
                }

                if (parameters['vlan_id'] !== undefined) {
                    form['vlan_id'] = parameters['vlan_id'];
                }

                if (parameters['vlan_id'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vlan_id'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Volt_Tenant_Detail_PATCH
             * @param {string} pk - 
             * @param {string} provider_service - 
             * @param {string} service_specific_id - 
             * @param {string} vlan_id - 
             * 
             */
            xoslib.prototype.Volt_Tenant_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/volttenant/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['provider_service'] !== undefined) {
                    form['provider_service'] = parameters['provider_service'];
                }

                if (parameters['service_specific_id'] !== undefined) {
                    form['service_specific_id'] = parameters['service_specific_id'];
                }

                if (parameters['vlan_id'] !== undefined) {
                    form['vlan_id'] = parameters['vlan_id'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PATCH',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Volt_Tenant_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Volt_Tenant_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/volttenant/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Volt_Tenant_List_GET
             * 
             */
            xoslib.prototype.Volt_Tenant_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/volttenant/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Volt_Tenant_List_POST
             * @param {string} provider_service - 
             * @param {string} service_specific_id - 
             * @param {string} vlan_id - 
             * 
             */
            xoslib.prototype.Volt_Tenant_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/volttenant/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['provider_service'] !== undefined) {
                    form['provider_service'] = parameters['provider_service'];
                }

                if (parameters['provider_service'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: provider_service'));
                    return deferred.promise;
                }

                if (parameters['service_specific_id'] !== undefined) {
                    form['service_specific_id'] = parameters['service_specific_id'];
                }

                if (parameters['service_specific_id'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: service_specific_id'));
                    return deferred.promise;
                }

                if (parameters['vlan_id'] !== undefined) {
                    form['vlan_id'] = parameters['vlan_id'];
                }

                if (parameters['vlan_id'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: vlan_id'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Slice_Plus_Detail_GET
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Slice_Plus_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/slicesplus/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Slice_Plus_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} name - The Name of the Slice
             * @param {boolean} enabled - Status for this Slice
             * @param {boolean} omf_friendly - 
             * @param {string} description - High level description of the slice and expected activities
             * @param {string} slice_url - 
             * @param {string} site - The Site this Slice belongs to
             * @param {integer} max_instances - 
             * @param {string} service - 
             * @param {string} network - 
             * @param {string} mount_data_sets - 
             * @param {string} default_image - 
             * @param {string} default_flavor - 
             * @param {string} serviceClass - 
             * @param {string} creator - 
             * @param {string} network_ports - 
             * @param {string} site_allocation - 
             * @param {string} site_ready - 
             * @param {string} users - 
             * @param {string} user_names - 
             * 
             */
            xoslib.prototype.Slice_Plus_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/slicesplus/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['omf_friendly'] !== undefined) {
                    form['omf_friendly'] = parameters['omf_friendly'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['slice_url'] !== undefined) {
                    form['slice_url'] = parameters['slice_url'];
                }

                if (parameters['site'] !== undefined) {
                    form['site'] = parameters['site'];
                }

                if (parameters['site'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: site'));
                    return deferred.promise;
                }

                if (parameters['max_instances'] !== undefined) {
                    form['max_instances'] = parameters['max_instances'];
                }

                if (parameters['max_instances'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: max_instances'));
                    return deferred.promise;
                }

                if (parameters['service'] !== undefined) {
                    form['service'] = parameters['service'];
                }

                if (parameters['network'] !== undefined) {
                    form['network'] = parameters['network'];
                }

                if (parameters['mount_data_sets'] !== undefined) {
                    form['mount_data_sets'] = parameters['mount_data_sets'];
                }

                if (parameters['default_image'] !== undefined) {
                    form['default_image'] = parameters['default_image'];
                }

                if (parameters['default_flavor'] !== undefined) {
                    form['default_flavor'] = parameters['default_flavor'];
                }

                if (parameters['serviceClass'] !== undefined) {
                    form['serviceClass'] = parameters['serviceClass'];
                }

                if (parameters['creator'] !== undefined) {
                    form['creator'] = parameters['creator'];
                }

                if (parameters['network_ports'] !== undefined) {
                    form['network_ports'] = parameters['network_ports'];
                }

                if (parameters['site_allocation'] !== undefined) {
                    form['site_allocation'] = parameters['site_allocation'];
                }

                if (parameters['site_ready'] !== undefined) {
                    form['site_ready'] = parameters['site_ready'];
                }

                if (parameters['users'] !== undefined) {
                    form['users'] = parameters['users'];
                }

                if (parameters['user_names'] !== undefined) {
                    form['user_names'] = parameters['user_names'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PUT',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Slice_Plus_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} name - The Name of the Slice
             * @param {boolean} enabled - Status for this Slice
             * @param {boolean} omf_friendly - 
             * @param {string} description - High level description of the slice and expected activities
             * @param {string} slice_url - 
             * @param {string} site - The Site this Slice belongs to
             * @param {integer} max_instances - 
             * @param {string} service - 
             * @param {string} network - 
             * @param {string} mount_data_sets - 
             * @param {string} default_image - 
             * @param {string} default_flavor - 
             * @param {string} serviceClass - 
             * @param {string} creator - 
             * @param {string} network_ports - 
             * @param {string} site_allocation - 
             * @param {string} site_ready - 
             * @param {string} users - 
             * @param {string} user_names - 
             * 
             */
            xoslib.prototype.Slice_Plus_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/slicesplus/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['omf_friendly'] !== undefined) {
                    form['omf_friendly'] = parameters['omf_friendly'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['slice_url'] !== undefined) {
                    form['slice_url'] = parameters['slice_url'];
                }

                if (parameters['site'] !== undefined) {
                    form['site'] = parameters['site'];
                }

                if (parameters['max_instances'] !== undefined) {
                    form['max_instances'] = parameters['max_instances'];
                }

                if (parameters['service'] !== undefined) {
                    form['service'] = parameters['service'];
                }

                if (parameters['network'] !== undefined) {
                    form['network'] = parameters['network'];
                }

                if (parameters['mount_data_sets'] !== undefined) {
                    form['mount_data_sets'] = parameters['mount_data_sets'];
                }

                if (parameters['default_image'] !== undefined) {
                    form['default_image'] = parameters['default_image'];
                }

                if (parameters['default_flavor'] !== undefined) {
                    form['default_flavor'] = parameters['default_flavor'];
                }

                if (parameters['serviceClass'] !== undefined) {
                    form['serviceClass'] = parameters['serviceClass'];
                }

                if (parameters['creator'] !== undefined) {
                    form['creator'] = parameters['creator'];
                }

                if (parameters['network_ports'] !== undefined) {
                    form['network_ports'] = parameters['network_ports'];
                }

                if (parameters['site_allocation'] !== undefined) {
                    form['site_allocation'] = parameters['site_allocation'];
                }

                if (parameters['site_ready'] !== undefined) {
                    form['site_ready'] = parameters['site_ready'];
                }

                if (parameters['users'] !== undefined) {
                    form['users'] = parameters['users'];
                }

                if (parameters['user_names'] !== undefined) {
                    form['user_names'] = parameters['user_names'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'PATCH',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Slice_Plus_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            xoslib.prototype.Slice_Plus_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/slicesplus/{pk}/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                path = path.replace('{pk}', parameters['pk']);

                if (parameters['pk'] === undefined) {
                    deferred.reject(new Error('Missing required path parameter: pk'));
                    return deferred.promise;
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'DELETE',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Slice_Plus_List_GET
             * 
             */
            xoslib.prototype.Slice_Plus_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/slicesplus/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var cached = parameters.$cache && parameters.$cache.get(url);
                if (cached !== undefined && parameters.$refresh !== true) {
                    deferred.resolve(cached);
                    return deferred.promise;
                }
                var options = {
                    timeout: parameters.$timeout,
                    method: 'GET',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };
            /**
             * 
             * @method
             * @name xoslib#Slice_Plus_List_POST
             * @param {string} enacted - 
             * @param {string} name - The Name of the Slice
             * @param {boolean} enabled - Status for this Slice
             * @param {boolean} omf_friendly - 
             * @param {string} description - High level description of the slice and expected activities
             * @param {string} slice_url - 
             * @param {string} site - The Site this Slice belongs to
             * @param {integer} max_instances - 
             * @param {string} service - 
             * @param {string} network - 
             * @param {string} mount_data_sets - 
             * @param {string} default_image - 
             * @param {string} default_flavor - 
             * @param {string} serviceClass - 
             * @param {string} creator - 
             * @param {string} network_ports - 
             * @param {string} site_allocation - 
             * @param {string} site_ready - 
             * @param {string} users - 
             * @param {string} user_names - 
             * 
             */
            xoslib.prototype.Slice_Plus_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/xoslib/slicesplus/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['omf_friendly'] !== undefined) {
                    form['omf_friendly'] = parameters['omf_friendly'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['slice_url'] !== undefined) {
                    form['slice_url'] = parameters['slice_url'];
                }

                if (parameters['site'] !== undefined) {
                    form['site'] = parameters['site'];
                }

                if (parameters['site'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: site'));
                    return deferred.promise;
                }

                if (parameters['max_instances'] !== undefined) {
                    form['max_instances'] = parameters['max_instances'];
                }

                if (parameters['max_instances'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: max_instances'));
                    return deferred.promise;
                }

                if (parameters['service'] !== undefined) {
                    form['service'] = parameters['service'];
                }

                if (parameters['network'] !== undefined) {
                    form['network'] = parameters['network'];
                }

                if (parameters['mount_data_sets'] !== undefined) {
                    form['mount_data_sets'] = parameters['mount_data_sets'];
                }

                if (parameters['default_image'] !== undefined) {
                    form['default_image'] = parameters['default_image'];
                }

                if (parameters['default_flavor'] !== undefined) {
                    form['default_flavor'] = parameters['default_flavor'];
                }

                if (parameters['serviceClass'] !== undefined) {
                    form['serviceClass'] = parameters['serviceClass'];
                }

                if (parameters['creator'] !== undefined) {
                    form['creator'] = parameters['creator'];
                }

                if (parameters['network_ports'] !== undefined) {
                    form['network_ports'] = parameters['network_ports'];
                }

                if (parameters['site_allocation'] !== undefined) {
                    form['site_allocation'] = parameters['site_allocation'];
                }

                if (parameters['site_ready'] !== undefined) {
                    form['site_ready'] = parameters['site_ready'];
                }

                if (parameters['users'] !== undefined) {
                    form['users'] = parameters['users'];
                }

                if (parameters['user_names'] !== undefined) {
                    form['user_names'] = parameters['user_names'];
                }

                if (parameters.$queryParameters) {
                    Object.keys(parameters.$queryParameters)
                        .forEach(function(parameterName) {
                            var parameter = parameters.$queryParameters[parameterName];
                            queryParameters[parameterName] = parameter;
                        });
                }

                var url = domain + path;
                var options = {
                    timeout: parameters.$timeout,
                    method: 'POST',
                    url: url,
                    params: queryParameters,
                    data: body,
                    headers: headers
                };
                if (Object.keys(form).length > 0) {
                    options.data = form;
                    options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    options.transformRequest = xoslib.transformRequest;
                }
                $http(options)
                    .success(function(data, status, headers, config) {
                        deferred.resolve(data);
                        if (parameters.$cache !== undefined) {
                            parameters.$cache.put(url, data, parameters.$cacheItemOpts ? parameters.$cacheItemOpts : {});
                        }
                    })
                    .error(function(data, status, headers, config) {
                        deferred.reject({
                            status: status,
                            headers: headers,
                            config: config,
                            body: data
                        });
                    });

                return deferred.promise;
            };

            return xoslib;
        })();

        return xoslib;
    }]);