# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil

from ._anvil_designer import ClassTemplateTemplate
from .MethodTemplate import MethodTemplate
from ....UnitTestTemplate import UnitTestTemplate

__version__ = "0.0.1"


class ClassTemplate(ClassTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.rp_children = anvil.RepeatingPanel(item_template=MethodTemplate)
        self.rp_children.items = self.item["children"]
        
        self.class_tests = UnitTestTemplate(
            cp_role=self.item["card_role"],
            btn_role=self.item['btn_role'],
            btn_text=self.item["name"],
            test_desc=self.item["ref"].__doc__,
            icon_size=self.item["icon_size"],
            btn_run_function=self.btn_run_test_click,
            rp_panels=self.rp_children
        )

        self.add_component(self.class_tests)

    def btn_run_test_click(self, **event_args):
        """This method is called when the button is clicked"""
        testmethods = self.rp_children.get_components()
        for test in testmethods:
            test_fp = test.get_components()[0].get_components()[0].get_components()[0]
            test_btn = test_fp.get_components()[0]
            try:
                test_btn.raise_event("click")
            except Exception:
                print(test_fp.get_components())
                fail_icon = test_fp.get_components()[3]
                fail_icon.visible = True
                self.class_tests.lbl_fail.visible = True
        if not self.class_tests.lbl_fail.visible:
            self.class_tests.lbl_success.visible = True
