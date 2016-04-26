/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

    /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosSmartTable
    * @restrict E
    * @description The xos-table directive
    * @param {Object} config The configuration for the component.
    * @scope
    * @example
    */
   
  .directive('xosSmartTable', function(){
    return {
      restrict: 'E',
      scope: {
        config: '='
      },
      template: `
        <xos-table config="vm.tableConfig" data="vm.data"></xos-table>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($injector, LabelFormatter, _){
        
        this.tableConfig = {
          columns: [
          ],
          // actions: [
          //   {
          //     label: 'delete',
          //     icon: 'remove',
          //     cb: (user) => {
          //       console.log(user);
          //       // _.remove(this.users, {id: user.id});
          //     },
          //     color: 'red'
          //   }
          // ],
          filter: 'field',
          order: true,
          pagination: {
            pageSize: 10
          }
        };

        let Resource = $injector.get(this.config.resource);

        Resource.query().$promise
        .then((res) => {

          let props = Object.keys(res[0]);

          _.remove(props, p => {
            return p == 'id' || p == 'password' || p == 'validators'
          });

          let labels = props.map(p => LabelFormatter.format(p));

          console.log(props, labels);

          props.forEach((p, i) => {
            this.tableConfig.columns.push({
              label: labels[i],
              prop: p
            });
          });


          console.log(this.tableConfig.columns);

          this.data = res;
        })
      }
    };
  });
})();