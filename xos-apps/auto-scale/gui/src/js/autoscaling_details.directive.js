angular.module('autoscaling')
.directive('serviceContainer', function(lodash, Autoscaling){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/service-container.tpl.html',
    controller: function($rootScope) {

      // set to true when a service is manually selected
      this.manualSelect = false;

      // start polling
      Autoscaling.getAutoscalingData();

      // list to polling events
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
        // arbitrary set the first service in the list as the selected one
        if(!this.manualSelect){
          this.serviceName = Object.keys(this.services)[0];
          this.selectedService = this.services[Object.keys(this.services)[0]];
        }
        else{
          this.selectedService = this.services[this.serviceName]
        }
      };

      /**
      * Change the current selected service
      */
     
      this.selectService = (serviceName) => {
        this.serviceName = serviceName;
        this.selectedService = this.services[serviceName];
        this.manualSelect = true;
      };
    }
  };
})
.directive('serviceDetail', function(lodash){
  return {
    restrict: 'E',
    scope: {
      service: '=service'
    },
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/service-detail.tpl.html',
    controller: function($scope) {

    }
  };
})
.directive('sliceDetail', function(lodash){
  return {
    restrict: 'E',
    scope: {
      instances: '=instances'
    },
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/slice-detail.tpl.html',
    controller: function($scope, $timeout) {

      this.chart = {
        options: {
          animation: true
        }
      };

      /**
      * Goes trough the array and format date to be used as labels
      *
      * @param Array data
      * @returns Array a list of labels
      */

      this.getLabels = (data) => {
        return data.reduce((list, item) => {
          let date = new Date(item.timestamp);
          list.push(`${date.getHours()}:${(date.getMinutes()<10?'0':'') + date.getMinutes()}:${date.getSeconds()}`);
          return list;
        }, []);
      };

      /**
      * Convert an object of array,
      * in an array of arrays of values
      */
      this.getData = (data, instanceNames) => {
        return lodash.map(instanceNames, (item) => {
          return lodash.reduce(data[item], (list, sample) => {
            // console.log(data[item], sample);
            list.push(sample.counter_volume);
            return list;
          }, []);
        });
      };

      this.drawChart = (data) => {

        const instanceNames = Object.keys(data);

        this.chart.labels = this.getLabels(data[instanceNames[0]]);
        this.chart.series = instanceNames;
        this.chart.data = this.getData(data, instanceNames);

        // console.log(this.getData(data, instanceNames));
      }

      $scope.$watch(() => this.instances, (val) => {
        $timeout(()=>{this.chart.options.animation = false}, 1000);
        this.drawChart(val)
      });

    }
  };
});

//  TODO
//  [x] repeat service name in a menu
//  [x] create a directive that receive a service
//  [ ] print a chart for every slice
//  [ ] print a line in the chart for every instance