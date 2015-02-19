#!/usr/bin/env python
import os
import argparse
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from observer.backend import Backend
from xos.config import Config, DEFAULT_CONFIG_FN

try:
    from django import setup as django_setup # django 1.7
except:
    django_setup = False

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

    if hasattr(config, "observer_pidfile"):
        pidfile = config.get("observer_pidfile")
    else:
        pidfile = "/var/run/xosobserver.pid"
    try:
        file(pidfile,"w").write(str(os.getpid()))
    except:
        print "failed to create pidfile %s" % pidfile

def main():
    # Generate command line parser
    parser = argparse.ArgumentParser(usage='%(prog)s [options]')
    parser.add_argument('-d', '--daemon', dest='daemon', action='store_true', default=False,
                        help='Run as daemon.')
    # smbaker: util/config.py parses sys.argv[] directly to get config file name; include the option here to avoid
    #   throwing unrecognized argument exceptions
    parser.add_argument('-C', '--config', dest='config_file', action='store', default=DEFAULT_CONFIG_FN,
                        help='Name of config file.')
    args = parser.parse_args()

    if args.daemon: daemon()

    if django_setup: # 1.7
        django_setup()

    backend = Backend()
    backend.run()    

if __name__ == '__main__':
    
    main() 
