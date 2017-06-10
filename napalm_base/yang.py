# Copyright 2017 Dravetech AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Python3 support
from __future__ import print_function
from __future__ import unicode_literals

import napalm_yang


# TODO this should come from napalm-yang
# TODO we probably need to adapt the validate framework as well
SUPPORTED_MODELS = [
    "openconfig-interfaces",
    "openconfig-network-instance",
]


class NapalmYangIntegration(object):

    @property
    def yang(self):
        if not hasattr(self, "config"):
            self.config = Yang("config", self)
            self.state = Yang("state", self)
        return self


class Yang(object):

    def __init__(self, mode, device):
        self._mode = mode
        self.device = device
        self.device.running = napalm_yang.base.Root()

        if mode == "config":
            self.device.candidate = napalm_yang.base.Root()

        for model in SUPPORTED_MODELS:
            model = model.replace("-", "_")
            funcname = "get_{}".format(model)
            setattr(Yang, funcname, yang_get_wrapper(model))

    def translate(self, merge=False, replace=False, profile=None):
        if profile is None:
            profile = self.device.profile

        if merge:
            return self.device.candidate.translate_config(profile=profile,
                                                          merge=self.device.running)
        elif replace:
            return self.device.candidate.translate_config(profile=profile,
                                                          replace=self.device.running)
        else:
            return self.device.candidate.translate_config(profile=profile)

    def diff(self):
        return napalm_yang.utils.diff(self.device.candidate, self.device.running)


def yang_get_wrapper(model):
    def method(self, **kwargs):

        # This is the class for the model
        modelobj = getattr(napalm_yang.models, model)()

        # We attach it to the running object
        self.device.running.add_model(modelobj)

        # We extract the attribute assigned to the running object
        # for example, device.running.interfaces
        modelattr = getattr(self.device.running, modelobj.elements().keys()[0])

        # We get the correct method (parse_config or parse_state)
        parsefunc = getattr(self.device.running, "parse_{}".format(self._mode))

        # We parse *only* the model that corresponds to this call
        parsefunc(device=self.device, attrs=[modelattr])

        # If we are in configuration mode and the user requests it
        # we create a candidate as well
        if kwargs.pop("candidate"):
            modelobj = getattr(napalm_yang.models, model)()
            self.device.candidate.add_model(modelobj)
            modelattr = getattr(self.device.candidate, modelobj.elements().keys()[0])
            parsefunc = getattr(self.device.candidate, "parse_{}".format(self._mode))
            parsefunc(device=self.device, attrs=[modelattr])

        # In addition to populate the running object, we return a dict with the contents
        # of the parsed model
        f = kwargs.get("filter", True)
        return modelattr.get(filter=f)

    return method
