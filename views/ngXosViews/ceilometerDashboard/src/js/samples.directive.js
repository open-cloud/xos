/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/21/16.
 */

(function () {
  'use strict';

  angular.module('xos.ceilometerDashboard')
  .directive('ceilometerSamples', function(_, $stateParams){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/ceilometer-samples.tpl.html',
      controller: function(Ceilometer) {

        this.chartColors = [
          '#286090',
          '#F7464A',
          '#46BFBD',
          '#FDB45C',
          '#97BBCD',
          '#4D5360',
          '#8c4f9f'
        ];

        this.chart = {
          series: [],
          labels: [],
          data: []
        }

        Chart.defaults.global.colours = this.chartColors;

        this.chartType = 'line';

        if($stateParams.name && $stateParams.tenant){
          this.name = $stateParams.name;
          this.tenant = $stateParams.tenant;
          // TODO rename tenant in resource_id
        }
        else{
          throw new Error('Missing Name and Tenant Params!');
        }

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
         * Goes trough the array and return a flat array of values
         *
         * @param Array data
         * @returns Array a list of values
         */

        this.getData = (data) => {
          return data.reduce((list, item) => {
            list.push(item.volume);
            return list;
          }, []);
        }

        /**
         * Add a samples to the chart
         *
         * @param string resource_id
         */
        this.chartMeters = [];
        this.addMeterToChart = (resource_id) => {
          this.chart['labels'] = this.getLabels(_.sortBy(this.samplesList[resource_id], 'timestamp'));
          this.chart['series'].push(resource_id);
          this.chart['data'].push(this.getData(_.sortBy(this.samplesList[resource_id], 'timestamp')));
          this.chartMeters.push(this.samplesList[resource_id][0]); //use the 0 as are all samples for the same resource and I need the name
          _.remove(this.sampleLabels, {id: resource_id});
        }

        this.removeFromChart = (meter) => {
          this.chart.data.splice(this.chart.series.indexOf(meter.resource_id), 1);
          this.chart.series.splice(this.chart.series.indexOf(meter.resource_id), 1);
          this.chartMeters.splice(_.findIndex(this.chartMeters, {resource_id: meter.resource_id}), 1);
          this.sampleLabels.push({
            id: meter.resource_id,
            name: meter.resource_name || meter.resource_id
          })
        };

        /**
         * Format samples to create a list of labels and ids
         */

        this.formatSamplesLabels = (samples) => {

          return _.uniq(samples, 'resource_id')
            .reduce((labels, item) => {
              labels.push({
                id: item.resource_id,
                name: item.resource_name || item.resource_id
              });

              return labels;
            }, []);
        }


        /**
         * Load the samples and format data
         */

        this.showSamples = () => {
          this.loader = true;
          // Ceilometer.getSamples(this.name, this.tenant) //fetch one
          Ceilometer.getSamples(this.name) //fetch all
            .then(res => {

              // rename things in UI
              res.map(m => {
                m.resource_name = m.resource_name.replace('mysite_onos_vbng', 'ONOS_FABRIC');
                m.resource_name = m.resource_name.replace('mysite_onos_volt', 'ONOS_CORD');
                m.resource_name = m.resource_name.replace('mysite_vbng', 'mysite_vRouter');
                return m;
              });
              // end rename things in UI

              // setup data for visualization
              this.samplesList = _.groupBy(res, 'resource_id');
              this.sampleLabels = this.formatSamplesLabels(res);

              // add current meter to chart
              this.addMeterToChart(this.tenant);

            })
            .catch(err => {
              this.error = err.data.detail;
            })
            .finally(() => {
              this.loader = false;
            });
        };

        this.showSamples();
      }
    }
  });
})();

