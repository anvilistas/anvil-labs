# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil

from ._anvil_designer import MethodTemplateTemplate
from .....UnitTestTemplate import UnitTestTemplate

__version__ = "0.0.1"


class MethodTemplate(MethodTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.success = True
        
        self.test_method = UnitTestTemplate(
            cp_role=self.item["card_role"],
            btn_role=self.item['btn_role'],
            btn_text=self.item["name"],
            test_desc=self.item["ref"].__doc__,
            icon_size=self.item["icon_size"],
            item = self.item,
            btn_run_function=self.btn_run_test_click
        )
        self.add_component(self.test_method)
        self.add_event_handler('x-run', self.run_try_except)

    def btn_run_test_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.Notification("Test " + self.item["name"] + " running..."):
            unitclass = self.item['classref']()
            unitclass.setUp()
            getattr(unitclass, self.item['name'].replace('Method:', '').strip())()
            unitclass.tearDown()
            self.test_method.pass_fail_icon_change(self.success)

    def run_try_except(self, **event_args):
        """Run the tests but without traceback."""
        try:
            self.btn_run_test_click()
            self.test_method.pass_fail_icon_change(self.success)
        except Exception:
            self.success = False
            self.test_method.pass_fail_icon_change(self.success)