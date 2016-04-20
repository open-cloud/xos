// TODO write tests for log

angular.module('xos.helpers')
.config([ '$provide', function( $provide )
{
  // Use the `decorator` solution to substitute or attach behaviors to
  // original service instance; @see angular-mocks for more examples....

  $provide.decorator( '$log', [ '$delegate', function( $delegate )
  {

    const isLogEnabled = () => {
      return window.location.href.indexOf('debug=true') >= 0;
    }
    // Save the original $log.debug()
    let debugFn = $delegate.info;

    // create the replacement function
    const replacement = (fn) => {
      return function(){
        if(!isLogEnabled()){
          console.log('logging is disabled');
          return;
        }
        let args    = [].slice.call(arguments);
        let now     = new Date();

        // Prepend timestamp
        args[0] = `[${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}] ${args[0]}`;

        // Call the original with the output prepended with formatted timestamp
        fn.apply(null, args)
      };
    };

    $delegate.info = replacement(debugFn);

    return $delegate;
  }]);
}]);