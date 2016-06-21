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
   * @name xos.ArchiveManager.serviceGrid
   **/

  angular.module('xos.serviceGrid')
  .service('ArchiveManager', function(){
    this.createArchive = () => {
      this.archive = new JSZip();
    };

    this.addFile = (fileName, content) => {
      this.archive.file(fileName, content);
    };

    this.download = (name) => {
      console.log(this.archive);
      this.archive.generateAsync({type: 'blob'})
        .then(function(content) {
          saveAs(content, `${name}.zip`);
        })
        .catch(e => {
          console.log(e);
        });
    };
  });
})();

