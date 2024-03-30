"""Procides the logging utilities."""

import time
from webchecks.config import config, LOGGING_FILE, LOGGING_LEVEL, \
    LOG_DEBUG, LOG_ERROR, LOG_INFO, LOG_WARNING, LOGGING_LINKS
from webchecks.utils.check import input_check

def log_level_to_string(log_level):
    """Converts log constants to strings."""
    if log_level == LOG_DEBUG:
        return "debug"
    if log_level == LOG_INFO:
        return "info"
    if log_level == LOG_WARNING:
        return "warning"
    if log_level == LOG_ERROR:
        return "error"
    return f"log_level-{log_level}"

def logging(string, log_level : int = LOG_DEBUG, tofile : bool = False, where : str = ""):
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
    input_check(log_level in range(4),
        "Bad input to logging: Check constants in the constants.py file.")

    logtype = log_level_to_string(log_level)
    if where == "":
        where = logging_get_where()
    msg = f"[{logtype}] {where}: {string}"
    if (tofile or log_level != LOG_DEBUG) and config[LOGGING_FILE] != "":
        with open(config[LOGGING_FILE], "a") as f:
            f.write("".join((time.asctime(), " ", msg, "\n")))

    if config[LOGGING_LEVEL] <= log_level:
        print(msg)

def log_link(url : str):
    """Special utility to log an accessed link. Writes the link down into the appropriate file."""
    if config[LOGGING_LINKS] != "":
        with open(config[LOGGING_LINKS], "a") as f:
            f.write(url + "\n")
    #logging(f"Accessing link {url}", log_level)



_where = [] # stack
def logging_push_where(where : str):
    """
    Set the current location of the code. When logging and you
    do not provide the location, this will be used. Note that this
    is a stack, you push a location, you pop it later to undo.
    """
    _where.append(where)

def logging_get_where() -> str:
    """
    Get last location that was pushed.
    Returns a string.
    """
    if not _where:
        return ""
    return _where[-1]

def logging_pop_where():
    """Remove the most recent location that was pushed onto the stack.
    Returns None."""
    global _where # pylint: disable=global-statement
    _where = _where[:-1]
