'use strict';

describe('The Subscriber View', () => {
  
  const subscribersList = [
    {
      humanReadableName: 'cordSubscriber-1',
      features: {cdn: false, uplink_speed: 1000000000, downlink_speed: 1000000000, uverse: true, status: 'enabled'},
      id: 1,
      identity: {account_num: '123', name: 'Stanford'},
      related: {}
    }
  ];

  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.subscribers'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    
    httpBackend.whenGET('/api/tenant/cord/subscriber/?no_hyperlinks=1').respond(subscribersList);
  
    scope = $rootScope.$new();
    element = angular.element('<subscribers-list></subscribers-list>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  it('should load 1 subscriber', () => {
    // this
    httpBackend.flush();
    scope.$digest();
    let table = $(element).find('table');
    let tr = table.find('tbody:last-child tr');
    // let tds = $(tr[1]).find('td');
    // console.log(tr);
    expect(tr.length).toBe(1);
    // expect($(tds[0]).html()).toBe('cordSubscriber-1')
  });

  it('should configure xos-smart-table', () => {
    expect(isolatedScope.smartTableConfig).toEqual({resource: 'Subscribers'});
  });

  it('should render xos-smart-table', () => {
    expect($(element).find('xos-smart-table').length).toBe(1);
  });

});