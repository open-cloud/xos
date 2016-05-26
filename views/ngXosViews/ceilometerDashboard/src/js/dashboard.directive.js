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
    .directive('ceilometerDashboard', function(_){
      return {
        restrict: 'E',
        scope: {},
        bindToController: true,
        controllerAs: 'vm',
        templateUrl: 'templates/ceilometer-dashboard.tpl.html',
        controller: function(Ceilometer){

          this.showStats = false;

          // this open the accordion
          this.accordion = {
            open: {}
          };

          /**
           * Open the active panel base on the service stored values
           */
          this.openPanels = () => {
            if(Ceilometer.selectedService){
              this.accordion.open[Ceilometer.selectedService] = true;
              if(Ceilometer.selectedSlice){
                this.loadSliceMeter(Ceilometer.selectedSlice, Ceilometer.selectedService);
                this.selectedSlice = Ceilometer.selectedSlice;
                if(Ceilometer.selectedResource){
                  this.selectedResource = Ceilometer.selectedResource;
                }
              }
            }
          };

          /**
           * Load the list of service and slices
           */
          this.loadMappings = () => {
            this.loader = true;
            Ceilometer.getMappings()
              .then((services) => {

                // rename thing in UI
                services.map((service) => {
                  if(service.service === 'service_ONOS_vBNG'){
                    service.service = 'ONOS_FABRIC';
                  }
                  if(service.service === 'service_ONOS_vOLT'){
                    service.service = 'ONOS_CORD';
                  }

                  service.slices.map(s => {
                    if(s.slice === 'mysite_onos_volt'){
                      s.slice = 'ONOS_CORD';
                    }
                    if(s.slice === 'mysite_onos_vbng'){
                      s.slice = 'ONOS_FABRIC';
                    }
                    if(s.slice === 'mysite_vbng'){
                      s.slice = 'mysite_vRouter';
                    }
                  });

                  return service;
                });
                // end rename thing in UI

                this.services = services;
                this.openPanels();
              })
              .catch(err => {
                this.error = (err.data && err.data.detail) ? err.data.detail : 'An Error occurred. Please try again later.';
              })
              .finally(() => {
                this.loader = false;
              });
          };

          this.loadMappings();

          /**
           * Load the list of a single slice
           */
          this.loadSliceMeter = (slice, service_name) => {

            Ceilometer.selectedSlice = null;
            Ceilometer.selectedService = null;
            Ceilometer.selectedResources = null;

            // visualization info
            this.loader = true;
            this.error = null;
            this.ceilometerError = null;

            Ceilometer.getMeters({tenant: slice.project_id})
              .then((sliceMeters) => {
                this.selectedSlice = slice.slice;
                this.selectedTenant = slice.project_id;

                // store the status
                Ceilometer.selectedSlice = slice;
                Ceilometer.selectedService = service_name;

                // rename things in UI
                sliceMeters.map(m => {
                  m.resource_name = m.resource_name.replace('mysite_onos_vbng', 'ONOS_FABRIC');
                  m.resource_name = m.resource_name.replace('mysite_onos_volt', 'ONOS_CORD');
                  m.resource_name = m.resource_name.replace('mysite_vbng', 'mysite_vRouter');
                  return m;
                });
                // end rename things in UI

                this.selectedResources = _.groupBy(sliceMeters, 'resource_name');

                // hacky
                if(Ceilometer.selectedResource){
                  this.selectedMeters = this.selectedResources[Ceilometer.selectedResource];
                }
              })
              .catch(err => {

                // this means that ceilometer is not yet ready
                if(err.status === 503){
                  return this.ceilometerError = err.data.detail.specific_error;
                }

                this.ceilometerError = (err.data && err.data.detail && err.data.detail.specific_error) ? err.data.detail.specific_error : 'An Error occurred. Please try again later.';
              })
              .finally(() => {
                this.loader = false;
              });
          };

          /**
           * Select Meters for a resource
           *
           * @param Array meters The list of selected resources
           * @returns void
           */
          this.selectedMeters = null;
          this.selectMeters = (meters, resource) => {
            this.selectedMeters = meters;

            Ceilometer.selectedResource = resource;
            this.selectedResource = resource;
          }

        }
      };
    })
})();

