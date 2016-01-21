/*jshint -W069 */
/*global angular:false */
angular.module('xos.hpcapi', [])
    .factory('hpcapi', ['$q', '$http', '$rootScope', function($q, $http, $rootScope) {
        'use strict';

        /**
         * 
         * @class hpcapi
         * @param {(string|object)} [domainOrOptions] - The project domain or options object. If object, see the object's optional properties.
         * @param {string} [domainOrOptions.domain] - The project domain
         * @param {string} [domainOrOptions.cache] - An angularjs cache implementation
         * @param {object} [domainOrOptions.token] - auth token - object with value property and optional headerOrQueryName and isQuery properties
         * @param {string} [cache] - An angularjs cache implementation
         */
        var hpcapi = (function() {
            function hpcapi(options, cache) {
                var domain = (typeof options === 'object') ? options.domain : options;
                this.domain = typeof(domain) === 'string' ? domain : 'http://localhost:9999';
                cache = cache || ((typeof options === 'object') ? options.cache : cache);
                this.cache = cache;
            }

            hpcapi.prototype.$on = function($scope, path, handler) {
                var url = domain + path;
                $scope.$on(url, function() {
                    handler();
                });
                return this;
            };

            hpcapi.prototype.$broadcast = function(path) {
                var url = domain + path;
                //cache.remove(url);
                $rootScope.$broadcast(url);
                return this;
            };

            hpcapi.transformRequest = function(obj) {
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
             * @name hpcapi#Hpc_Api_Root_GET
             * 
             */
            hpcapi.prototype.Hpc_Api_Root_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Health_Check_List_GET
             * 
             */
            hpcapi.prototype.Hpc_Health_Check_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpchealthchecks/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Health_Check_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} hpcService - 
             * @param {choice} kind - 
             * @param {string} resource_name - 
             * @param {string} result_contains - 
             * @param {integer} result_min_size - 
             * @param {integer} result_max_size - 
             * 
             */
            hpcapi.prototype.Hpc_Health_Check_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpchealthchecks/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['kind'] !== undefined) {
                    form['kind'] = parameters['kind'];
                }

                if (parameters['kind'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: kind'));
                    return deferred.promise;
                }

                if (parameters['resource_name'] !== undefined) {
                    form['resource_name'] = parameters['resource_name'];
                }

                if (parameters['resource_name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: resource_name'));
                    return deferred.promise;
                }

                if (parameters['result_contains'] !== undefined) {
                    form['result_contains'] = parameters['result_contains'];
                }

                if (parameters['result_min_size'] !== undefined) {
                    form['result_min_size'] = parameters['result_min_size'];
                }

                if (parameters['result_max_size'] !== undefined) {
                    form['result_max_size'] = parameters['result_max_size'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Health_Check_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Hpc_Health_Check_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpchealthchecks/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Health_Check_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} hpcService - 
             * @param {choice} kind - 
             * @param {string} resource_name - 
             * @param {string} result_contains - 
             * @param {integer} result_min_size - 
             * @param {integer} result_max_size - 
             * 
             */
            hpcapi.prototype.Hpc_Health_Check_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpchealthchecks/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['kind'] !== undefined) {
                    form['kind'] = parameters['kind'];
                }

                if (parameters['kind'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: kind'));
                    return deferred.promise;
                }

                if (parameters['resource_name'] !== undefined) {
                    form['resource_name'] = parameters['resource_name'];
                }

                if (parameters['resource_name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: resource_name'));
                    return deferred.promise;
                }

                if (parameters['result_contains'] !== undefined) {
                    form['result_contains'] = parameters['result_contains'];
                }

                if (parameters['result_min_size'] !== undefined) {
                    form['result_min_size'] = parameters['result_min_size'];
                }

                if (parameters['result_max_size'] !== undefined) {
                    form['result_max_size'] = parameters['result_max_size'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Health_Check_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} hpcService - 
             * @param {choice} kind - 
             * @param {string} resource_name - 
             * @param {string} result_contains - 
             * @param {integer} result_min_size - 
             * @param {integer} result_max_size - 
             * 
             */
            hpcapi.prototype.Hpc_Health_Check_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpchealthchecks/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['kind'] !== undefined) {
                    form['kind'] = parameters['kind'];
                }

                if (parameters['resource_name'] !== undefined) {
                    form['resource_name'] = parameters['resource_name'];
                }

                if (parameters['result_contains'] !== undefined) {
                    form['result_contains'] = parameters['result_contains'];
                }

                if (parameters['result_min_size'] !== undefined) {
                    form['result_min_size'] = parameters['result_min_size'];
                }

                if (parameters['result_max_size'] !== undefined) {
                    form['result_max_size'] = parameters['result_max_size'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Health_Check_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Hpc_Health_Check_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpchealthchecks/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Service_List_GET
             * 
             */
            hpcapi.prototype.Hpc_Service_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpcservices/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Service_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} description - Description of Service
             * @param {boolean} enabled - 
             * @param {string} kind - Kind of service
             * @param {string} name - Service Name
             * @param {string} versionNumber - Version of Service Definition
             * @param {boolean} published - 
             * @param {string} view_url - 
             * @param {string} icon_url - 
             * @param {string} public_key - Public key string
             * @param {string} service_specific_id - 
             * @param {string} service_specific_attribute - 
             * @param {string} cmi_hostname - 
             * @param {boolean} hpc_port80 - Enable port 80 for HPC
             * @param {string} watcher_hpc_network - Network for hpc_watcher to contact hpc instance
             * @param {string} watcher_dnsdemux_network - Network for hpc_watcher to contact dnsdemux instance
             * @param {string} watcher_dnsredir_network - Network for hpc_watcher to contact dnsredir instance
             * 
             */
            hpcapi.prototype.Hpc_Service_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpcservices/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['kind'] !== undefined) {
                    form['kind'] = parameters['kind'];
                }

                if (parameters['kind'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: kind'));
                    return deferred.promise;
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['versionNumber'] !== undefined) {
                    form['versionNumber'] = parameters['versionNumber'];
                }

                if (parameters['versionNumber'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: versionNumber'));
                    return deferred.promise;
                }

                if (parameters['published'] !== undefined) {
                    form['published'] = parameters['published'];
                }

                if (parameters['view_url'] !== undefined) {
                    form['view_url'] = parameters['view_url'];
                }

                if (parameters['icon_url'] !== undefined) {
                    form['icon_url'] = parameters['icon_url'];
                }

                if (parameters['public_key'] !== undefined) {
                    form['public_key'] = parameters['public_key'];
                }

                if (parameters['service_specific_id'] !== undefined) {
                    form['service_specific_id'] = parameters['service_specific_id'];
                }

                if (parameters['service_specific_attribute'] !== undefined) {
                    form['service_specific_attribute'] = parameters['service_specific_attribute'];
                }

                if (parameters['cmi_hostname'] !== undefined) {
                    form['cmi_hostname'] = parameters['cmi_hostname'];
                }

                if (parameters['hpc_port80'] !== undefined) {
                    form['hpc_port80'] = parameters['hpc_port80'];
                }

                if (parameters['watcher_hpc_network'] !== undefined) {
                    form['watcher_hpc_network'] = parameters['watcher_hpc_network'];
                }

                if (parameters['watcher_dnsdemux_network'] !== undefined) {
                    form['watcher_dnsdemux_network'] = parameters['watcher_dnsdemux_network'];
                }

                if (parameters['watcher_dnsredir_network'] !== undefined) {
                    form['watcher_dnsredir_network'] = parameters['watcher_dnsredir_network'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Service_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Hpc_Service_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpcservices/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Service_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} description - Description of Service
             * @param {boolean} enabled - 
             * @param {string} kind - Kind of service
             * @param {string} name - Service Name
             * @param {string} versionNumber - Version of Service Definition
             * @param {boolean} published - 
             * @param {string} view_url - 
             * @param {string} icon_url - 
             * @param {string} public_key - Public key string
             * @param {string} service_specific_id - 
             * @param {string} service_specific_attribute - 
             * @param {string} cmi_hostname - 
             * @param {boolean} hpc_port80 - Enable port 80 for HPC
             * @param {string} watcher_hpc_network - Network for hpc_watcher to contact hpc instance
             * @param {string} watcher_dnsdemux_network - Network for hpc_watcher to contact dnsdemux instance
             * @param {string} watcher_dnsredir_network - Network for hpc_watcher to contact dnsredir instance
             * 
             */
            hpcapi.prototype.Hpc_Service_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpcservices/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['kind'] !== undefined) {
                    form['kind'] = parameters['kind'];
                }

                if (parameters['kind'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: kind'));
                    return deferred.promise;
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['versionNumber'] !== undefined) {
                    form['versionNumber'] = parameters['versionNumber'];
                }

                if (parameters['versionNumber'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: versionNumber'));
                    return deferred.promise;
                }

                if (parameters['published'] !== undefined) {
                    form['published'] = parameters['published'];
                }

                if (parameters['view_url'] !== undefined) {
                    form['view_url'] = parameters['view_url'];
                }

                if (parameters['icon_url'] !== undefined) {
                    form['icon_url'] = parameters['icon_url'];
                }

                if (parameters['public_key'] !== undefined) {
                    form['public_key'] = parameters['public_key'];
                }

                if (parameters['service_specific_id'] !== undefined) {
                    form['service_specific_id'] = parameters['service_specific_id'];
                }

                if (parameters['service_specific_attribute'] !== undefined) {
                    form['service_specific_attribute'] = parameters['service_specific_attribute'];
                }

                if (parameters['cmi_hostname'] !== undefined) {
                    form['cmi_hostname'] = parameters['cmi_hostname'];
                }

                if (parameters['hpc_port80'] !== undefined) {
                    form['hpc_port80'] = parameters['hpc_port80'];
                }

                if (parameters['watcher_hpc_network'] !== undefined) {
                    form['watcher_hpc_network'] = parameters['watcher_hpc_network'];
                }

                if (parameters['watcher_dnsdemux_network'] !== undefined) {
                    form['watcher_dnsdemux_network'] = parameters['watcher_dnsdemux_network'];
                }

                if (parameters['watcher_dnsredir_network'] !== undefined) {
                    form['watcher_dnsredir_network'] = parameters['watcher_dnsredir_network'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Service_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} description - Description of Service
             * @param {boolean} enabled - 
             * @param {string} kind - Kind of service
             * @param {string} name - Service Name
             * @param {string} versionNumber - Version of Service Definition
             * @param {boolean} published - 
             * @param {string} view_url - 
             * @param {string} icon_url - 
             * @param {string} public_key - Public key string
             * @param {string} service_specific_id - 
             * @param {string} service_specific_attribute - 
             * @param {string} cmi_hostname - 
             * @param {boolean} hpc_port80 - Enable port 80 for HPC
             * @param {string} watcher_hpc_network - Network for hpc_watcher to contact hpc instance
             * @param {string} watcher_dnsdemux_network - Network for hpc_watcher to contact dnsdemux instance
             * @param {string} watcher_dnsredir_network - Network for hpc_watcher to contact dnsredir instance
             * 
             */
            hpcapi.prototype.Hpc_Service_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpcservices/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['kind'] !== undefined) {
                    form['kind'] = parameters['kind'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['versionNumber'] !== undefined) {
                    form['versionNumber'] = parameters['versionNumber'];
                }

                if (parameters['published'] !== undefined) {
                    form['published'] = parameters['published'];
                }

                if (parameters['view_url'] !== undefined) {
                    form['view_url'] = parameters['view_url'];
                }

                if (parameters['icon_url'] !== undefined) {
                    form['icon_url'] = parameters['icon_url'];
                }

                if (parameters['public_key'] !== undefined) {
                    form['public_key'] = parameters['public_key'];
                }

                if (parameters['service_specific_id'] !== undefined) {
                    form['service_specific_id'] = parameters['service_specific_id'];
                }

                if (parameters['service_specific_attribute'] !== undefined) {
                    form['service_specific_attribute'] = parameters['service_specific_attribute'];
                }

                if (parameters['cmi_hostname'] !== undefined) {
                    form['cmi_hostname'] = parameters['cmi_hostname'];
                }

                if (parameters['hpc_port80'] !== undefined) {
                    form['hpc_port80'] = parameters['hpc_port80'];
                }

                if (parameters['watcher_hpc_network'] !== undefined) {
                    form['watcher_hpc_network'] = parameters['watcher_hpc_network'];
                }

                if (parameters['watcher_dnsdemux_network'] !== undefined) {
                    form['watcher_dnsdemux_network'] = parameters['watcher_dnsdemux_network'];
                }

                if (parameters['watcher_dnsredir_network'] !== undefined) {
                    form['watcher_dnsredir_network'] = parameters['watcher_dnsredir_network'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Hpc_Service_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Hpc_Service_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/hpcservices/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Origin_Server_List_GET
             * 
             */
            hpcapi.prototype.Origin_Server_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/originservers/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Origin_Server_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} origin_server_id - 
             * @param {string} url - 
             * @param {string} contentProvider - 
             * @param {boolean} authenticated - Status for this Site
             * @param {boolean} enabled - Status for this Site
             * @param {choice} protocol - 
             * @param {boolean} redirects - Indicates whether Origin Server redirects should be used for this Origin Server
             * @param {string} description - 
             * 
             */
            hpcapi.prototype.Origin_Server_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/originservers/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['origin_server_id'] !== undefined) {
                    form['origin_server_id'] = parameters['origin_server_id'];
                }

                if (parameters['url'] !== undefined) {
                    form['url'] = parameters['url'];
                }

                if (parameters['url'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url'));
                    return deferred.promise;
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['contentProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: contentProvider'));
                    return deferred.promise;
                }

                if (parameters['authenticated'] !== undefined) {
                    form['authenticated'] = parameters['authenticated'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['protocol'] !== undefined) {
                    form['protocol'] = parameters['protocol'];
                }

                if (parameters['protocol'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: protocol'));
                    return deferred.promise;
                }

                if (parameters['redirects'] !== undefined) {
                    form['redirects'] = parameters['redirects'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Origin_Server_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Origin_Server_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/originservers/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Origin_Server_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} origin_server_id - 
             * @param {string} url - 
             * @param {string} contentProvider - 
             * @param {boolean} authenticated - Status for this Site
             * @param {boolean} enabled - Status for this Site
             * @param {choice} protocol - 
             * @param {boolean} redirects - Indicates whether Origin Server redirects should be used for this Origin Server
             * @param {string} description - 
             * 
             */
            hpcapi.prototype.Origin_Server_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/originservers/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['origin_server_id'] !== undefined) {
                    form['origin_server_id'] = parameters['origin_server_id'];
                }

                if (parameters['url'] !== undefined) {
                    form['url'] = parameters['url'];
                }

                if (parameters['url'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: url'));
                    return deferred.promise;
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['contentProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: contentProvider'));
                    return deferred.promise;
                }

                if (parameters['authenticated'] !== undefined) {
                    form['authenticated'] = parameters['authenticated'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['protocol'] !== undefined) {
                    form['protocol'] = parameters['protocol'];
                }

                if (parameters['protocol'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: protocol'));
                    return deferred.promise;
                }

                if (parameters['redirects'] !== undefined) {
                    form['redirects'] = parameters['redirects'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Origin_Server_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} origin_server_id - 
             * @param {string} url - 
             * @param {string} contentProvider - 
             * @param {boolean} authenticated - Status for this Site
             * @param {boolean} enabled - Status for this Site
             * @param {choice} protocol - 
             * @param {boolean} redirects - Indicates whether Origin Server redirects should be used for this Origin Server
             * @param {string} description - 
             * 
             */
            hpcapi.prototype.Origin_Server_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/originservers/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['origin_server_id'] !== undefined) {
                    form['origin_server_id'] = parameters['origin_server_id'];
                }

                if (parameters['url'] !== undefined) {
                    form['url'] = parameters['url'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['authenticated'] !== undefined) {
                    form['authenticated'] = parameters['authenticated'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['protocol'] !== undefined) {
                    form['protocol'] = parameters['protocol'];
                }

                if (parameters['redirects'] !== undefined) {
                    form['redirects'] = parameters['redirects'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Origin_Server_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Origin_Server_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/originservers/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Cdn_Prefix_List_GET
             * 
             */
            hpcapi.prototype.Cdn_Prefix_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/cdnprefixs/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Cdn_Prefix_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} cdn_prefix_id - 
             * @param {string} prefix - Registered Prefix for Domain
             * @param {string} contentProvider - 
             * @param {string} description - Description of Content Provider
             * @param {string} defaultOriginServer - 
             * @param {boolean} enabled - 
             * 
             */
            hpcapi.prototype.Cdn_Prefix_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/cdnprefixs/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['cdn_prefix_id'] !== undefined) {
                    form['cdn_prefix_id'] = parameters['cdn_prefix_id'];
                }

                if (parameters['prefix'] !== undefined) {
                    form['prefix'] = parameters['prefix'];
                }

                if (parameters['prefix'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: prefix'));
                    return deferred.promise;
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['contentProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: contentProvider'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['defaultOriginServer'] !== undefined) {
                    form['defaultOriginServer'] = parameters['defaultOriginServer'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Cdn_Prefix_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Cdn_Prefix_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/cdnprefixs/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Cdn_Prefix_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} cdn_prefix_id - 
             * @param {string} prefix - Registered Prefix for Domain
             * @param {string} contentProvider - 
             * @param {string} description - Description of Content Provider
             * @param {string} defaultOriginServer - 
             * @param {boolean} enabled - 
             * 
             */
            hpcapi.prototype.Cdn_Prefix_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/cdnprefixs/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['cdn_prefix_id'] !== undefined) {
                    form['cdn_prefix_id'] = parameters['cdn_prefix_id'];
                }

                if (parameters['prefix'] !== undefined) {
                    form['prefix'] = parameters['prefix'];
                }

                if (parameters['prefix'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: prefix'));
                    return deferred.promise;
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['contentProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: contentProvider'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['defaultOriginServer'] !== undefined) {
                    form['defaultOriginServer'] = parameters['defaultOriginServer'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Cdn_Prefix_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} cdn_prefix_id - 
             * @param {string} prefix - Registered Prefix for Domain
             * @param {string} contentProvider - 
             * @param {string} description - Description of Content Provider
             * @param {string} defaultOriginServer - 
             * @param {boolean} enabled - 
             * 
             */
            hpcapi.prototype.Cdn_Prefix_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/cdnprefixs/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['cdn_prefix_id'] !== undefined) {
                    form['cdn_prefix_id'] = parameters['cdn_prefix_id'];
                }

                if (parameters['prefix'] !== undefined) {
                    form['prefix'] = parameters['prefix'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['defaultOriginServer'] !== undefined) {
                    form['defaultOriginServer'] = parameters['defaultOriginServer'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Cdn_Prefix_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Cdn_Prefix_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/cdnprefixs/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Service_Provider_List_GET
             * 
             */
            hpcapi.prototype.Service_Provider_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/serviceproviders/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Service_Provider_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} hpcService - 
             * @param {integer} service_provider_id - 
             * @param {string} name - Service Provider Name
             * @param {string} description - Description of Service Provider
             * @param {boolean} enabled - 
             * 
             */
            hpcapi.prototype.Service_Provider_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/serviceproviders/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['hpcService'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: hpcService'));
                    return deferred.promise;
                }

                if (parameters['service_provider_id'] !== undefined) {
                    form['service_provider_id'] = parameters['service_provider_id'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Service_Provider_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Service_Provider_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/serviceproviders/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Service_Provider_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} hpcService - 
             * @param {integer} service_provider_id - 
             * @param {string} name - Service Provider Name
             * @param {string} description - Description of Service Provider
             * @param {boolean} enabled - 
             * 
             */
            hpcapi.prototype.Service_Provider_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/serviceproviders/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['hpcService'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: hpcService'));
                    return deferred.promise;
                }

                if (parameters['service_provider_id'] !== undefined) {
                    form['service_provider_id'] = parameters['service_provider_id'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Service_Provider_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} hpcService - 
             * @param {integer} service_provider_id - 
             * @param {string} name - Service Provider Name
             * @param {string} description - Description of Service Provider
             * @param {boolean} enabled - 
             * 
             */
            hpcapi.prototype.Service_Provider_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/serviceproviders/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['service_provider_id'] !== undefined) {
                    form['service_provider_id'] = parameters['service_provider_id'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Service_Provider_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Service_Provider_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/serviceproviders/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Content_Provider_List_GET
             * 
             */
            hpcapi.prototype.Content_Provider_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/contentproviders/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Content_Provider_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} content_provider_id - 
             * @param {string} name - 
             * @param {boolean} enabled - 
             * @param {string} description - Description of Content Provider
             * @param {string} serviceProvider - 
             * 
             */
            hpcapi.prototype.Content_Provider_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/contentproviders/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['content_provider_id'] !== undefined) {
                    form['content_provider_id'] = parameters['content_provider_id'];
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

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['serviceProvider'] !== undefined) {
                    form['serviceProvider'] = parameters['serviceProvider'];
                }

                if (parameters['serviceProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: serviceProvider'));
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Content_Provider_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Content_Provider_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/contentproviders/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Content_Provider_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} content_provider_id - 
             * @param {string} name - 
             * @param {boolean} enabled - 
             * @param {string} description - Description of Content Provider
             * @param {string} serviceProvider - 
             * 
             */
            hpcapi.prototype.Content_Provider_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/contentproviders/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['content_provider_id'] !== undefined) {
                    form['content_provider_id'] = parameters['content_provider_id'];
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

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['serviceProvider'] !== undefined) {
                    form['serviceProvider'] = parameters['serviceProvider'];
                }

                if (parameters['serviceProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: serviceProvider'));
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Content_Provider_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {integer} content_provider_id - 
             * @param {string} name - 
             * @param {boolean} enabled - 
             * @param {string} description - Description of Content Provider
             * @param {string} serviceProvider - 
             * 
             */
            hpcapi.prototype.Content_Provider_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/contentproviders/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['content_provider_id'] !== undefined) {
                    form['content_provider_id'] = parameters['content_provider_id'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['enabled'] !== undefined) {
                    form['enabled'] = parameters['enabled'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['serviceProvider'] !== undefined) {
                    form['serviceProvider'] = parameters['serviceProvider'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Content_Provider_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Content_Provider_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/contentproviders/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Access_Map_List_GET
             * 
             */
            hpcapi.prototype.Access_Map_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/accessmaps/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Access_Map_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} contentProvider - 
             * @param {string} name - Name of the Access Map
             * @param {string} description - 
             * @param {string} map - specifies which client requests are allowed
             * 
             */
            hpcapi.prototype.Access_Map_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/accessmaps/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['contentProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: contentProvider'));
                    return deferred.promise;
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['map'] !== undefined) {
                    form['map'] = parameters['map'];
                }

                if (parameters['map'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: map'));
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Access_Map_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Access_Map_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/accessmaps/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Access_Map_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} contentProvider - 
             * @param {string} name - Name of the Access Map
             * @param {string} description - 
             * @param {string} map - specifies which client requests are allowed
             * 
             */
            hpcapi.prototype.Access_Map_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/accessmaps/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['contentProvider'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: contentProvider'));
                    return deferred.promise;
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['map'] !== undefined) {
                    form['map'] = parameters['map'];
                }

                if (parameters['map'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: map'));
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Access_Map_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} contentProvider - 
             * @param {string} name - Name of the Access Map
             * @param {string} description - 
             * @param {string} map - specifies which client requests are allowed
             * 
             */
            hpcapi.prototype.Access_Map_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/accessmaps/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['map'] !== undefined) {
                    form['map'] = parameters['map'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Access_Map_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Access_Map_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/accessmaps/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Site_Map_List_GET
             * 
             */
            hpcapi.prototype.Site_Map_List_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/sitemaps/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Site_Map_List_POST
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} contentProvider - 
             * @param {string} serviceProvider - 
             * @param {string} cdnPrefix - 
             * @param {string} hpcService - 
             * @param {string} name - Name of the Site Map
             * @param {string} description - 
             * @param {string} map - specifies how to map requests to hpc instances
             * @param {integer} map_id - 
             * 
             */
            hpcapi.prototype.Site_Map_List_POST = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/sitemaps/';

                var body;
                var queryParameters = {};
                var headers = {};
                var form = {};

                if (parameters['enacted'] !== undefined) {
                    form['enacted'] = parameters['enacted'];
                }

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['serviceProvider'] !== undefined) {
                    form['serviceProvider'] = parameters['serviceProvider'];
                }

                if (parameters['cdnPrefix'] !== undefined) {
                    form['cdnPrefix'] = parameters['cdnPrefix'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['map'] !== undefined) {
                    form['map'] = parameters['map'];
                }

                if (parameters['map'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: map'));
                    return deferred.promise;
                }

                if (parameters['map_id'] !== undefined) {
                    form['map_id'] = parameters['map_id'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Site_Map_Detail_GET
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Site_Map_Detail_GET = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/sitemaps/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Site_Map_Detail_PUT
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} contentProvider - 
             * @param {string} serviceProvider - 
             * @param {string} cdnPrefix - 
             * @param {string} hpcService - 
             * @param {string} name - Name of the Site Map
             * @param {string} description - 
             * @param {string} map - specifies how to map requests to hpc instances
             * @param {integer} map_id - 
             * 
             */
            hpcapi.prototype.Site_Map_Detail_PUT = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/sitemaps/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['backend_status'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: backend_status'));
                    return deferred.promise;
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['serviceProvider'] !== undefined) {
                    form['serviceProvider'] = parameters['serviceProvider'];
                }

                if (parameters['cdnPrefix'] !== undefined) {
                    form['cdnPrefix'] = parameters['cdnPrefix'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['name'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: name'));
                    return deferred.promise;
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['map'] !== undefined) {
                    form['map'] = parameters['map'];
                }

                if (parameters['map'] === undefined) {
                    deferred.reject(new Error('Missing required form parameter: map'));
                    return deferred.promise;
                }

                if (parameters['map_id'] !== undefined) {
                    form['map_id'] = parameters['map_id'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Site_Map_Detail_PATCH
             * @param {string} pk - 
             * @param {string} enacted - 
             * @param {string} policed - 
             * @param {string} backend_register - 
             * @param {string} backend_status - 
             * @param {boolean} deleted - 
             * @param {boolean} write_protect - 
             * @param {boolean} lazy_blocked - 
             * @param {boolean} no_sync - 
             * @param {string} contentProvider - 
             * @param {string} serviceProvider - 
             * @param {string} cdnPrefix - 
             * @param {string} hpcService - 
             * @param {string} name - Name of the Site Map
             * @param {string} description - 
             * @param {string} map - specifies how to map requests to hpc instances
             * @param {integer} map_id - 
             * 
             */
            hpcapi.prototype.Site_Map_Detail_PATCH = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/sitemaps/{pk}/';

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

                if (parameters['policed'] !== undefined) {
                    form['policed'] = parameters['policed'];
                }

                if (parameters['backend_register'] !== undefined) {
                    form['backend_register'] = parameters['backend_register'];
                }

                if (parameters['backend_status'] !== undefined) {
                    form['backend_status'] = parameters['backend_status'];
                }

                if (parameters['deleted'] !== undefined) {
                    form['deleted'] = parameters['deleted'];
                }

                if (parameters['write_protect'] !== undefined) {
                    form['write_protect'] = parameters['write_protect'];
                }

                if (parameters['lazy_blocked'] !== undefined) {
                    form['lazy_blocked'] = parameters['lazy_blocked'];
                }

                if (parameters['no_sync'] !== undefined) {
                    form['no_sync'] = parameters['no_sync'];
                }

                if (parameters['contentProvider'] !== undefined) {
                    form['contentProvider'] = parameters['contentProvider'];
                }

                if (parameters['serviceProvider'] !== undefined) {
                    form['serviceProvider'] = parameters['serviceProvider'];
                }

                if (parameters['cdnPrefix'] !== undefined) {
                    form['cdnPrefix'] = parameters['cdnPrefix'];
                }

                if (parameters['hpcService'] !== undefined) {
                    form['hpcService'] = parameters['hpcService'];
                }

                if (parameters['name'] !== undefined) {
                    form['name'] = parameters['name'];
                }

                if (parameters['description'] !== undefined) {
                    form['description'] = parameters['description'];
                }

                if (parameters['map'] !== undefined) {
                    form['map'] = parameters['map'];
                }

                if (parameters['map_id'] !== undefined) {
                    form['map_id'] = parameters['map_id'];
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
                    options.transformRequest = hpcapi.transformRequest;
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
             * @name hpcapi#Site_Map_Detail_DELETE
             * @param {string} pk - 
             * 
             */
            hpcapi.prototype.Site_Map_Detail_DELETE = function(parameters) {
                if (parameters === undefined) {
                    parameters = {};
                }
                var deferred = $q.defer();

                var domain = this.domain;
                var path = '/hpcapi/sitemaps/{pk}/';

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
                    options.transformRequest = hpcapi.transformRequest;
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

            return hpcapi;
        })();

        return hpcapi;
    }]);