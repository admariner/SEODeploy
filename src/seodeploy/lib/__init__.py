#! /usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2020 JR Oakes
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""SEODeploy: SEOTesting Class."""

import json
from datetime import datetime
import pandas as pd

from seodeploy.lib.modules import ModuleConfig
from seodeploy.lib.logging import get_logger
from seodeploy.lib.config import Config

_LOG = get_logger(__name__)


class SEOTesting:

    """ SEOTesting Class: Base Class for SEODeploy."""

    def __init__(self, config=None):
        """Initialize SEOTesting Class"""

        self.config = config or Config()
        self.messages = []
        self.module_config = ModuleConfig(self.config)

        self.sample_paths = None
        self.modules = None
        self.summary = None
        self.passing = True

    def execute(self, sample_paths=None):
        """Execute modules against argument, sample_paths."""

        self.summary = {"started": str(datetime.now())}

        # Get Sample Paths
        self.sample_paths = sample_paths or self.sample_paths

        self.summary.update({"samples": len(self.sample_paths)})

        # get Modules
        self.modules = self.module_config.module_names
        self.summary.update({"modules": ",".join(self.modules)})

        print()
        print("SEODeploy: Brought to you by LOCOMOTIVE®")
        print("Loaded...")
        print()

        for active_module in self.module_config.active_modules:

            module_config = Config(module=active_module, cfiles=self.config.cfiles[:1])

            module = self.module_config.active_modules[active_module].SEOTestingModule(
                config=module_config
            )

            print("Running Module: {}".format(module.modulename))
            _LOG.info("Running Module: {}".format(module.modulename))
            messages, errors = module.run(sample_paths=self.sample_paths)

            print("Number of Messages: {}".format(len(messages)))
            _LOG.info("Number of Messages: {}".format(len(messages)))

            passing = len(messages) == 0

            self._update_messages(messages)
            self._update_passing(passing)

            self.summary.update({"{} passing: ".format(module.modulename): passing})
            self.summary.update({"{} errors: ".format(module.modulename): len(errors)})

            if errors:
                _LOG.error("Run Errors:" + json.dumps(errors, indent=2))

            print()

        self.get_messages().to_csv("output.csv", index=False)

        self.print_summary()

        return self.passing

    def _update_messages(self, messages):
        """Update messages property."""
        self.messages.extend(messages)

    def _update_passing(self, passing):
        """Update passing property."""
        self.passing = False if not passing and self.passing else self.passing

    def get_messages(self):
        """Return messages as Pandas DataFrame."""
        return pd.DataFrame(self.messages)

    def print_summary(self):
        """Print summarty to stdout"""
        print("Run CSV saved to:", "output.csv")
        print()
        print("Run Summary")
        print(json.dumps(self.summary, indent=2))
