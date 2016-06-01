(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The xosNotification service', () => {

      let service, scope;

      const options = {icon: 'icon', body: 'message'};

      let notificationMock = {
        requestPermission: () => {
          return {
            then: cb => cb('granted')
          }
        },
        permission: 'granted'
      }


      // load the application module
      beforeEach(module('xos.helpers', ($provide) => {
        $provide.value('Notification', notificationMock);
      }));

      // inject the cartService
      beforeEach(inject(function (_xosNotification_, $rootScope) {
        // The injector unwraps the underscores (_) from around the parameter names when matching
        service = _xosNotification_;
        scope = $rootScope;
        spyOn(service, 'sendNotification');
        spyOn(service, 'checkPermission').and.callThrough();
        spyOn(notificationMock, 'requestPermission').and.callThrough();
      }));

      it('should exist', () => {
        expect(service).toBeDefined();
      });

      describe('when permission are granted', () => {
        it('should send the notification', () => {
          service.notify('Test', options);
          expect(service.sendNotification).toHaveBeenCalledWith('Test', options);
        });
      });

      describe('when permission are not granted', () => {
        beforeEach(() => {
          notificationMock.permission = false;
        });

        it('should request permission', () => {
          service.notify('Test', options);
          expect(service.checkPermission).toHaveBeenCalled();
          scope.$apply(); // this resolve the promise
          expect(service.sendNotification).toHaveBeenCalledWith('Test', options);
        });
      });

    });
  });

})();