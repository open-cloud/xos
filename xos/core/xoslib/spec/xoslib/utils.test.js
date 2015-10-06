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

  describe('The templateFromId method', () => {
    xit('should behave...', () => {
      
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
    xit('should be tested', () => {
      
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

  describe('The array_diff method', () => {
    it('should return the difference between two array', () => {
      let res = array_diff([1,2,3], [1,2,5]);
      expect(res).toEqual(['3', '5']); //is this right?
      console.log('convert the array to a string, can\'t we use lodash?');
    });
  });

  describe('The array_subtract method', () => {
    it('should substract two arrays', () => {
      let res = array_subtract([1,2],[1,2,3]);
      expect(res).toEqual([1,2]);
      console.log('[1,2] - [1,2,3] = [1,2]?');
    });
  });

  describe('The array_same_elements method', () => {
    it('should return true if array have same elements', () => {
      let res = array_same_elements([1,2],[2,1]);
      expect(res).toBeTruthy();
    });

    it('should return false if array have different elements', () => {
      let res = array_same_elements([1,2],[2,2]);
      expect(res).toBeFalsy();
    });
  });

  describe('The array_pair_lookup method', () => {
    it('should return corresponding values in other array', () => {
      let res = array_pair_lookup('Baker', ['Scott', 'Jhon'], ['Baker', 'Snow']);
      expect(res).toEqual('Scott');
    });

    it('should return missing value', () => {
      let res = array_pair_lookup('Larry', ['Scott', 'Jhon'], ['Baker', 'Snow']);
      expect(res).toEqual('object #Larry');
    });
  });

  describe('The all_options method', () => {

    beforeEach(() => {
      jasmine.getFixtures().set(`
        <select id="test-select">
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3/option>
        </select>
      `);
    });

    it('should return all options from a select', () => {
      let res = all_options('#test-select');
      expect(res).toEqual(['1','2','3']);
    });
  });

  describe('The make_same_width method', () => {
    xit('should be tested', () => {
          
    });
  });

  describe('The strip_scripts method', () => {
    it('should be tested', () => {
      const mockHtml = `
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <title>Test</title>
            <script src="myScript.js"></script>
          </head>
          <body></body>
        </html>
      `;

      let res = strip_scripts(mockHtml);
      expect(res.indexOf('script')).toBe(-1);
    });
  });

  describe('The parse_portlist method', () => {
    it('should parse space separated ports', () => {
      let res = parse_portlist('tcp 123, tcp 124');
      expect(res).toEqual([{l4_protocol: 'tcp', l4_port: '123'},{l4_protocol: 'tcp', l4_port: '124'}]);
    });

    it('should parse / separated ports', () => {
      let res = parse_portlist('tcp/123, tcp/124');
      expect(res).toEqual([{l4_protocol: 'tcp', l4_port: '123'},{l4_protocol: 'tcp', l4_port: '124'}]);
    });

    it('should parse : joined ports', () => {
      let res = parse_portlist('tcp 123:124');
      expect(res).toEqual([{l4_protocol: 'tcp', l4_port: '123:124'}]);
    });

    it('should parse - joined ports', () => {
      let res = parse_portlist('tcp 123-124');
      expect(res).toEqual([{l4_protocol: 'tcp', l4_port: '123:124'}]);
    });

    it('should throw an error for malformed separator', () => {
      let res = () => {
        return parse_portlist('tcp+123, tcp+124');
      }
      expect(res).toThrow('malformed port specifier tcp+123, format example: "tcp 123, tcp 201:206, udp 333"');
    });

    it('should should throw if unknown protocol', () => {
      let res = () => {
        parse_portlist('abc 123');
      }
      expect(res).toThrow('unknown protocol abc');
    });
  });

  describe('The portlist_regexp', () => {

    const r = portlist_regexp();

    it('should not match tcp', () => {
      expect('tcp'.match(r)).toBeNull();
    });

    it('should match tcp 123', () => {
      expect('tcp 123'.match(r)[0]).toEqual('tcp 123');
    });

    it('should match udp 123', () => {
      expect('udp 123'.match(r)[0]).toEqual('udp 123');
    });

    it('should match tcp 123, upd 456', () => {
      expect('tcp 123, udp 456'.match(r)[0]).toEqual('tcp 123, udp 456');
    });
  });
});