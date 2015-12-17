angular.module('autoscaling')
.directive('serviceContainer', function(lodash, Autoscaling){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/service-container.tpl.html',
    controller: function($rootScope) {
      Autoscaling.getAutoscalingData();
      $rootScope.$on('autoscaling.update', (evt, data) => {
        this.printData(data);
      });

      /**
      * Group resources by service and slice
      */
     
      this.printData = (data) => {
        this.services = lodash.groupBy(data, 'service');
        lodash.forEach(Object.keys(this.services), (service) => {
          this.services[service] = lodash.groupBy(this.services[service], 'slice');
          lodash.forEach(Object.keys(this.services[service]), (slice) => {
            // grouping instance by name
            this.services[service][slice] = lodash.groupBy(this.services[service][slice], 'instance_name');
            // instance can't have the same name,
            // so take them out of an array
            // and keep only the sample data
            lodash.forEach(Object.keys(this.services[service][slice]), (instance) => {
              // console.log(this.services[service][slice][instance]);
              this.services[service][slice][instance] = this.services[service][slice][instance][0].queue;
            });
            
          })
        });
        console.log(this.services);
      };
    }
  };
});
