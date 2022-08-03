import logging
import os
import splunk 


def setup_logging():
    logger = logging.getLogger('kvsbackup')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "kvsbackup.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')

    LOGGING_FORMAT = "%(asctime)s %(levelname)-s %(process)d %(module)s %(funcName)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    # add stdout
    stdout_log_handler = logging.StreamHandler()
    stdout_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(stdout_log_handler)
    #logger.addHandler(logging.StreamHandler())
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)

    #default logging level , can be overidden in stanza config
    logger.setLevel(logging.DEBUG)
    return logger
