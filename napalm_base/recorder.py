from functools import wraps

from collections import defaultdict

from datetime import datetime

import pip
import logging
import os
import pickle
import yaml


logger = logging.getLogger("napalm-base")


# This is written as a decorator so it can be used independently
def recorder(cls):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if cls.mode == "pass":
                return func(*args, **kwargs)

            cls.current_count = cls.calls[func.__name__]
            cls.calls[func.__name__] += 1

            if cls.mode == "record":
                return record(cls, func, *args, **kwargs)
            elif cls.mode == "replay":
                return replay(cls, func, *args, **kwargs)

        return wrapper
    return real_decorator


def record(cls, func, *args, **kwargs):
    logger.debug("Recording {}".format(func.__name__))
    r = func(*args, **kwargs)
    filename = "{}.{}".format(func.__name__, cls.current_count)
    with open(os.path.join(cls.path, filename), 'w') as f:
        f.write(pickle.dumps(r))
    return r


def replay(cls, func, *args, **kwargs):
    logger.debug("Replaying {}".format(func.__name__))
    filename = "{}.{}".format(func.__name__, cls.current_count)
    with open(os.path.join(cls.path, filename), 'r') as f:
        r = pickle.load(f)
    return r


class Recorder(object):

    def __init__(self, cls, recorder_options, *args, **kwargs):
        self.cls = cls

        self.mode = recorder_options.get("mode", "pass")
        self.path = recorder_options.get("path", "")

        self.device = cls(*args, **kwargs)
        self.calls = defaultdict(lambda: 1)

        if self.mode == "record":
            self.stamp_metadata()

    def stamp_metadata(self):
        dt = datetime.now()

        installed_packages = pip.get_installed_distributions()
        napalm_packages = sorted(["{}=={}".format(i.key, i.version)
                                  for i in installed_packages if i.key.startswith("napalm")])

        with open("{}/metadata.yaml".format(self.path), "w") as f:
            f.write(yaml.dump({"date": dt, "napalm_version": napalm_packages},
                              default_flow_style=False))

    def __getattr__(self, attr):
        return recorder(self)(self.device.__getattribute__(attr))
