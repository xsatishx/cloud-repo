#  Copyright 2013 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
''' Basic utilities '''

import importlib
import logging
import logging.handlers
import os.path

from functools import wraps

try:
    import local_settings
except ImportError:
    local_settings = None


def debug_result(fn):
    ''' print the results of the function before returning it '''

    @wraps(fn)
    def decorated(*args, **kwds):
        temp = fn(*args, **kwds)
        logger = get_logger()
        logger.debug("DEBUG RESULT: %s", temp)
        return temp
    return decorated


def get_logger(level=getattr(local_settings, "LOG_LEVEL", logging.DEBUG),
        log_format=getattr(local_settings, "LOG_FORMAT", ('%(asctime)s '
                '%(levelname)s %(message)s %(pathname)s:%(lineno)d')),
        log_file_name=os.path.join(getattr(local_settings, "LOG_DIR", "/tmp/"),
            'tukey_middleware.log')):
    '''Return a python logger formatted according to local settings or args '''

    logger = logging.getLogger('tukey')

    if (not logger.handlers) or logger.handlers[0].baseFilename != log_file_name:
        logger.setLevel(level)

        formatter = logging.Formatter(log_format)

        logFile = logging.handlers.WatchedFileHandler(log_file_name)
        logFile.setFormatter(formatter)

        logger.addHandler(logFile)

    return logger


def get_class(path):
    ''' return a class object from path '''

    driver_modules = path.split(".")
    driver_module_name = ".".join(driver_modules[:-1])
    driver_class_name = driver_modules[-1]

    logger = get_logger()

    logger.debug("driver module name %s", driver_module_name)
    logger.debug("driver class name %s", driver_class_name)

    driver_module = importlib.import_module("%s" % driver_module_name)

    logger.debug("imported the class")

    return getattr(driver_module, driver_class_name)


def cache_attr(fn):
    """ Decorate a method by caching the result of the method to a field e.g.:

    @cache_attr
    def my_method(self):
        return 2 + 2
    ...

    after calling instance.my_method() a new field instance._my_method will
    exist such that instance._my_method == 4 and further calls to my_method()
    will return the value of _my_method and not call the actual method itself.

    Note: the decorated function is assumed to be a class method
    Note: if you use this decorator with the property decorator put property
    before cache_attr like so:

    @property
    @cache_attr
    ...

    that way @cache_attr is applied while it is still treated like a proper
    function
    """
    @wraps(fn)
    def decorated(*args, **kwds):
        attr = "_" + fn.__name__
        if not getattr(args[0], attr, None):
            setattr(args[0], attr, fn(*args, **kwds))
        return getattr(args[0], attr)
    return decorated

