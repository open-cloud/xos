/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/22/16.
 */

(function () {
  'use strict';

  /**
   * @ngdoc service
   * @name xos.NetworkTemplateEncoder.serviceGrid
   **/

  // TODO write tests
  angular.module('xos.serviceGrid')
    .service('NetworkTemplateEncoder', function($q, Networkstemplates){

      this.buildTosca = (templateId, toscaSpec) => {
        const d = $q.defer();
        Networkstemplates.get({id: templateId}).$promise
        .then(template => {
          const toscaObj = {};
          toscaObj[`network_template#${template.name}`] = {
            type: 'tosca.nodes.NetworkTemplate'
          };
          angular.extend(toscaSpec.topology_template.node_templates, toscaObj);
          d.resolve([toscaSpec, template]);
        })
        .catch(e => {
          d.reject(e);
        });

        return d.promise;
      };
    });
})();

