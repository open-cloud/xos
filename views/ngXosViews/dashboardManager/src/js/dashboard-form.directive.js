(function () {
  'use strict';

  angular.module('xos.dashboardManager')
  .directive('dashboardForm', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/dashboard-form.tpl.html',
      controller: function($stateParams, $log, Dashboards){

        this.dashboard = {
          enabled: true
        };

        if($stateParams.id){
          Dashboards.get({id: $stateParams.id}).$promise
          .then(dash => {
            this.dashboard = dash;
          })
          .catch(e => {
            console.log(e);
          })
        }

        this.formConfig = {
          exclude: [
            'backend_register',
            'controllers',
            'deployments',
            'enacted',
            'humanReadableName',
            'lazy_blocked',
            'no_policy',
            'no_sync',
            'policed',
            'write_protect'
          ],
          actions: [
            {
              label: 'Save',
              icon: 'ok',
              cb: (item) => {
                this.createOrUpdateDashboard(item);
              },
              class: 'success'
            },
            {
              label: 'Esport to TOSCA',
              icon: 'export',
              cb: (item) => {
                this.toTosca(item);
              },
              class: 'primary'
            }
          ],
          formName: 'dashboardForm',
          feedback: {
            show: false,
            message: 'Form submitted successfully !!!',
            type: 'success'
          },
          fields: {
            name: {
              type: 'string',
              validators: {
                required: true
              }
            },
            url: {
              type: 'string',
              validators: {
                required: true
              }
            },
            enabled: {
              type: 'boolean'
            }
          }
        };

        this.createOrUpdateDashboard = dashboard => {
          let p;
          if(dashboard.id){
            delete dashboard.controllers;
            delete dashboard.deployments;
            p = dashboard.$save();
          }
          else{
            p = Dashboards.save(dashboard).$promise;
          }

          p.then(res => {
            this.formConfig.feedback.show = true;
          })
          .catch(e => {
            $log.info(e);
            this.formConfig.feedback.show = true;
            this.formConfig.feedback.message = e;
            this.formConfig.feedback.type = 'error';
          })
        };

        this.toTosca = dashboard => {
          const yaml = {}
          yaml[dashboard.name] = {
            type: 'tosca.nodes.DashboardView',
            properties: {
              url: dashboard.url
            }
          };
          this.tosca = jsyaml.dump(yaml).replace(/'/g, '');

          const yamlRequirements = {
            requirements: []
          };
          const dashboardRequirements = {};
          dashboardRequirements[`${dashboard.name.toLowerCase()}_dashboard`] = {
            node: dashboard.name,
            relationship: 'tosca.relationships.UsesDashboard'
          }
          yamlRequirements.requirements.push(dashboardRequirements);
          this.toscaRequirements = jsyaml.dump(yamlRequirements).replace(/'/g, '');
        };
      }
    }
  });
})();