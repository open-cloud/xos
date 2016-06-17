/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  var scope, element, isolatedScope, rootScope, compile;
  const compileElement = () => {

    if(!scope){
      scope = rootScope.$new();
    }

    element = angular.element('<xos-table config="config" data="data"></xos-table>');
    compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }


  describe('The xos.helper module', function(){
    describe('The xos-table component', () => {

      beforeEach(module('xos.helpers'));

      beforeEach(inject(function ($compile, $rootScope) {
        compile = $compile;
        rootScope = $rootScope;
      }));

      it('should throw an error if no config is specified', () => {
        function errorFunctionWrapper(){
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosTable] Please provide a configuration via the "config" attribute'));
      });

      it('should throw an error if no config columns are specified', () => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = rootScope.$new();
          scope.config = 'green';
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosTable] Please provide a columns list in the configuration'));
      });

      describe('when basically configured', function() {

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

        it('should render labels', () => {
          let label1 = $(element).find('thead tr th')[0]
          let label2 = $(element).find('thead tr th')[1]
          expect($(label1).text().trim()).toEqual('Label 1');
          expect($(label2).text().trim()).toEqual('Label 2');
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
              scope.config = {
                columns: [
                  {
                    label: 'Label 1',
                    prop: 'label-1',
                    type: 'boolean'
                  },
                  {
                    label: 'Label 2',
                    prop: 'label-2',
                    type: 'boolean'
                  }
                ]
              };
              scope.data = [
                {
                  'label-1': true,
                  'label-2': 1
                },
                {
                  'label-1': false,
                  'label-2': 0
                }
              ];
              compileElement();
            });

            it('should render an incon', () => {
              let td1 = $(element).find('tbody tr:first-child td')[0];
              let td2 = $(element).find('tbody tr:last-child td')[0];
              expect($(td1).find('i')).toHaveClass('glyphicon-ok');
              expect($(td2).find('i')).toHaveClass('glyphicon-remove');
            });

            describe('with field filters', () => {
              beforeEach(() => {
                scope.config.filter = 'field';
                compileElement();
              });

              it('should render a dropdown for filtering', () => {
                let td1 = $(element).find('table tbody tr td')[0];
                expect(td1).toContainElement('select');
                expect(td1).not.toContainElement('input');
              });

              it('should correctly filter results', () => {
                isolatedScope.query = {
                  'label-1': false
                };
                scope.$digest();
                expect(isolatedScope.query['label-1']).toBeFalsy();
                var tr = $(element).find('tbody:last-child > tr');
                var icon = $(tr[0]).find('td i');
                expect(tr.length).toEqual(1);
                expect(icon).toHaveClass('glyphicon-remove');
              });

              it('should correctly filter results if the field is in the form of 0|1', () => {
                isolatedScope.query = {
                  'label-2': false
                };
                scope.$digest();
                expect(isolatedScope.query['label-1']).toBeFalsy();
                var tr = $(element).find('tbody:last-child > tr');
                var icon = $(tr[0]).find('td i');
                expect(tr.length).toEqual(1);
                expect(icon).toHaveClass('glyphicon-remove');
              });
            });
          });

          describe('and is date', () => {
            beforeEach(() => {
              scope.config = {
                columns: [
                  {
                    label: 'Label 1',
                    prop: 'label-1',
                    type: 'date'
                  }
                ]
              };
              scope.data = [
                {
                  'label-1': '2015-02-17T22:06:38.059000Z'
                }
              ];
              compileElement();
            });

            it('should render an formatted date', () => {
              let td1 = $(element).find('tbody tr:first-child td')[0];
              expect($(td1).text().trim()).toEqual('14:06 Feb 17, 2015');
            });
          });

          describe('and is array', () => {
            beforeEach(() => {
              scope.data = [
                {categories: ['Film', 'Music']}
              ];
              scope.config = {
                filter: 'field',
                columns: [
                  {
                    label: 'Categories',
                    prop: 'categories',
                    type: 'array'
                  }
                ]
              }
              compileElement();
            });
            it('should render a comma separated list', () => {
              let td1 = $(element).find('tbody:last-child tr:first-child')[0];
              expect($(td1).text().trim()).toEqual('Film, Music');
            });

            it('should not render the filter field', () => {
              let filter = $(element).find('tbody tr td')[0];
              expect($(filter)).not.toContainElement('input');
            });
          });

          describe('and is object', () => {
            beforeEach(() => {
              scope.data = [
                {
                  attributes: {
                    age: 20,
                    height: 50
                  }
                }
              ];
              scope.config = {
                filter: 'field',
                columns: [
                  {
                    label: 'Categories',
                    prop: 'attributes',
                    type: 'object'
                  }
                ]
              }
              compileElement();
            });
            it('should render a list of key-values', () => {
              let td = $(element).find('tbody:last-child tr:first-child')[0];
              let ageLabel = $(td).find('dl dt')[0];
              let ageValue = $(td).find('dl dd')[0];
              let heightLabel = $(td).find('dl dt')[1];
              let heightValue = $(td).find('dl dd')[1];
              expect($(ageLabel).text().trim()).toEqual('age');
              expect($(ageValue).text().trim()).toEqual('20');
              expect($(heightLabel).text().trim()).toEqual('height');
              expect($(heightValue).text().trim()).toEqual('50');
            });

            it('should not render the filter field', () => {
              let filter = $(element).find('tbody tr td')[0];
              expect($(filter)).not.toContainElement('input');
            });
          });

          describe('and is custom', () => {

            let formatterFn = jasmine.createSpy('formatter').and.returnValue('Formatted Content');

            beforeEach(() => {
              scope.data = [
                {categories: ['Film', 'Music']}
              ];
              scope.config = {
                filter: 'field',
                columns: [
                  {
                    label: 'Categories',
                    prop: 'categories',
                    type: 'custom',
                    formatter: formatterFn
                  }
                ]
              }
              compileElement();
            });

            it('should check for a formatter property', () => {
              function errorFunctionWrapper(){
                // setup the parent scope
                scope = rootScope.$new();
                scope.config = {
                  columns: [
                    {
                      label: 'Categories',
                      prop: 'categories',
                      type: 'custom'
                    }
                  ]
                };
                compileElement();
              }
              expect(errorFunctionWrapper).toThrow(new Error('[xosTable] You have provided a custom field type, a formatter function should provided too.'));
            });

            it('should check that the formatter property is a function', () => {
              function errorFunctionWrapper(){
                // setup the parent scope
                scope = rootScope.$new();
                scope.config = {
                  columns: [
                    {
                      label: 'Categories',
                      prop: 'categories',
                      type: 'custom',
                      formatter: 'formatter'
                    }
                  ]
                };
                compileElement();
              }
              expect(errorFunctionWrapper).toThrow(new Error('[xosTable] You have provided a custom field type, a formatter function should provided too.'));
            });

            it('should format data using the formatter property', () => {
              let td1 = $(element).find('tbody:last-child tr:first-child')[0];
              expect($(td1).text().trim()).toEqual('Formatted Content');
              // the custom formatted should receive the entire object, otherwise is not so custom
              expect(formatterFn).toHaveBeenCalledWith({categories: ['Film', 'Music']});
            });

            it('should not render the filter field', () => {
              // displayed value is different from model val, filter would not work
              let filter = $(element).find('tbody tr td')[0];
              expect($(filter)).not.toContainElement('input');
            });
          });

          describe('and is icon', () => {

            beforeEach(() => {
              scope.config = {
                columns: [
                  {
                    label: 'Label 1',
                    prop: 'label-1',
                    type: 'icon',
                    formatter: item => {
                      switch (item['label-1']){
                      case 1:
                        return 'ok';
                      case 2:
                        return 'remove';
                      case 3:
                        return 'plus'
                      }
                    }
                  }
                ]
              };
              scope.data = [
                {
                  'label-1': 1
                },
                {
                  'label-1': 2
                },
                {
                  'label-1': 3
                }
              ];
              compileElement();
            });

            it('should render a custom icon', () => {
              let td1 = $(element).find('tbody tr:first-child td')[0];
              let td2 = $(element).find('tbody tr:nth-child(2) td')[0];
              let td3 = $(element).find('tbody tr:last-child td')[0];
              expect($(td1).find('i')).toHaveClass('glyphicon-ok');
              expect($(td2).find('i')).toHaveClass('glyphicon-remove');
              expect($(td3).find('i')).toHaveClass('glyphicon-plus');
            });
          });
        });

        describe('when a link property is provided', () => {
          beforeEach(() => {
            scope.data = [
              {
                id: 1}
            ];
            scope.config = {
              columns: [
                {
                  label: 'Id',
                  prop: 'id',
                  link: (item) => {
                    return `/link/${item.id}`;
                  }
                }
              ]
            }
            compileElement();
          });

          it('should check that the link property is a function', () => {
            function errorFunctionWrapper(){
              // setup the parent scope
              scope = rootScope.$new();
              scope.config = {
                columns: [
                  {
                    label: 'Categories',
                    prop: 'categories',
                    link: 'custom'
                  }
                ]
              };
              compileElement();
            }
            expect(errorFunctionWrapper).toThrow(new Error('[xosTable] The link property should be a function.'));
          });

          it('should render a link with the correct url', () => {
            let link = $(element).find('tbody tr:first-child td a')[0];
            expect($(link).attr('href')).toEqual('/link/1');
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

          describe('and a default ordering is passed', () => {

            beforeEach(() => {
              scope.config.order = {
                field: 'label-1',
                reverse: true
              };
              compileElement();
            });

            it('should orderBy the default order', () => {
              var tr = $(element).find('tr');
              expect($(tr[1]).text()).toContain('Sample 2.2');
              expect($(tr[2]).text()).toContain('Sample 1.1');
            });
          });

          describe('and an order is set', () => {
            beforeEach(() => {
              isolatedScope.orderBy = 'label-1';
              isolatedScope.reverse = true;
              scope.$digest();
            });

            it('should orderBy', function() {
              // console.log($(element).find('table'));
              var tr = $(element).find('tr');
              expect($(tr[1]).text()).toContain('Sample 2.2');
              expect($(tr[2]).text()).toContain('Sample 1.1');
            });
          });
        });
      });
    });
  });
})();

