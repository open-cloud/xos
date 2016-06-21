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
   * @name xos.SiteEncoder.serviceGrid
   **/

  angular.module('xos.serviceGrid')
    .service('SiteEncoder', function($q, Sites){

      this.buildTosca = (siteId, toscaSpec) => {
        const d = $q.defer();

        Sites.get({id: siteId}).$promise
        .then(site => {
          const toscaObj = {};
          toscaObj[`${site.name}`] = {
            type: 'tosca.nodes.Site'
          };
          angular.extend(toscaSpec.topology_template.node_templates, toscaObj);
          d.resolve([toscaSpec, site]);
        })
        .catch(d.reject);


        return d.promise;
      };
    });
})();

