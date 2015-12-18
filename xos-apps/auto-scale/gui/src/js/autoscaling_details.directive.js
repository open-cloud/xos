angular.module('autoscaling')
.directive('serviceContainer', function(lodash, Autoscaling){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/service-container.tpl.html',
    controller: function($rootScope) {

      this.loader = true;

      // set to true when a service is manually selected
      this.manualSelect = false;

      // start polling
      Autoscaling.getAutoscalingData();

      // list to polling events
      $rootScope.$on('autoscaling.update', (evt, data) => {
        
        if (data.length > 0) {
          this.loader = false;
        };
        this.printData(data);
      });

      // handle errors
      $rootScope.$on('autoscaling.error', (evt, err) => {
        this.loader = false;
        this.error = err.data.message;
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
              // TODO maintain the instance order
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
          datasetFill: false,
          animation: true,
          // animationEasing: 'easeInBack'
        }
      };

      this.chartColors = [
        '#286090',
        '#F7464A',
        '#46BFBD',
        '#FDB45C',
        '#97BBCD',
        '#4D5360',
        '#8c4f9f'
      ];

      Chart.defaults.global.colours = this.chartColors;

      /**
      * Goes trough the array and format date to be used as labels
      *
      * @param Array data
      * @returns Array a list of labels
      */

      this.getLabels = (data) => {
        // we should compare the  labels and get the last available
        return this.prependValues(
          data.reduce((list, item) => {
            let date = new Date(item.timestamp);
            list.push(`${date.getHours()}:${(date.getMinutes()<10?'0':'') + date.getMinutes()}:${date.getSeconds()}`);
            return list;
          }, [])
        , '');
      };

      /**
      * Prepend value if the array is less than 10 element
      */
      this.prependValues = (list, value) => {
        if(list.length < 10){
          list.unshift(value);
          // call itself to check again
          return this.prependValues(list, value);
        }
        return list;
      }

      /**
      * Convert an object of array,
      * in an array of arrays of values
      */
      this.getData = (data, instanceNames) => {
        return lodash.map(instanceNames, (item) => {
          return this.prependValues(lodash.reduce(data[item], (list, sample) => {
            // console.log(data[item], sample);
            list.push(sample.counter_volume);
            return list;
          }, []), null);
        });
      };

      this.getMostRecentSeries = (instances) => {
        // console.log(instances);
        const newestValues = [];
        instances = lodash.toArray(instances)
        lodash.forEach(instances, (values) => {
          newestValues.push(lodash.max(values, item => new Date(item.timestamp)));
        });

        var highestValue = 0;
        var newestInstanceIndex = lodash.findIndex(newestValues, (val) => {
          return new Date(val.timestamp) > highestValue;
        });

        return instances[newestInstanceIndex]
      }

      this.drawChart = (data) => {

        const instanceNames = Object.keys(data);

        this.chart.labels = this.getLabels(this.getMostRecentSeries(data));
        this.chart.series = instanceNames;
        this.chart.data = this.getData(data, instanceNames);
      }

      $scope.$watch(() => this.instances, (val) => {
        $timeout(()=>{this.chart.options.animation = false}, 1000);
        this.drawChart(val)
      });

    }
  };
});