'use strict';

describe('The XOS Lib Utilities', function() {
  describe('The idInArray method', function() {
    it('should match a string ID', () => {
      let res = idInArray('1', [1, 2, 3]);
      expect(res).toBeTruthy();
    });

    it('should march a number ID', () => {
      let res = idInArray(1, [1, 2, 3]);
      expect(res).toBeTruthy();
    });

    it('should not match this ID', () => {
      let res = idInArray(4, [1, 2, 3]);
      expect(res).toBeFalsy();
    });
  });

  describe('The firstCharUpper', () => {
    it('should return the first char UPPERCASE', () => {
      let res = firstCharUpper('test');
      expect(res).toEqual('Test');
    });
  });

  describe('The toTitleCase', () => {
    it('should convert all word\'s first letter to uppercase and the other to lowercase', () => {
      let res = toTitleCase('tesT tEst');
      expect(res).toEqual('Test Test');
    });
  });

  describe('The fieldNameToHumanReadable method', () => {
    it('should convert lodash to spaces and apply toTitleCase', () => {
      let res = fieldNameToHumanReadable('tEst_fIelD');
      expect(res).toEqual('Test Field')
    });
  });

  describe('The limitTableRows', () => {
    it('should be tested', () => {
      
    });
  });

  describe('The validateField', () => {
    it('should should validate notBlank', () => {
      let res = validateField('notBlank', null);
      expect(res).toEqual('can not be blank');
    });

    it('should validate a url', () => {
      let res = validateField('url', 'test a fake url');
      expect(res).toEqual('must be a valid url');
    });

    it('should validate a port', () => {
      let res = validateField('portspec', 'i a not a port');
      expect(res).toEqual('must be a valid portspec (example: \'tcp 123, udp 456-789\')');
    });

    it('should return true for a valid url', () => {
      let res = validateField('url', 'www.onlab.us');
      expect(res).toBeTruthy();
    });
  });
});