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
        
        self.test_method = UnitTestTemplate(
            cp_role=self.item["card_role"],
            btn_role=self.item['btn_role'],
            btn_text=self.item["name"],
            test_desc=self.item["ref"].__doc__,
            icon_size=self.item["icon_size"],
            btn_run_function=self.btn_run_test_click
        )
        self.add_component(self.test_method)

    def btn_run_test_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.test_method.lbl_fail.visible = False
        self.test_method.lbl_success.visible = False
        with anvil.Notification("Test " + self.item["name"] + " running..."):
            self.item["setUp"]()
            self.item["ref"]()
            self.item["tearDown"]()
            print("Test " + self.item["name"] + " was a success!")
            self.test_method.lbl_success.visible = True
