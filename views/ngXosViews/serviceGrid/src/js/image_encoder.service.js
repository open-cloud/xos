
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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

