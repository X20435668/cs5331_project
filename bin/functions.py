import sys
import logging
import logging.handlers as handlers
from pathlib import Path
home = str(Path.home())

logger = None
def setup_log():
    logger = logging.getLogger('telegram-bot')
    logger.setLevel(logging.DEBUG)
    # create file handler that logs debug and higher level messages
    fh = handlers.RotatingFileHandler(home+'/.update/log/update_activity.log',maxBytes=20*1024*1024,backupCount=5)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = handlers.RotatingFileHandler(home+'/.update/log/update_error.log',maxBytes=20*1024*1024,backupCount=5)
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    ih=logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    ih.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(ih)   
    return logger


def list_updates(args):
    """
    List updates available
    """
    pass


def roll_back(args):
    """
    roll back the previous change
    """
    pass

def install_update(args):
    """
    install updates
    """
    pass

def print_manual():
    print("This is print manual")
    pass

if __name__=="__main__":
    logger=setup_log()    
    if len(sys.argv) < 2:
        print_manual()
    elif sys.argv[1] == 'list':
        list_updates(sys.argv[2:])
    elif sys.argv[1] == 'rollback':
        roll_back(sys.argv[2:])
    elif sys.argv[1] == 'install':
        install_update(sys.argv[2:])
    else:
        print_manual()
