(function () {
  'use strict';

  /**
   * @ngdoc service
   * @name xos.toscaExporter.serviceGrid
   **/

  angular.module('xos.serviceGrid')
  .service('ToscaEncoder', function($q, _, ArchiveManager, ServiceEncoder, SlicesEncoder){

    let toscaSpec = {
      tosca_definitions_version: 'tosca_simple_yaml_1_0',
      description: '',
      imports: [
        'custom_types/xos.yaml'
      ],
      topology_template:{
        node_templates: {}
      }
    };

    /**
     * @ngdoc method
     * @name xos.serviceGrid.ToscaEncoder#$toYml
     * @methodOf xos.serviceGrid.ToscaEncoder
     * @description
     * Convert a Json data structure to Yaml, use https://github.com/nodeca/js-yaml
     * @param {Object} item A Json object to be converted
     * @returns {string} The Yaml representation of the Json input
     **/

    this.toYml = (item) => {
      return jsyaml.dump(item).replace(/'/g, '');
    };

    this.export = (service) => {
      ArchiveManager.download(service.name);
      const file = this.toYml(toscaSpec);
      return file;
    };

    this.serviceToTosca = service => {

      ArchiveManager.createArchive();
      //clean
      toscaSpec.topology_template.node_templates = {};

      toscaSpec.description = `Just enough Tosca to get the ${service.humanReadableName} service up and running`;

      const d = $q.defer();

      // build service properties
      ServiceEncoder.formatServiceProperties(service, toscaSpec)
      .then(spec => {
        return SlicesEncoder.getServiceSlices(service, spec);
      })
      // add required slices (and it will all the slice requirements)
      .then((spec) => {
        return ServiceEncoder.getServiceRequirements(service, spec);
      })
      // add required services (provider services)
      .then((spec) => {
        ArchiveManager.addFile(`${service.name}_service.yaml`, this.toYml(spec));

        this.export(service);

        d.resolve(this.toYml(spec));
      })
      .catch(e => {
        d.reject(e);
      });
      return d.promise;

    }

  });

}());