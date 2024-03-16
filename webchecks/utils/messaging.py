
import time
from webchecks.config import config, LOGGING_FILE, LOGGING_LEVEL, LOG_DEBUG, LOG_ERROR, LOG_INFO, LOG_WARNING, LOGGING_LINKS
from webchecks.utils.check import input_check

def log_level_to_string(log_level):
    """Converts log constants to strings."""
    if log_level == LOG_DEBUG:
        return "debug"
    elif log_level == LOG_INFO:
        return "info"
    elif log_level == LOG_WARNING:
        return "warning"
    elif log_level == LOG_ERROR:
        return "error"
    return f"log_level-{log_level}"

def logging(string, log_level = LOG_DEBUG, tofile = False, where = ""):
    """Logging utility. 

    Parameters:
    ------------
    string: str
        The message to print.
    log_level: int
        Constant, one from LOG_DEBUG, LOG_ERROR, LOG_INFO, LOG_WARNING.
    tofile: bool
        Whether to print the message into the logging file.
    where: str
        Optional information about the location of the logging call.
    """
    input_check(log_level in range(4), "Bad input to logging: Check constants in the constants.py file.")

    logtype = log_level_to_string(log_level)
    if where == "":
        where = logging_get_where()
    msg = f"[{logtype}] {where}: {string}"
    if (tofile or log_level != LOG_DEBUG) and config[LOGGING_FILE] != "":
        with open(config[LOGGING_FILE], "a") as f:
            f.write("".join((time.asctime(), " ", msg, "\n")))
    
    if config[LOGGING_LEVEL] <= log_level:
        print(msg)

def log_link(url, log_level = LOG_INFO):
    """Special utility to log an accessed link. Writes the link down into the appropriate file."""
    if config[LOGGING_LINKS] != "":
        with open(config[LOGGING_LINKS], "a") as f:
            f.write(url + "\n")
    #logging(f"Accessing link {url}", log_level)
    


_where = [] # stack
def logging_push_where(where):
    global _where
    _where.append(where)

def logging_get_where():
    global _where
    if _where == []:
        return ""
    return _where[-1]

def logging_pop_where():
    global _where
    _where = _where[:-1]