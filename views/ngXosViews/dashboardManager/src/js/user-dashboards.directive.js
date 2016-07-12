(function () {
  angular.module('xos.dashboardManager')
  .directive('userDashboards', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/user-dashboards.tpl.html',
      controller: function($q, _, UserDashboards, Dashboards){
        
        // retrieving user list
        $q.all([
          UserDashboards.query().$promise,
          Dashboards.query({enabled: 'False'}).$promise,
        ])
        .then((res) => {
          let [dashboards, disabled] = res;
          this.disabled = disabled;
          this.list = {
            enabled: _.filter(dashboards, {shown: true}),
            disabled: _.filter(dashboards, {shown: false})
          };
        })
        .catch((e) => {
          throw new Error(e);
        });

        this.removeFromList = (listName, itemId) => {
          _.remove(this.list[listName], {id: itemId});
        };

        this.addToList = (listName, item) => {
          this.list[listName].push(item)
        };

        this.isInList = (listName, item) => {
          return _.find(this.list[listName], item);
        };

        this.reorderList = (list, newPos, oldPos, item) => {

          let listToOrder = _.filter(list, i => {
            // if is the item, skip it, it is already updated
            if(i.id === item.id){
              return false;
            }
            if(i.order < oldPos){
              return true;
            }
            if(i.order >= newPos){
              return true;
            }
            return false;
          });

          listToOrder = listToOrder.map(i => {
            i.order++;
            return i;
          })
        };

        this.addedToList = (event, index, item, external, list) => {
          let originalPosition;

          // load the item in the list
          let itemInList = this.isInList(list, item);
          if(itemInList){
            // if is in the list update it
            originalPosition = item.order;
            itemInList.order = index;
            item.order = index;
          }
          else {
            // create a new one
            item.order = this.list[list].length;
            item.shown = !item.shown;
          }

          const otherList = list === 'enabled' ? 'disabled' : 'enabled';

          UserDashboards.update(item).$promise
          .then((item) => {
            if(!itemInList){
              // if it is not in the list, update both lists
              this.addToList(list, item);
              this.removeFromList(otherList, item.id);
            }
            else {
              // reorder
              this.reorderList(this.list[list], index, originalPosition, item);
            }
          });
        }
      }
    };
  });
})(); 