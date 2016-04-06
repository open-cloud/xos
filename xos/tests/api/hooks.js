var hooks = require('hooks');
require('shelljs/global');

var restoreSubscriber = `ssh xos 'sudo docker exec frontend_xos_db_1 psql -U postgres -d xos -c "UPDATE core_tenantroot SET deleted=false WHERE id=1"';`

hooks.beforeEach(function (transaction, done) {
  hooks.log('before each');
  var child = exec(restoreSubscriber, {async:true});
    child.stdout.on('data', function(data) {
      done();
    });
});