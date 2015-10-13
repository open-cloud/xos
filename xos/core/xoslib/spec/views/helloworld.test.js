'use strict';

describe('The HelloWorld template', () => {

  beforeEach(() => {
    spyOn(xos.slices, 'startPolling');
  });

  xit('should call startPolling method', () => {
    expect(xos.slices.startPolling).toHaveBeenCalled();
  });
});
