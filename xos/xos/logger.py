#!/usr/bin/env python

#----------------------------------------------------------------------
# Copyright (c) 2008 Board of Trustees, Princeton University
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS 
# IN THE WORK.
#----------------------------------------------------------------------

import os, sys
import traceback
import logging, logging.handlers
import logstash
from xos.config import Config

CRITICAL=logging.CRITICAL
ERROR=logging.ERROR
WARNING=logging.WARNING
INFO=logging.INFO
DEBUG=logging.DEBUG

# a logger that can handle tracebacks 
class Logger:
    def __init__ (self,logfile=None,loggername=None,level=logging.INFO):
        # Logstash config
        try:
            logstash_host,logstash_port = Config().observer_logstash_hostport.split(':')
            logstash_handler = logstash.LogstashHandler(logstash_host, int(logstash_port), version=1)
        except:
            logstash_handler = None

        # default is to locate loggername from the logfile if avail.
        if not logfile:
            try:
                logfile = Config().observer_log_file
            except:
                logfile = "/var/log/xos.log"

        if (logfile == "console"):
            loggername = "console"
            handler = logging.StreamHandler()
        else:
            if not loggername:
                loggername=os.path.basename(logfile)
            try:
                handler=logging.handlers.RotatingFileHandler(logfile,maxBytes=1000000, backupCount=5)
            except IOError:
                # This is usually a permissions error becaue the file is
                # owned by root, but httpd is trying to access it.
                tmplogfile=os.getenv("TMPDIR", "/tmp") + os.path.sep + os.path.basename(logfile)
                # In strange uses, 2 users on same machine might use same code,
                # meaning they would clobber each others files
                # We could (a) rename the tmplogfile, or (b)
                # just log to the console in that case.
                # Here we default to the console.
                if os.path.exists(tmplogfile) and not os.access(tmplogfile,os.W_OK):
                    loggername = loggername + "-console"
                    handler = logging.StreamHandler()
                else:
                    handler=logging.handlers.RotatingFileHandler(tmplogfile,maxBytes=1000000, backupCount=5)

        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger=logging.getLogger(loggername)
        self.logger.setLevel(level)
        # check if logger already has the handler we're about to add
        handler_exists = False
        logstash_handler_exists = False

        if not len(self.logger.handlers):
            self.logger.addHandler(handler)

            if (logstash_handler):
                self.logger.addHandler(logstash_handler)

        self.loggername=loggername

    def setLevel(self,level):
        self.logger.setLevel(level)

    # shorthand to avoid having to import logging all over the place
    def setLevelDebug(self):
        self.logger.setLevel(logging.DEBUG)

    def debugEnabled (self):
        return self.logger.getEffectiveLevel() == logging.DEBUG

    # define a verbose option with s/t like
    # parser.add_option("-v", "--verbose", action="count", dest="verbose", default=0)
    # and pass the coresponding options.verbose to this method to adjust level
    def setLevelFromOptVerbose(self,verbose):
        if verbose==0:
            self.logger.setLevel(logging.WARNING)
        elif verbose==1:
            self.logger.setLevel(logging.INFO)
        elif verbose>=2:
            self.logger.setLevel(logging.DEBUG)
    # in case some other code needs a boolean
    def getBoolVerboseFromOpt(self,verbose):
        return verbose>=1
    def getBoolDebugFromOpt(self,verbose):
        return verbose>=2

    ####################

    def extract_context(self,cur):
        try:
            observer_name=Config().observer_name
            cur['synchronizer_name']=observer_name
        except:
            pass

        return cur

    def info(self, msg, extra={}):
        extra = self.extract_context(extra) 
        self.logger.info(msg, extra=extra)

    def debug(self, msg, extra={}):
        extra = self.extract_context(extra) 
        self.logger.debug(msg, extra=extra)
        
    def warn(self, msg, extra={}):
        extra = self.extract_context(extra) 
        self.logger.warn(msg, extra=extra)

    # some code is using logger.warn(), some is using logger.warning()
    def warning(self, msg, extra={}):
        extra = self.extract_context(extra) 
        self.logger.warning(msg,extra=extra)
   
    def error(self, msg, extra={}):
        extra = self.extract_context(extra) 
        self.logger.error(msg, extra=extra)    
 
    def critical(self, msg, extra={}):
        extra = self.extract_context(extra) 
        self.logger.critical(msg, extra=extra)

    # logs an exception - use in an except statement
    def log_exc(self,message, extra={}):
        extra = self.extract_context(extra) 
        self.error("%s BEG TRACEBACK"%message+"\n"+traceback.format_exc().strip("\n"), extra=extra)
        self.error("%s END TRACEBACK"%message, extra=extra)
    
    def log_exc_critical(self,message, extra={}):
        extra = self.extract_context(extra) 
        self.critical("%s BEG TRACEBACK"%message+"\n"+traceback.format_exc().strip("\n"), extra=extra)
        self.critical("%s END TRACEBACK"%message, extra=extra)
    
    # for investigation purposes, can be placed anywhere
    def log_stack(self,message, extra={}):
        extra = self.extract_context(extra) 
        to_log="".join(traceback.format_stack())
        self.info("%s BEG STACK"%message+"\n"+to_log,extra=extra)
        self.info("%s END STACK"%message,extra=extra)

    def enable_console(self, stream=sys.stdout):
        formatter = logging.Formatter("%(message)s")
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


info_logger = Logger(loggername='info', level=logging.INFO)
debug_logger = Logger(loggername='debug', level=logging.DEBUG)
warn_logger = Logger(loggername='warning', level=logging.WARNING)
error_logger = Logger(loggername='error', level=logging.ERROR)
critical_logger = Logger(loggername='critical', level=logging.CRITICAL)
logger = info_logger
observer_logger = Logger(logfile='/var/log/observer.log', loggername='observer', level=logging.DEBUG)
########################################
import time

def profile(logger):
    """
    Prints the runtime of the specified callable. Use as a decorator, e.g.,
    
    @profile(logger)
    def foo(...):
        ...
    """
    def logger_profile(callable):
        def wrapper(*args, **kwds):
            start = time.time()
            result = callable(*args, **kwds)
            end = time.time()
            args = map(str, args)
            args += ["%s = %s" % (name, str(value)) for (name, value) in kwds.iteritems()]
            # should probably use debug, but then debug is not always enabled
            logger.info("PROFILED %s (%s): %.02f s" % (callable.__name__, ", ".join(args), end - start))
            return result
        return wrapper
    return logger_profile


if __name__ == '__main__': 
    print 'testing logging into logger.log'
    logger1=Logger('logger.log', loggername='std(info)')
    logger2=Logger('logger.log', loggername='error', level=logging.ERROR)
    logger3=Logger('logger.log', loggername='debug', level=logging.DEBUG)
    
    for (logger,msg) in [ (logger1,"std(info)"),(logger2,"error"),(logger3,"debug")]:
        
        print "====================",msg, logger.logger.handlers
   
        logger.enable_console()
        logger.critical("logger.critical")
        logger.error("logger.error")
        logger.warn("logger.warning")
        logger.info("logger.info")
        logger.debug("logger.debug")
        logger.setLevel(logging.DEBUG)
        logger.debug("logger.debug again")
    
        @profile(logger)
        def sleep(seconds = 1):
            time.sleep(seconds)

        logger.info('console.info')
        sleep(0.5)
        logger.setLevel(logging.DEBUG)
        sleep(0.25)

