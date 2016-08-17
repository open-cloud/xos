/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/27/16.
 */

(function () {
  'use strict';
  angular.module('xos.ecordTopology')
  .directive('elineForm', function(){
    return {
      restrict: 'E',
      scope: {
        uni: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/eline-form.tpl.html',
      controller: function ($scope, $timeout, $location, _, Uni, Eline) {
        // FORM HELPERS
        const isUniSelected = (uni, list) => {
          return _.findIndex(list, {id: uni.id, selected: true}) === -1 ? false : true;
        };

        const deselectOtherUni = (uni, list) => {
          list.map(u => {
            if(u.id !== uni.id){
              u.selected = false;
              u.alreadySelected = false;
            }
            return u;
          })
        };

        this.selectUni = (uni, position) => {
          if(uni.selected){

            deselectOtherUni(uni, this[`${position}Unis`]);

            // need to check if is selected in the other list
            const list = position === 'start' ? 'end':'start';

            if(isUniSelected(uni, this[`${list}Unis`])){
              return uni.alreadySelected = true;
            }
            this.formErrors[`${position}Error`] = null;
            return this.el[position] = uni;
          }

          this.el[position] = null;
          return uni.alreadySelected = false;
        };
        // END FORM HELPERS

        this.el = {};

        Uni.query().$promise
        .then((unis) => {
          // TODO we were mapping UNIS to name, location. Bring that back to life!
          this.startUnis = angular.copy(unis);
          this.endUnis = angular.copy(unis);
          this.infrastructureUnis = angular.copy(unis);
        });

        const createEline = (el) => {

          // NOTE:
          // name and latlng have been added to request, will XOS manage them?

          let formatted = {
              adminstate : 'activationrequested',
              operstate : 'active',
              uni1 : {'id' : el.start.id},
              uni2 : {'id' : el.end.id},
              sid: el.evcCfgidentifier,
              type : 'Point_To_Point',
          };

          return formatted;
        }


        this.formErrors = {};
        this.createEline = (el, form) => {

          if(!el.start){
            this.formErrors.startError = 'Select a starting point'
          }

          if(!el.end){
            this.formErrors.endError = 'Select an ending point'
          }

          if(!el.start || !el.end){
            return;
          }

          let eline = createEline(el);

          Eline.save(eline).$promise
          .then((res) => {
            form.$saved = true;
            $scope.$emit('elan.created', res);
            //cordConfig.pages.push(res);

            $timeout(() => {
              $location.path('/');
            }, 1000);
          })
          .catch(e => {
            throw new Error(e);
          });
        };

        $scope.$watch(() => this.el, (val, oldval) => {
          if(val !== oldval && this.eline.$saved){
            this.eline.$saved = false;
          }
        }, true);

        this.prepareInfrastructure = (el_prefix, unis) => {

          let i = 0;

          const builElines = (elements) => {

            let elines = [];

            let firstEl =  elements.shift();

            let newElines = elements.reduce((list, end) => {
              let el = {};
              // prepare e-line as the form
              el.evcCfgidentifier = `${el_prefix}-${++i}`;
              el.start = firstEl;
              el.end = end;
              list.push(createEline(el))
              return list;
            }, []);

            elines = elines.concat(...newElines);

            if(elements.length === 1){

              return elines;
            }
            else {
              return elines.concat(...builElines(elements));
            }

          }

          return builElines(unis);
        }

        this.createInfrastructure = (unis) => {

          unis = _.filter(unis, {selected: true});
          $log.info('Send request to MARC!!! - Decide the format!', unis);

          let promises = [];

          this.prepareInfrastructure('test', unis).forEach((eline) => {
            promises.push(Eline().save(eline).$promise)
          });

          $q.all(promises)
          .then((res) => {
            res.forEach(eline => {
              $scope.$emit('elan.created', eline);
              cordConfig.pages.push(eline);
            });

            $timeout(() => {
              $location.path('/home');
            }, 1000);
          });
        }
      }
    }
  })
})();

