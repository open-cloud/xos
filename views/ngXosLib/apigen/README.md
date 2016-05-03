# Autogenerating Angular $resource from apiblueprint format

This a tool that is intended to autogenerate Angular Js code starting from an `apiary.apirb` file.

At the moment it is pretty much working, just we don't have time to improve this and the release it as a `npm` module, so we are looking for contributors.

## Further implementation (in my opinion)

Given this input: [Subscribers.md](../../xos/tests/api/source/tenant/cord/subscribers.md)

The actual output is:

```
(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Subscribers
  * @description Angular resource to fetch Subscribers
  **/
  .service('Subscribers', function($resource){
    return $resource('/api/tenant/cord/subscriber/:id/', { id: '@id' }, {
      update: { method: 'PUT' },

      ...

      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-uplink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-uplink_speed
      **/
      'Update-Subscriber-uplink_speed': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/'
      },
      
      ...
      
    });
  })
})();
```

While I believe it is better to have something like:

```
(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Subscribers
  * @description Angular resource to fetch Subscribers
  **/
  .service('Subscribers', function($resource, $http, $q){
    let R = $resource('/api/tenant/cord/subscriber/:id/', { id: '@id' }, {
    });

    ...

    R.prototype.update_link_speed = function() {
      let deferred = $q.defer();
      $http.put(`/api/tenant/cord/subscriber/${this.id}/features/uplink_speed/`, {uplink_speed: this.uplink_speed})
      .then(res => deferred.resolve(res.data))
      .catch(e => deferred.resolve(e.data));
      return {$promise: deferred.promise};
    };
    
    ...

    return R;
  })
})();
```

In this way we can use it in this way:

```
Subscribers.get({id: 1}).$promise
  .then((subscriber) => {
    subscriber.uplink_speed = 20;
    return subscriber.update_link_speed().$promise
  })
  .then((res) => {
    console.log(res);
  })
  .catch(e => {
    console.log(e)
  });
```
