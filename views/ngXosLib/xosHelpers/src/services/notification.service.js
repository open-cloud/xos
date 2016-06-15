/* eslint-disable  angular/ng_window_service*/
(function() {
  'use strict';

  angular
  .module('xos.helpers')
  .factory('Notification', function(){
    return window.Notification;
  })
  /**
  * @ngdoc service
  * @name xos.helpers.xosNotification
  * @description This factory define a set of helper function to trigger desktop notification
  **/
  .service('xosNotification', function($q, $log, Notification) {

    this.checkPermission = () => {
      const deferred = $q.defer();
      Notification.requestPermission()
      .then(permission => {
        if (permission === 'granted') {
          deferred.resolve(permission);
        }
        else {
          deferred.reject(permission);
        }
      });
      return deferred.promise;
    };

    this.sendNotification = (title, options) => {
      const notification = new Notification(title, options);
      notification.onerror = function(err){
        $log.error(err);
      };
    };

    /**
    * @ngdoc method
    * @name xos.helpers.xosNotification#notify
    * @methodOf xos.helpers.xosNotification
    * @description
    * This method will check for user permission and if granted will send a browser notification.
    * @param {string} title The notification title
    * @param {object} options The notification options: `{icon: 'url', body: 'Notification body'}`
    **/

    this.notify = (title, options) => {
      if (!('Notification' in window)) {
        $log.info('This browser does not support desktop notification');
      }
      else if (Notification.permission !== 'granted') {
        this.checkPermission()
        .then(() => this.sendNotification(title, options));
      }
      else if (Notification.permission === 'granted') {
        this.sendNotification(title, options);
      }
    }

  })
})();
