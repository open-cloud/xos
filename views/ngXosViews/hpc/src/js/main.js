'use strict';

angular.module('xos.hpc', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('hpc-list', {
    url: '/',
    template: '<hpcs-list></hpcs-list>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.service('Hpc', function($q, $http){
  this.query = (params) => {
    const d = $q.defer();

    $http.get('/xoslib/hpcview', {params: params})
      .then((res) => {
        d.resolve(res.data);
      })
      .catch(d.reject);

    return {$promise: d.promise};
  };
})
.directive('hpcsList', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/hpc-list.tpl.html',
    controller: function(Hpc){

      const secondsToHms = d => {
        d = Number(d);
        var h = Math.floor(d / 3600);
        var m = Math.floor(d % 3600 / 60);
        var s = Math.floor(d % 3600 % 60);
        return ((h > 0 ? h + 'h ' + (m < 10 ? '0' :'') :'') + m + 'm ' + (s < 10 ? '0' :'') + s + 's');
      };

      const toDuration = (property) => {
        return (item) => {
          if(!angular.isNumber(item[property])){
            return item[property]
          }
          return secondsToHms(item[property]);
        }
      };

      this.routerConfig = {
        filter: 'field',
        order: true,
        columns: [
          {
            label: 'Name',
            prop: 'name'
          },
          {
            label: 'Ip Address',
            prop: 'ip'
          },
          {
            label: 'Record Checker',
            prop: 'watcher.DNS.msg'
          },
          {
            label: 'Name Servers',
            prop: 'nameservers',
            type: 'array'
          },
          {
            label: 'Dns Demux Config Age',
            prop: 'dnsdemux_config_age',
            type: 'custom',
            formatter: toDuration('dnsdemux_config_age')
          },
          {
            label: 'Dns Redir Config Age',
            prop: 'dnsredir_config_age',
            type: 'custom',
            formatter: toDuration('dnsredir_config_age')
          }
        ]
      };

      this.cacheConfig = {
        filter: 'field',
        order: true,
        columns: [
          {
            label: 'Name',
            prop: 'name'
          },
          {
            label: 'Prober',
            prop: 'watcher.HPC-hb.msg'
          },
          {
            label: 'Fetcher',
            prop: 'watcher.HPC-fetch.msg'
          },
          {
            label: 'Config Age',
            prop: 'config_age',
            type: 'custom',
            formatter: toDuration('config_age')
          }
        ]
      };


      this.fetch = () => {
        Hpc.query().$promise
        .then((hpcs) => {
          this.routers = hpcs[0].dnsdemux;
          this.caches = hpcs[0].hpc;
        })
        .catch((e) => {
          throw new Error(e);
        });
      };

      this.fetch();
    }
  };
});