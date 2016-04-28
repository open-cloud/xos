/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The xos-table component', () => {

      beforeEach(module('xos.helpers'));

      it('should throw an error if no config is specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          $compile(angular.element('<xos-table></xos-table>'))($rootScope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosTable] Please provide a configuration via the "config" attribute'));
      }));

      it('should throw an error if no config columns are specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          let scope = $rootScope.$new();
          scope.config = 'green';
          $compile(angular.element('<xos-table config="config"></xos-table>'))(scope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosTable] Please provide a columns list in the configuration'));
      }));

      describe('when basicly configured', function() {
        var scope, element, isolatedScope;

        beforeEach(inject(function ($compile, $rootScope) {
          scope = $rootScope.$new();

          scope.config = {
            columns: [
              {
                label: 'Label 1',
                prop: 'label-1'
              },
              {
                label: 'Label 2',
                prop: 'label-2'
              }
            ]
          };

          scope.data = [
            {
              'label-1': 'Sample 1.1',
              'label-2': 'Sample 1.2'
            },
            {
              'label-1': 'Sample 2.1',
              'label-2': 'Sample 2.2'
            }
          ]

          element = angular.element('<xos-table config="config" data="data"></xos-table>');
          $compile(element)(scope);
          scope.$digest();
          isolatedScope = element.isolateScope().vm;
        }));

        it('should contain 2 columns', function() {
          var th = element[0].getElementsByTagName('th');
          expect(th.length).toEqual(2);
          expect(isolatedScope.columns.length).toEqual(2);
        });

        it('should contain 3 rows', function() {
          var tr = element[0].getElementsByTagName('tr');
          expect(tr.length).toEqual(3);
        });

        describe('when no data are provided', () => {
          beforeEach(() => {
            isolatedScope.data = [];
            scope.$digest();
          });
          it('should render an alert', () => {
            let alert = element[0].getElementsByClassName('alert');
            let table = element[0].getElementsByTagName('table');
            expect(alert.length).toEqual(1);
            expect(table.length).toEqual(1);
          });
        });

        describe('when a field type is provided', () => {
          describe('and is boolean', () => {
            beforeEach(() => {
              console.log('iS: ' + isolatedScope);
              isolatedScope.config = {
                columns: [
                  {
                    label: 'Label 1',
                    prop: 'label-1',
                    type: 'boolean'
                  }
                ]
              };
              isolatedScope.data = [
                {
                  'label-1': true
                },
                {
                  'label-1': false
                }
              ];
              scope.$digest();
            });

            it('should render an incon', () => {
              let td1 = $(element).find('tbody tr:first-child td')[0];
              let td2 = $(element).find('tbody tr:last-child td')[0];
              console.log(td2);
              expect($(td1).find('i')).toHaveClass('glyphicon-ok');
              expect($(td2).find('i')).toHaveClass('glyphicon-remove');
            });
          });

          describe('and is date', () => {
            beforeEach(() => {
              console.log('iS: ' + isolatedScope);
              isolatedScope.config = {
                columns: [
                  {
                    label: 'Label 1',
                    prop: 'label-1',
                    type: 'date'
                  }
                ]
              };
              isolatedScope.data = [
                {
                  'label-1': '2015-02-17T22:06:38.059000Z'
                }
              ];
              scope.$digest();
            });

            it('should render an formatted date', () => {
              let td1 = $(element).find('tbody tr:first-child td')[0];
              expect($(td1).text()).toEqual('02-17-2015 14:06:38');
            });
          });
        });

        describe('when actions are passed', () => {

          let cb = jasmine.createSpy('callback')

          beforeEach(() => {
            isolatedScope.config.actions = [
              {
                label: 'delete',
                icon: 'remove',
                cb: cb,
                color: 'red'
              }
            ];
            scope.$digest();
          });

          it('should have 3 columns', () => {
            var th = element[0].getElementsByTagName('th');
            expect(th.length).toEqual(3);
            expect(isolatedScope.columns.length).toEqual(2);
          });

          it('when clicking on action should invoke callback', () => {
            var link = element[0].getElementsByTagName('a')[0];
            link.click();
            expect(cb).toHaveBeenCalledWith(scope.data[0]);
          });
        });

        describe('when filter is fulltext', () => {
          beforeEach(() => {
            isolatedScope.config.filter = 'fulltext';
            scope.$digest();
          });

          it('should render a text field', () => {
            var textField = element[0].getElementsByTagName('input');
            expect(textField.length).toEqual(1);
          });

          describe('and a value is enterd', () => {
            beforeEach(() => {
              isolatedScope.query = '2.2';
              scope.$digest();
            });

            it('should contain 2 rows', function() {
              var tr = element[0].getElementsByTagName('tr');
              expect(tr.length).toEqual(2);
            });
          });
        });

        describe('when filter is field', () => {
          beforeEach(() => {
            isolatedScope.config.filter = 'field';
            scope.$digest();
          });

          it('should render a text field for each column', () => {
            var textField = element[0].getElementsByTagName('input');
            expect(textField.length).toEqual(2);
          });

          describe('and a value is enterd', () => {
            beforeEach(() => {
              isolatedScope.query = {'label-1': '2.1'};
              scope.$digest();
            });

            it('should contain 3 rows', function() {
              var tr = element[0].getElementsByTagName('tr');
              expect(tr.length).toEqual(3);
            });
          });
        });

        describe('when order is true', () => {
          beforeEach(() => {
            isolatedScope.config.order = true;
            scope.$digest();
          });

          it('should render a arrows beside', () => {
            var arrows = element[0].getElementsByTagName('i');
            expect(arrows.length).toEqual(4);
          });

          describe('and an order is set', () => {
            beforeEach(() => {
              isolatedScope.orderBy = 'label-1';
              isolatedScope.reverse = true;
              scope.$digest();
            });

            it('should orderBy', function() {
              var tr = element[0].getElementsByTagName('tr');
              expect(angular.element(tr[1]).text()).toContain('Sample 2.2');
              expect(angular.element(tr[2]).text()).toContain('Sample 1.1');
            });
          });
        });
      });
    });
  });
})();

