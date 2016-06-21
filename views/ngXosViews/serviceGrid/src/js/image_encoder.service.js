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
   * @name xos.ImageEncoder.serviceGrid
   **/

  // TODO write tests
  angular.module('xos.serviceGrid')
    .service('ImageEncoder', function($q, Images){

      this.buildTosca = (imageId, toscaSpec) => {
        const d = $q.defer();

        Images.get({id: imageId}).$promise
          .then(image => {
            const toscaObj = {};
            toscaObj[`image#${image.name}`] = {
              type: 'tosca.nodes.Image'
            };
            angular.extend(toscaSpec.topology_template.node_templates, toscaObj);
            d.resolve([toscaSpec, image]);
          })
          .catch(d.reject);


        return d.promise;
      };
    });
})();

