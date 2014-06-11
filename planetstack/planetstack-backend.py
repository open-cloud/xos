#!/usr/bin/env python
import os
import argparse
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from observer.backend import Backend
from planetstack.config import Config 

config = Config()

# after http://www.erlenstar.demon.co.uk/unix/faq_2.html
def daemon():
    """Daemonize the current process."""
    if os.fork() != 0: os._exit(0)
    os.setsid()
    if os.fork() != 0: os._exit(0)
    os.umask(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, 0)
    # xxx fixme - this is just to make sure that nothing gets stupidly lost - should use devnull
    logdir=os.path.dirname(config.observer_logfile)
    # when installed in standalone we might not have httpd installed
    if not os.path.isdir(logdir): os.mkdir(logdir)
    crashlog = os.open('%s'%config.observer_logfile, os.O_RDWR | os.O_APPEND | os.O_CREAT, 0644)
    os.dup2(crashlog, 1)
    os.dup2(crashlog, 2)

def main():
    # Generate command line parser
    parser = argparse.ArgumentParser(usage='%(prog)s [options]')
    parser.add_argument('-d', '--daemon', dest='daemon', action='store_true', default=False, 
                        help='Run as daemon.')
    # smbaker: util/config.py parses sys.argv[] directly to get config file name; include the option here to avoid
    #   throwing unrecognized argument exceptions
    parser.add_argument('-C', '--config', dest='config_file', action='store', default="/opt/planetstack/plstackapi_config",
                        help='Name of config file.')
    args = parser.parse_args()
       
    if args.daemon: daemon()

    backend = Backend()
    backend.run()    

if __name__ == '__main__':
    
    main() 
